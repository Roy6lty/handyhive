from datetime import timedelta
import pyotp
import time
from fastapi import HTTPException, Request, status
from uuid import UUID

from src.models import token_models
from src.database.handlers import user_handler
from src.models import user_model, email_model, authentication
from passlib.context import CryptContext
from src.root.database import db_dependency
from src.custom_exceptions import error
from src.services.notifications import authorizationcode_email
from src.services import token as token_service
from src.root.env_settings import env
from authlib.integrations.starlette_client import OAuth
from src.models import authentication
from google.auth.transport import requests as google_oauth_request
from google.oauth2 import id_token
from src.models import user_model
from src.root import logger
from src.services import referal_service


oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=env.GOOGLE_CLIENT_ID,
    client_secret=env.GOOGLE_CLIENT_SECRET,
    client_kwargs={"scope": "email openid profile"},
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_2fa_code():
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key, interval=30)
    return totp.now()


async def authenticate_user(db_conn: db_dependency, login: authentication.LoginSchema):
    # get user
    try:
        user = await user_handler.get_user_by_email(db_conn=db_conn, email=login.email)
        verified_password = verify_password(
            plain_password=login.password, hashed_password=user.hashed_password
        )
        return user
    except error.NotFoundError:
        raise HTTPException(status_code=400, detail="incorrect email or password")


async def verify_OTP(db_conn: db_dependency, details: user_model.VerifyOTP):
    user = await user_handler.get_user_by_email(db_conn=db_conn, email=details.email)

    print(user.two_fa_auth_expiry_time, int(time.time()))
    # check otp expiration
    if user.two_fa_auth_expiry_time > int(time.time()):
        if user.two_fa_auth_code == details.otp:
            # process login response
            access_token_data = token_models.AccessTokenEncode(
                id=user.id, is_active=user.is_active, role=user.role
            )

            access_token = token_service.create_access_token(
                access_token_data.model_dump()
            )
            refresh_token = await token_service.create_refresh_token(
                user_id=user.id, db_conn=db_conn
            )

            return authentication.LoginResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                access_token=access_token,
                refresh_token=refresh_token,
                role=user.role,
                account_type=user.account_type,
            )

    return HTTPException(400, detail="incorrect or expired otp")


async def token(
    email: str,
    password: str,
    db_conn: db_dependency,
):
    login_data = authentication.LoginSchema(email=email, password=password)
    user_data = await authenticate_user(db_conn=db_conn, login=login_data)
    token_model: token_models.AccessTokenEncode = (
        token_models.AccessTokenEncode.model_validate(user_data)
    )
    token_data = token_model.model_dump()
    access_token = token_service.create_access_token(
        token_data=token_data,
        expires_delta=timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINS),
    )
    return token_models.AccessTokenResponse(access_token=access_token)


async def resend_2fa_code(email: str, db_conn: db_dependency):
    try:
        user = await user_handler.get_user_by_email(db_conn=db_conn, email=email)
        if user:
            code = generate_2fa_code()

            update_token = user_model.Update2faCode(
                two_fa_auth_code=code, two_fa_auth_expiry_time=int(time.time()) + 300
            )
            updated_user = await user_handler.update_user_by_id(
                db_conn=db_conn, user_id=user.id, values=update_token
            )
            if updated_user:
                email_schema = email_model.EmailSchema(
                    subject="two factor authentication", recipients=[user.email]
                )

                # send email
                await authorizationcode_email.send_email(
                    passcode=code,
                    email=email_schema,
                    template_name=email_model.EmailTemplates.TWO_FACTOR_AUTHENTICATION,
                )

    except error.NotFoundError:
        raise HTTPException(status_code=400, detail="incorrect email or password")


async def login(login: authentication.LoginSchema, db_conn: db_dependency):
    try:
        user = await authenticate_user(db_conn=db_conn, login=login)
        if user:
            await resend_2fa_code(email=login.email, db_conn=db_conn)
        return {"message": "enter verification code"}

    except error.NotFoundError:
        raise HTTPException(status_code=400, detail="incorrect email or password")


