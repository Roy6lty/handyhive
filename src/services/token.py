from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Any
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from itsdangerous import URLSafeSerializer

# from src.models.orm_models import UserTableModel
from src.models.orm_models import UserTableModel
from src.models.token_models import (
    AccessTokenEncode,
    RefreshTokenDataEncode,
    RefreshTokenData,
    TokenType,
)
from src.models.user_model import UpdateUserProfile
from src.root.env_settings import env
from datetime import timedelta

# from backend.src.root.logger import logger
from src.root.database import db_dependency
from src.database.handlers import user_handler
from src.custom_exceptions.error import (
    NotFoundError,
    TokenExpirationError,
)
from src.root import logger

oauth2_Scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", scheme_name="users")

ACCESS_TOKEN_EXPIRES = env.ACCESS_TOKEN_EXPIRE_MINS
REFRESH_TOKEN_EXPIRES = env.REFRESH_TOKEN_EXPIRE_MINS
ALGORITHM = env.ALGORITHM
ACCESS_SECRET_KEY = env.ACCESS_SECRET_KEY
REFRESH_SECRET_KEY = env.REFRESH_SECRET_KEY
TOKEN_WRAPPER_KEY = env.TOKEN_WRAPPER_KEY
TOKEN_WRAPPER_SALT = env.TOKEN_WRAPPER_SALT


def __create_token(token_data: dict, expires_delta: timedelta, key: str) -> str:
    to_encode = token_data
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key, ALGORITHM)
    serializer = URLSafeSerializer(
        secret_key=TOKEN_WRAPPER_KEY, salt=TOKEN_WRAPPER_SALT
    )
    token = serializer.dumps(encoded_jwt)

    return token  # type: ignore


def __decode_token(
    token: str, algorithm: str, key: str, token_type: TokenType
) -> dict[str, Any]:
    serializer = URLSafeSerializer(
        secret_key=TOKEN_WRAPPER_KEY, salt=TOKEN_WRAPPER_SALT
    )
    try:
        token = serializer.loads(token)

        payload = jwt.decode(
            token,
            key,
            algorithms=[algorithm],
        )

        if payload == {}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalids Token"
            )
        return payload  # type: ignore

    except ExpiredSignatureError as jwt_exec:
        logger.error_logger.warning(jwt_exec)
        raise TokenExpirationError(token_type=token_type.value)

    except JWTError as jwt_exec:
        logger.error_logger.warning(jwt_exec)
        raise ExpiredSignatureError


def create_access_token(
    token_data: dict, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES)
) -> str:
    data = __create_token(token_data, expires_delta, ACCESS_SECRET_KEY)
    return data


def decode_access_token(
    token: str, algorithm=ALGORITHM, key=ACCESS_SECRET_KEY
) -> dict[str, Any]:
    data = __decode_token(
        token=token,
        algorithm=algorithm,
        key=key,
        token_type=TokenType.access_token,
    )

    return data


def verify_access_token(token: str):
    """_summary_

    Args:
        token (str): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        payload = decode_access_token(token)
        return payload

    except TokenExpirationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def create_refresh_token(
    user_id: UUID,
    db_conn: db_dependency,
    expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRES),
) -> str:
    # verify Refresh token
    updated_model = UpdateUserProfile(token_jit=uuid4())
    try:
        user_data = await user_handler.update_user_by_id(
            user_id=user_id, values=updated_model, db_conn=db_conn
        )
        token_model = RefreshTokenDataEncode.model_validate(user_data)
        return __create_token(
            token_data=token_model.model_dump(),
            expires_delta=expires_delta,
            key=REFRESH_SECRET_KEY,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e


async def decode_refresh_token(token: str, algorithm=ALGORITHM) -> RefreshTokenData:
    try:
        token_data: dict[str, Any] = __decode_token(
            token, algorithm, REFRESH_SECRET_KEY, TokenType.refresh_token
        )
    except TokenExpirationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return RefreshTokenData.model_validate(token_data)


async def verify_refresh_token(db_conn: db_dependency, token: str) -> RefreshTokenData:
    user_data = await decode_refresh_token(token=token)
    token_model = RefreshTokenData.model_validate(user_data)
    try:
        user_data = await user_handler.get_user_by_id(
            user_id=token_model.id, db_conn=db_conn
        )
        if user_data.token_jit != token_model.token_jit:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_model

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


async def generate_access_and_refresh_tokens(
    db_conn: db_dependency, user_data: UserTableModel
) -> tuple[str, str]:
    token_model = AccessTokenEncode.model_validate(user_data)
    token_data = token_model.model_dump()
    access_token = create_access_token(
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES),
        token_data=token_data,
    )
    refresh_token = await create_refresh_token(
        user_id=user_data.id,
        db_conn=db_conn,
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRES),
    )

    return access_token, refresh_token
