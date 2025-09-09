from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, status
from src.models.token_models import AccessTokenData
from src.services import profile_service
from src.root.database import db_dependency
from src.models import user_model
from src.services.authorization_service import get_user_verification_service

router = APIRouter(tags=["Profile"], prefix="/api/v1/profile")


@router.get(
    "",
    description="Get User Profile Data",
    response_model=user_model.UserProfileResponse,
)
async def get_profile(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await profile_service.get_user_profile(
        db_conn=db_conn, user_id=token_info.id
    )


@router.patch(
    "",
    description="Update User Profile",
    response_model=user_model.UserProfileResponse,
)
async def update_user_profile(
    db_conn: db_dependency,
    update_profile: user_model.UpdateUserProfile,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await profile_service.update_user_profile(
        db_conn=db_conn, user_id=token_info.id, profile=update_profile
    )


@router.patch(
    "/picture",
    description="Update User Profile",
    response_model=user_model.UserProfileResponse,
)
async def update_user_profile_picture(
    db_conn: db_dependency,
    profile_pic: UploadFile,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await profile_service.update_profle_picture(
        db_conn=db_conn, user_id=token_info.id, profile_pic=profile_pic
    )


@router.delete(
    "",
    description="Delete User Account",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_user_account(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await profile_service.delete_user_profile(
        db_conn=db_conn, user_id=token_info.id
    )
