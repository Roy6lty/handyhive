import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import UUID4
from src.models.responses import SuccessfulResponse
from src.models import bookings_model
from src.services import booking_service
from src.models import service_provider_model
from src.models.token_models import ProviderAccessTokenData
from src.services import service_provider
from src.root.database import db_dependency
from src.services.authorization_service import (
    get_business_verification_service,
)
from src.root.database import db_dependency

router = APIRouter(tags=["providers"], prefix="/api/v1/providers")


@router.post(
    "/",
    description="Get single Service Provider",
)
async def create_service_provider(
    db_conn: db_dependency,
    service: service_provider_model.CreateService,
    _: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.create_service_provider(
        db_conn=db_conn, values=service
    )


@router.post(
    "/search",
    description="Get single Service Provider",
)
async def search_service_provider(
    db_conn: db_dependency,
    search_info: service_provider_model.SearchServices,
    _: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.search_service_providers_by_location_and_category(
        db_conn=db_conn, search_query=search_info
    )


@router.get(
    "/bookings",
    description="Get bookings by  service provider id",
)
async def get_bookings_by_service_provider(
    db_conn: db_dependency,
    token_info: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await booking_service.get_all_bookings_service_provider(
        db_conn=db_conn, service_provider_id=token_info.service_provider_id
    )


@router.get(
    "/profile",
    description="Get Business Information",
)
async def get_service_provider_profile(
    db_conn: db_dependency,
    user_info: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.get_business_profile(
        db_conn=db_conn, user_id=user_info.id
    )


@router.get(
    "/{id}",
    description="Get single Service Provider",
)
async def get_service_provider(
    db_conn: db_dependency,
    id: UUID4,
    _: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.get_service_provider_by_id(
        db_conn=db_conn, service_provider_id=id
    )


@router.patch(
    "/verify",
    description="Update Verification Status",
)
async def update_verified_status(
    db_conn: db_dependency,
    status: service_provider_model.UpdateVerifiedStatus,
    user_info: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.update_verified_status(
        db_conn=db_conn,
        service_provider_id=user_info.service_provider_id,
        verified=status.verified,
    )


@router.patch("/online-status", description="Update Provider Online Status")
async def update_online_status(
    db_conn: db_dependency,
    status: service_provider_model.UpdateOnlineStatus,
    user_info: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.update_online_status(
        db_conn=db_conn,
        service_provider_id=user_info.service_provider_id,
        values=status,
    )


@router.patch(
    "/",
    description="Update Business Information",
    status_code=200,
    response_model=SuccessfulResponse,
)
async def update_service(
    db_conn: db_dependency,
    update_profile: service_provider_model.UpdateServices,
    user_info: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    _ = await service_provider.update_service_provider_by_id(
        db_conn=db_conn,
        service_provider_id=user_info.service_provider_id,
        values=update_profile,
    )
    return SuccessfulResponse


# Once payment is made a booking cannot be updates
# once a booking is accepted it cannot be updated


@router.patch(
    "/catalogue-picture",
    description="upload catatlogue images",
)
async def upload_picture(
    catalogue_pic: list[UploadFile] = File(...),
    user_info: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await service_provider.upload_pictures(
        catalogue=catalogue_pic,
    )


#####################################################
## Invoices
######################################################


##############################################
@router.patch(
    "/bookings/{id}", description="Update Bookings status by passing the booking ID"
)
async def update_bookings(
    db_conn: db_dependency,
    id: uuid.UUID,
    bookings: bookings_model.UpdateBookingStatus,
    _: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return await booking_service.update_bookings(
        db_conn=db_conn, booking_id=id, booking=bookings
    )


@router.get("/available-time/{provider_id}")
async def get_provider_available_time(
    db_conn: db_dependency,
    _: ProviderAccessTokenData = Depends(get_business_verification_service),
):
    return ["8:00am", "9:00am"]
