import uuid
from fastapi import HTTPException


from src.root.database import db_dependency
from src.database.handlers import bookings_handler, invoice_handler
from src.models import bookings_model, invoice_models
from src.custom_exceptions import error


async def get_booking_by_id(booking_id: uuid.UUID, db_conn: db_dependency):
    return await bookings_handler.get_booking_by_id(
        booking_id=booking_id, db_conn=db_conn
    )


async def create_bookings(
    db_conn: db_dependency,
    booking: bookings_model.CreateBookingModel,
    user_id: uuid.UUID,
):
    booking = await bookings_handler.create_booking(
        db_conn=db_conn, booking=booking, user_id=user_id
    )
    return bookings_model.BookingResponse.model_validate(booking)


async def update_bookings(
    db_conn: db_dependency,
    booking: bookings_model.UpdateBookingModel | bookings_model.UpdateBookingStatus,
    booking_id: uuid.UUID,
):
    # check if the booking has been accepted
    try:
        invoice = await invoice_handler.get_invoice_by_booking_id(
            db_conn=db_conn, booking_id=booking_id
        )
        if invoice.status != invoice_models.Status.PENDING:
            raise HTTPException(status_code=400, detail="invoice already accepted")
    except error.NotFoundError as err:
        pass
    return await bookings_handler.update_booking_by_id(
        db_conn=db_conn, values=booking, booking_id=booking_id
    )


async def get_all_bookings_service_provider(
    db_conn: db_dependency, service_provider_id: uuid.UUID
):
    return await bookings_handler.get_all_bookings_service_provider(
        db_conn=db_conn, service_provider_id=service_provider_id
    )


async def get_all_bookings_customer(db_conn: db_dependency, customer_id: uuid.UUID):
    return await bookings_handler.get_all_bookings_customer(
        db_conn=db_conn, customer_id=customer_id
    )
