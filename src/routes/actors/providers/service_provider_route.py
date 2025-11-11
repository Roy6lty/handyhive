from uuid import UUID
import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import UUID4
from src.models import bookings_model
from src.services import booking_service
from src.models import service_provider_model
from src.models.token_models import AccessTokenData
from src.services import service_provider
from src.root.database import db_dependency
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


@router.get(
    "/bookings",
    description="Get bookings by  service provider id",
)
async def get_bookings_by_service_provider(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return booking_service.get_all_bookings_service_provider(
        db_conn=db_conn, service_provider_id=token_info.id
    )


@router.get(
    "/profile",
    description="Get Business Information",
)
async def get_service_provider_profile(
    db_conn: db_dependency,
    user_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.get_business_profile(
        db_conn=db_conn, user_id=user_info.id
    )


@router.patch("/booking/{booking_id}/update", description="Accept Booking")
async def accept_booking(
    db_conn: db_dependency,
    booking_id: UUID,
    status: bookings_model.UpdateBookingStatus,
    user_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.update_booking_status(
        db_conn=db_conn,
        booking_id=booking_id,
        service_provider_id=user_info.id,
        values=status,
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


@router.patch(
    "/verify/{service_provider_id}",
    description="Update Verification Status",
)
async def update_verfied_status(
    db_conn: db_dependency,
    service_provider_id: UUID,
    status: service_provider_model.UpdateVerifiedStatus,
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await service_provider.update_verfied_status(
        db_conn=db_conn,
        service_provider_id=service_provider_id,
        verified=status.verified,
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
    "/catalogue-picture/{service_id}",
    description="upload catatlogue images",
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


##############################################
@router.patch("/bookings/{id}", description="Update Bookings status0")
async def update_bookings(
    db_conn: db_dependency, id: uuid.UUID, bookings: bookings_model.UpdateBookingStatus
):
    return await booking_service.update_bookings(
        db_conn=db_conn, booking_id=id, booking=bookings
    )


@router.get("/available-time/{provider_id}")
async def get_provider_available_time(db_conn: db_dependency):
    return ["8:00am", "9:00am"]
