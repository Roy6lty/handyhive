from fastapi import APIRouter, Depends
from src.models.token_models import AccessTokenData
from src.services import booking_service
from src.services.authorization_service import get_user_verification_service
from src.root.database import db_dependency
from src.models import bookings_model
import uuid

router = APIRouter(tags=["Bookings"], prefix="/api/v1/customers")


@router.post("/bookings", description="Create a new booking")
async def create_bookings(
    db_conn: db_dependency,
    booking: bookings_model.CreateBookingModel,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await booking_service.create_bookings(
        db_conn=db_conn, booking=booking, user_id=token_info.id
    )


@router.get(
    "/bookings",
    description="Get bookings by id",
)
async def get_bookings_by_service_provider(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return booking_service.get_all_bookings_service_provider(
        db_conn=db_conn, service_provider_id=token_info.id
    )


@router.get(
    "/bookings",
    description="Get bookings by id",
)
async def get_bookings_by_customer_provider(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return booking_service.get_all_bookings_service_provider(
        db_conn=db_conn, service_provider_id=token_info.id
    )


@router.get(
    "/bookings/{id}",
    description="Get bookings by id",
)
async def get_bookings_by_id(db_conn: db_dependency, id: uuid.UUID):
    return booking_service.get_booking_by_id(db_conn=db_conn, booking_id=id)
