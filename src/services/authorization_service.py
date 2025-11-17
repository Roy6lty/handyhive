from typing import Annotated, Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.services.token import verify_access_token
from src.models import token_models
from fastapi import WebSocket, Query, Header, HTTPException, WebSocketException, status

oauth2_Scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", scheme_name="users")

# def check_roles_service(token_data:Depends(get_user_verification_service)):
#     if token_data.


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


def get_business_verification_service(
    token: Annotated[str, Depends(get_user_verification_service)],
) -> token_models.ProviderAccessTokenData:
    """
    Dependency to get the current business user's data from the access token.
    Raises HTTPException if the token is invalid or expired.
    """
    token_data = token_models.ProviderAccessTokenData.model_validate(token)
    if token_data.service_provider_id:
        return token_data
    raise HTTPException(status_code=403, detail="User is not a service provider")


async def get_user_verification_service_ws(
    websocket: WebSocket,
    query_param_token: Optional[str] = Query(None, alias="token"),
    authorization_header: Optional[str] = Header(None, alias="Authorization"),
) -> token_models.AccessTokenData:
    """
    Dependency to get the current user's data for WebSocket connections.
    Extracts token from query parameter or Authorization header.
    Raises WebSocketException if the token is invalid, missing, or expired.
    """
    token_str: Optional[str] = None
    print("token_str")

    if query_param_token:
        token_str = query_param_token
    elif authorization_header:
        parts = authorization_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token_str = parts[1]
        else:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Malformed Authorization header",
            )

    if not token_str:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication token not found in query parameter or Authorization header",
        )

    try:
        payload = verify_access_token(token_str)
        print(payload)

        token_data = token_models.AccessTokenData.model_validate(payload)
        return token_data
    except HTTPException as e:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"access-token invalid or expired: {str(e)}",
        )
    except Exception as e:  # Catch-all for other unexpected errors
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Token verification failed"
        )
