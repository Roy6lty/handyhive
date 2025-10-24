import uuid
from uuid import UUID
from src.root.database import db_dependency
from src.models import invoice_models
from src.database.orms import user_orm
from sqlalchemy import select, update, delete
from src.custom_exceptions import error
from src.models import orm_models


async def create_invoice(
    db_conn: db_dependency,
    invoice: invoice_models.CreateInvoiceModel,
    user_id: uuid.UUID,
) -> orm_models.InvoiceTableModel:
    new_invoice = user_orm.InvoiceTable(
        id=uuid.uuid4(),
        service_provider_id=user_id,
        status=invoice_models.Status.PENDING,
        **invoice.model_dump()
    )
    db_conn.add(new_invoice)
    await db_conn.commit()
    await db_conn.refresh(new_invoice)

    return orm_models.InvoiceTableModel.model_validate(new_invoice)


async def get_invoice_by_provider_id(
    db_conn: db_dependency, invoice_id: UUID, provider_id: uuid.UUID
):
    invoice = select(user_orm.BookingsTable).where(
        user_orm.InvoiceTable.id == invoice_id
        and user_orm.InvoiceTable.service_provider_id == provider_id
    )
    result = await db_conn.execute(invoice)
    found_service = result.scalar_one_or_none()
    if found_service:
        return orm_models.InvoiceTableModel.model_validate(found_service)

    else:
        raise error.NotFoundError


async def get_invoice_by_id(invoice_id: uuid.UUID, db_conn: db_dependency):
    booking = select(user_orm.InvoiceTable).where(
        user_orm.InvoiceTable.id == invoice_id
    )
    result = await db_conn.execute(booking)
    found_service = result.scalar_one_or_none()
    if found_service:
        return orm_models.InvoiceTableModel.model_validate(found_service)

    else:
        raise error.NotFoundError


async def get_invoice_by_customer_id(
    db_conn: db_dependency, invoice_id: UUID, customer_id: uuid.UUID
):
    booking = select(user_orm.BookingsTable).where(
        user_orm.InvoiceTable.id == invoice_id
        and user_orm.InvoiceTable.customer_id == customer_id
    )
    result = await db_conn.execute(booking)
    found_service = result.scalar_one_or_none()
    if found_service:
        return orm_models.InvoiceTableModel.model_validate(found_service)

    else:
        raise error.NotFoundError


async def get_all_invoices_service_provider(
    db_conn: db_dependency, service_provider_id: UUID
):
    query = select(user_orm.InvoiceTable).where(
        user_orm.InvoiceTable.service_provider_id == service_provider_id
    )
    result = await db_conn.execute(query)
    found_services = result.scalars().all()
    if found_services:
        return [
            orm_models.InvoiceTableModel.model_validate(service)
            for service in found_services
        ]
    else:
        return []


async def get_all_invoices_by_customer_id(db_conn: db_dependency, customer_id: UUID):
    query = select(user_orm.InvoiceTable).where(
        user_orm.InvoiceTable.customer_id == customer_id
    )
    result = await db_conn.execute(query)
    found_services = result.scalars().all()
    if found_services:
        return [
            orm_models.InvoiceTableModel.model_validate(service)
            for service in found_services
        ]
    else:
        return []


async def get_invoice_by_booking_id(db_conn: db_dependency, booking_id: UUID):
    invoice = select(user_orm.InvoiceTable).where(
        user_orm.InvoiceTable.booking_id == booking_id
    )
    result = await db_conn.execute(invoice)
    found_service = result.scalar_one_or_none()
    if found_service:
        return orm_models.InvoiceTableModel.model_validate(found_service)

    else:
        raise error.NotFoundError


async def update_invoice_by_id(
    db_conn: db_dependency, invoice_id: UUID, values: invoice_models.UpdateInvoiceModel
):
    query = (
        update(user_orm.InvoiceTable)
        .where(user_orm.InvoiceTable.id == invoice_id)
        .values(**values.model_dump(exclude_unset=True))
        .returning(user_orm.InvoiceTable)
    )
    result = await db_conn.execute(query)
    updated_service = result.scalar_one_or_none()
    if updated_service:
        return orm_models.InvoiceTableModel.model_validate(updated_service)
    else:
        raise error.NotFoundError


async def delete_bookings_by_id(db_conn: db_dependency, service_id: UUID):
    query = (
        delete(user_orm.InvoiceTable)
        .where(user_orm.InvoiceTable.id == service_id)
        .returning(user_orm.InvoiceTable)
    )
    result = await db_conn.execute(query)
    deleted_service = result.scalar_one_or_none()
    if deleted_service:
        await db_conn.commit()
        return None
    else:
        raise error.NotFoundError
