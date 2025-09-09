import asyncio
from fastapi import HTTPException, UploadFile
import cloudinary
import cloudinary.uploader
import cloudinary.api
from src.root.env_settings import env
from pydantic import UUID4
from src.root.database import db_dependency

cloudinary_config = cloudinary.config(
    cloud_name=env.CLOUDINARY_CLOUD_NAME,
    api_key=env.CLOUDINARY_API_KEY,
    api_secret=env.CLOUDINARY_API_SECRET,
)


def check_file_extension(file: UploadFile):
    allowed_extensions = ["jpeg", "jpg", "png"]
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")

    filename: str = file.filename
    file_ext = filename.split(".")[-1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File Extension not support image must be 'png', 'jpg' or 'jpeg'",
        )


async def upload_single_file(file: UploadFile) -> str:
    try:
        result = cloudinary.uploader.upload(file.file)
        return result["secure_url"]
    except Exception as e:
        print(f"Error Uploading file {e}")
        raise e


async def upload_profile_pic(
    *,
    db_conn: db_dependency,
    profile_pic: UploadFile | None,
    user_id: UUID4,
):
    pass
