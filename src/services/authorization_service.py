from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.services.token import verify_access_token
from src.models import token_models

oauth2_Scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", scheme_name="users")


def get_user_verification_service(
    token: Annotated[str, Depends(oauth2_Scheme)],
) -> token_models.AccessTokenData:
    """
    Dependency to get the current user's data from the access token.
    Raises HTTPException if the token is invalid or expired.
    """
    payload = verify_access_token(token)
    token_data = token_models.AccessTokenData.model_validate(payload)
    return token_data