async def create_user(
    user_data: authentication.CreateUserSchema,
    db_conn: db_dependency,
):
    # check if user already exists
    try:
        _ = await user_handler.get_user_by_email(email=user_data.email, db_conn=db_conn)
    except error.NotFoundError:
        hashed_password = hash_password(user_data.hashed_password)
        referral_code = referal_service.generate_code()

        user_model = await user_handler.create_user(
            user=user_data,
            db_conn=db_conn,
            hashed_password=hashed_password,
            referral_code=referral_code,
        )
        # send verification mail

        # await handle_email_verification(
        #     user_data=user_model,
        #     db_conn=db_conn,
        #     email_notification_service=email_notification_service,
        #     two_factor_auth_service=two_factor_auth_service,
        # )
        return authentication.CreateUserResponse()

    raise error.UserAlreadyExistsException


async def verify_google_token(token: str) -> authentication.OpenIDUserDataModel:
    """
    Verifies a Google ID token and returns user information.

    Args:
        token (str): The Google ID token to verify.

    Returns:
        OpenIDUserDataModel: A pydantic model containing user information if the token is valid,
                        otherwise None.

    Raises:
        HTTPException: If the token is invalid or verification fails.
    """
    try:
        # Verify the token against Google's servers
        id_info = id_token.verify_token(token, google_oauth_request.Request())

        # Check if the token is valid and intended for our application
        if not id_info:
            raise ValueError("Invalid token.")

        # Extract user information from the token
        user_info = authentication.OpenIDUserDataModel(
            email=id_info.get("email"),
            first_name=id_info.get("given_name"),
            last_name=id_info.get("family_name"),
            profile_pic=id_info.get("picture"),
        )

        return user_info

    except ValueError as e:
        # Handle token verification failures
        raise e


async def process_google_token_login(
    request: Request, token: str, db_conn: db_dependency
):
    """
    Processes OpenID login when the frontend provides the  ID token.
    Verifies the token, retrieves user information, and either logs in or signs up the user.
    """
    try:

        user_info = await verify_google_token(token)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google ID token",
            )

        try:
            db_user = await user_handler.get_user_by_email(
                db_conn=db_conn, email=user_info.email
            )
        except error.NotFoundError:
            # Sign up the user if not already registered
            db_user = await user_handler.create_user(
                db_conn=db_conn, user=user_info, hashed_password=None
            )

        # Log in the user and generate tokens
        access_token, refresh_token = (
            await token_service.generate_access_and_refresh_tokens(
                db_conn=db_conn, user_data=db_user
            )
        )

        return authentication.LoginResponse(  # Added is_active for consistency
            id=db_user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            role=db_user.role,
            account_type=db_user.account_type,
        )

    except Exception as e:
        logger.error_logger.error(f"Error during Google token login: {e}")
        raise HTTPException(status_code=500, detail=f"Google token login failed: {e}")


async def logout(user_id: UUID, db_conn: db_dependency):
    try:
        _ = await user_handler.update_user_by_id(
            db_conn=db_conn,
            values=user_model.UpdateUserProfile(token_jit=None),
            user_id=user_id,
        )

    except error.NotFoundError:
        logger.error_logger.error({"message": "user logout does not exists"})


async def change_password(
    old_password: str,
    new_password,
    user_id: UUID,
    db_conn: db_dependency,
):
    # verify the old password
    try:
        user_data = await user_handler.get_user_by_id(user_id=user_id, db_conn=db_conn)
        if not verify_password(
            plain_password=old_password,
            hashed_password=user_data.hashed_password,
        ):
            raise error.IncorrectPasswordOrUsernameException
        # update password
        hashed_password = hash_password(new_password)
        password_updated = user_model.UpdateUserProfile(hashed_password=hashed_password)
        updated_user = await user_handler.update_user_by_id(
            db_conn=db_conn, user_id=user_id, values=password_updated
        )
        if updated_user:
            return authentication.SuccessfulResponse()
        raise error.UserDoesNotExistException
    except error.NotFoundError as e:
        logger.error_logger.warning(e)
        raise error.UserDoesNotExistException
