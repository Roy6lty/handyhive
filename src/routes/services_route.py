from fastapi import APIRouter, Depends
from src.models.token_models import AccessTokenData
from src.services import service_management_service
from src.root.database import db_dependency
from src.models import user_model, services_model
from src.services.authorization_service import get_user_verification_service
import json

router = APIRouter(tags=["Services"], prefix="/api/v1/services")


@router.get(
    "/",
    description="Get all available services",
)
async def get_all_services(
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return service_management_service.get_all_services()
