from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from src.root.database import db_dependency
from src.services import authorization_service, authentication as authentication_service
from src.root.env_settings import env
from src.models import token_models
from src.models import authentication as authentication_model, user_model

PREFIX = "/api/v1/auth"
router = APIRouter(tags=["Authentication"], prefix=PREFIX)

# FRONTEND_WEB_CALLBACK_SUCCESS_URL = env.GOOGLE_OAUTH_REDIRECT_URI_WEB
MOBILE_APP_CUSTOM_SCHEME_CALLBACK = env.GOOGLE_OAUTH_REDIRECT_URI_MOBILE

oauth = authentication_service.oauth


class GoogleAuthCodeSchema(BaseModel):
    code: str
    redirect_uri: str


@router.post(
    "/refresh",
    response_model=token_models.RefreshTokenResponse,
    responses={
        400: {"description": "invalid-token"},
        401: {"description": "expired-token"},
    },
)
async def refresh_token(
    db_conn: db_dependency,
    refresh_token: str = Header(),
):
    return await authorization_service.verify_and_update_refresh_token(
        refresh_token=refresh_token, db_conn=db_conn, token_service=token_service
    )


@router.post("/token")
async def token(
    db_conn: db_dependency,
    form_data=Depends(OAuth2PasswordRequestForm),
):

    return await authentication_service.token(
        db_conn=db_conn,
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/google-oauth/token", summary="Google OAuth Login with Token")
async def google_oauth_token(
    request: Request,
    token: str,
    db_conn: db_dependency,
):
    """
    Handles Google OAuth login when the frontend provides the Google ID token.
    This bypasses the standard OAuth flow and directly authenticates with the token.
    """
    return await authentication_service.process_google_token_login(
        request=request,
        token=token,
        db_conn=db_conn,
    )


@router.post(
    "/signup",
    summary="Login",
    status_code=status.HTTP_201_CREATED,
    response_model=authentication_model.CreateUserResponse,
)
async def signup(
    user_data: authentication_model.CreateUserSchema,
    db_conn: db_dependency,
) -> authentication_model.CreateUserResponse:
    return await authentication_service.create_user(
        db_conn=db_conn,
        user_data=user_data,
    )


@router.post(
    "/login",
    response_model=authentication_model.LoginResponse
    | authentication_model.TwoFAResponse,
    summary="Login",
    status_code=status.HTTP_200_OK,
)
async def login(
    user_data: authentication_model.LoginSchema,
    db_conn: db_dependency,
):
    return await authentication_service.login(
        db_conn=db_conn,
        login=user_data,
    )


@router.post(
    "/logout",
    summary="logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    db_conn: db_dependency,
    user_info: token_models.AccessTokenData = Depends(
        authorization_service.get_user_verification_service
    ),
):
    return await authentication_service.logout(
        user_id=user_info.id,
        db_conn=db_conn,
    )


@router.post(
    "/verify/2fa",
    summary="two factor verification",
    # response_model=authentication_model.LoginResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def verify_2fa(
    db_conn: db_dependency,
    verification: user_model.VerifyOTP,
):
    """
    Verifies the 2FA code and, if successful, returns login tokens.
    """
    return await authentication_service.verify_OTP(
        details=verification,
        db_conn=db_conn,
    )


@router.get(
    "/verify/email",
    summary="email verification code",
    response_model=authentication_model.SuccessfulResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_verification_email(
    db_conn: db_dependency,
    email: EmailStr,
):
    return await authentication_service.resend_2fa_code(
        db_conn=db_conn,
        email=email,
    )


# @router.post(
#     "/verify/email",
#     summary="email verification",
#     response_model=SuccessfulResponse,
#     status_code=status.HTTP_202_ACCEPTED,
# )
# async def verify_email(
#     db_conn: db_dependency,
#     verification: VerificationCodeSchema,
#     two_factor_auth_service: TwoFactorAuthenticationService = Depends(
#         get_two_factor_auth_service
#     ),
# ):
#     return await authentication_service.verify_email_code(
#         db_conn=db_conn,
#         email=verification.email,
#         verification_code=verification.verification_code,
#         two_factor_authentication=two_factor_auth_service,
#     )


# @router.post("/password/reset", status_code=status.HTTP_202_ACCEPTED)
# async def reset_password(
#     db_conn: db_dependency,
#     email: str,
#     email_service=Depends(get_email_notification_service),
#     password_reset_service=Depends(get_password_service),
#     two_factor_auth_service=Depends(get_two_factor_auth_service),
# ):
#     return await authentication_service.reset_password(
#         email=email,
#         db_conn=db_conn,
#         email_service=email_service,
#         password_service=password_reset_service,
#         two_factor_auth_service=two_factor_auth_service,
#     )


# @router.post(
#     "/verify/passwordcode",
#     summary="password reset verification",
#     response_model=authentication_model.SuccessfulResponse,
#     status_code=status.HTTP_202_ACCEPTED,
# )
# async def verify_reset_password_code(
#     db_conn: db_dependency,
#     verification: VerificationNewPassword,
#     password_service=Depends(get_password_service),
#     two_factor_auth_service: TwoFactorAuthenticationService = Depends(
#         get_two_factor_auth_service
#     ),
# ):

#     return await authentication_service.verify_reset_password(
#         email=verification.email,
#         verification_code=verification.verification_code,
#         db_conn=db_conn,
#         password=verification.confirm_password,
#         two_factor_authentication=two_factor_auth_service,
#         password_reset=password_service,
#     )


@router.post(
    "/password/change",
    summary="Update existing password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    db_conn: db_dependency,
    password: authentication_model.PasswordChangeSchema,
    user_info: token_models.AccessTokenData = Depends(
        authorization_service.get_user_verification_service
    ),
):
    return await authentication_service.change_password(
        old_password=password.old_password,
        new_password=password.new_password,
        db_conn=db_conn,
        user_id=user_info.id,
    )
