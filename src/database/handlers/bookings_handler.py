import uuid
from uuid import UUID
from src.root.database import db_dependency
from src.models import bookings_model
from src.database.orms import user_orm
from sqlalchemy import select, update, delete
from src.custom_exceptions import error
from src.models import orm_models


async def create_booking(
    db_conn: db_dependency,
    booking: bookings_model.CreateBookingModel,
    user_id: uuid.UUID,
):
    new_bookings = user_orm.BookingsTable(
        id=uuid.uuid4(), customer_id=user_id, **booking.model_dump()
    )
    db_conn.add(new_bookings)
    await db_conn.commit()
    await db_conn.refresh(new_bookings)

    return orm_models.BookingsTableModel.model_validate(new_bookings)


async def get_booking_by_id(db_conn: db_dependency, booking_id: UUID):
    booking = select(user_orm.BookingsTable).where(
        user_orm.BookingsTable.id == booking_id
    )
    result = await db_conn.execute(booking)
    found_service = result.scalar_one_or_none()
    if found_service:
        return orm_models.BookingsTableModel.model_validate(found_service)

    else:
        raise error.NotFoundError


async def get_all_bookings_service_provider(
    db_conn: db_dependency, service_provider_id: UUID
):
    query = select(user_orm.BookingsTable).where(
        user_orm.BookingsTable.service_provider_id == service_provider_id
    )
    result = await db_conn.execute(query)
    found_services = result.scalars().all()
    if found_services:
        return [
            orm_models.BookingsTableModel.model_validate(service)
            for service in found_services
        ]
    else:
        return []


async def get_all_bookings_customer(db_conn: db_dependency, customer_id: UUID):
    query = select(user_orm.BookingsTable).where(
        user_orm.BookingsTable.customer_id == customer_id
    )
    result = await db_conn.execute(query)
    found_services = result.scalars().all()
    if found_services:
        return [
            orm_models.BookingsTableModel.model_validate(service)
            for service in found_services
        ]
    else:
        return []


async def update_booking_by_id(
    db_conn: db_dependency, booking_id: UUID, values: bookings_model.UpdateBookingModel
):
    query = (
        update(user_orm.BookingsTable)
        .where(user_orm.BookingsTable.id == booking_id)
        .values(**values.model_dump(exclude_unset=True))
        .returning(user_orm.BookingsTable)
    )
    result = await db_conn.execute(query)
    updated_service = result.scalar_one_or_none()
    if updated_service:
        return orm_models.BookingsTableModel.model_validate(updated_service)
    else:
        raise error.NotFoundError


async def delete_bookings_by_id(db_conn: db_dependency, service_id: UUID):
    query = (
        delete(user_orm.ServiceProviderTable)
        .where(user_orm.ServiceProviderTable.id == service_id)
        .returning(user_orm.ServiceProviderTable)
    )
    result = await db_conn.execute(query)
    deleted_service = result.scalar_one_or_none()
    if deleted_service:
        await db_conn.commit()
        return None
    else:
        raise error.NotFoundError
