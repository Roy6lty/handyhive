from src.root.database import db_dependency
from src.models import user_model
from src.database.handlers import user_handler
from src.custom_exceptions import error
from fastapi import HTTPException
from src.services import cloudinary_service
from uuid import UUID


async def get_user_profile(db_conn: db_dependency, user_id: UUID):
    try:
        user = await user_handler.get_user_by_id(db_conn=db_conn, user_id=user_id)
        return user_model.UserProfileResponse.model_validate(user)
    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")


async def update_profle_picture(
    db_conn: db_dependency, user_id: UUID, profile_pic: str | None
):

    # upload image
    uploaded_profile = await cloudinary_service.upload_single_file(profile_pic)

    try:
        updated_user = await user_handler.update_user_by_id(
            db_conn=db_conn,
            user_id=user_id,
            values=user_model.UpdateUser(profile_pic=uploaded_profile),
        )
        return user_model.UserProfileResponse.model_validate(updated_user)
    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")


async def update_user_profile(
    db_conn: db_dependency, user_id: UUID, profile: user_model.UpdateUserProfile
):
    try:
        updated_user = await user_handler.update_user_by_id(
            db_conn=db_conn, user_id=user_id, values=profile
        )
        return user_model.UserProfileResponse.model_validate(updated_user)
    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")


async def update_notifications(
    db_conn: db_dependency, user_id: UUID, notifications: user_model.NotificationSchema
):
    values = user_model.UpdateUserProfile(
        push_notifications=notifications.push_notifications,
        promotional_notifications=notifications.promotional_notifications,
    )
    try:
        _ = await user_handler.update_user_by_id(
            db_conn=db_conn, user_id=user_id, values=values
        )
    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")


async def delete_user_profile(db_conn: db_dependency, user_id: UUID):
    try:
        await user_handler.delete_user_by_id(db_conn=db_conn, user_id=user_id)
        return {"detail": "user deleted successfully"}
    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")
