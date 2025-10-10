import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import UUID4
from src.models import service_provider_model
from src.models.token_models import AccessTokenData
from src.services import service_provider
from src.root.database import db_dependency
from src.models import user_model, invoice_models
from src.services import invoice_service
from src.services.authorization_service import get_user_verification_service
from src.root.database import db_dependency

router = APIRouter(tags=["providers"], prefix="/api/v1/providers")


@router.post(
    "/",
    description="Get single Service Provider",
)
async def create_service_provider(
    db_conn: db_dependency,
    service: service_provider_model.CreateService,
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.create_service_provider(
        db_conn=db_conn, values=service
    )


@router.get(
    "/{id}",
    description="Get single Service Provider",
)
async def get_service_provider(
    db_conn: db_dependency,
    id: UUID4,
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.get_service_provider_by_id(
        db_conn=db_conn, service_provider_id=id
    )


@router.post(
    "/search",
    description="Get single Service Provider",
)
async def search_service_provider(
    db_conn: db_dependency,
    search_info: service_provider_model.SearchServices,
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.search_service_providers_by_location_and_category(
        db_conn=db_conn, search_query=search_info
    )


@router.patch(
    "/{id}",
    description="Update Business Information",
)
async def update_service(
    id: UUID4,
    db_conn: db_dependency,
    update_profile: service_provider_model.UpdateServices,
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.update_service_provider_by_id(
        db_conn=db_conn, service_provider_id=id, values=update_profile
    )


# Once payment is made a booking cannot be updates
# once a booking is accepted it cannot be updated

#####################################################
## Invoices
######################################################


@router.patch(
    "/picture/{service_id}",
    description="upload catatlogue images",
    response_model=user_model.UserProfileResponse,
)
async def update_user_profile_picture(
    db_conn: db_dependency,
    service_id: UUID,
    catalogue_pic: list[UploadFile] = File(...),
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.update_catalogue_picture(
        db_conn=db_conn, service_id=service_id, catalogue_pic=catalogue_pic
    )
