import uuid
from src.root.database import db_dependency
from src.database.handlers import invoice_handler
from src.models import invoice_models
from fastapi import HTTPException


async def get_invoice_by_customer_id(
    invoice_id: uuid.UUID, db_conn: db_dependency, customer_id: uuid.UUID
):
    return await invoice_handler.get_invoice_by_customer_id(
        invoice_id=invoice_id, db_conn=db_conn, customer_id=customer_id
    )


async def get_invoice_by_provider_id(
    invoice_id: uuid.UUID, db_conn: db_dependency, provider_id: uuid.UUID
):
    return await invoice_handler.get_invoice_by_provider_id(
        invoice_id=invoice_id, db_conn=db_conn, provider_id=provider_id
    )


async def create_invoice(
    db_conn: db_dependency,
    user_id: uuid.UUID,
    invoice: invoice_models.CreateInvoiceModel,
):
    return await invoice_handler.create_invoice(
        db_conn=db_conn, invoice=invoice, user_id=user_id
    )


async def update_invoice(
    db_conn: db_dependency,
    invoice: invoice_models.UpdateInvoiceModel,
    invoice_id: uuid.UUID,
):
    ## Check if the status is on ACCEPTED or REJECTED

    invoice_found = await invoice_handler.get_invoice_by_id(
        db_conn=db_conn, invoice_id=invoice_id
    )
    if invoice_found.status != invoice_models.Status.PENDING:
        raise HTTPException(status_code=400, detail="Cannot update accepted invoice")
    return await invoice_handler.update_invoice_by_id(
        db_conn=db_conn, invoice_id=invoice_id, values=invoice
    )


async def get_all_invoices_service_provider(
    db_conn: db_dependency, service_provider_id: uuid.UUID
):
    return await invoice_handler.get_all_invoices_service_provider(
        db_conn=db_conn, service_provider_id=service_provider_id
    )


async def get_all_invoices_customer(db_conn: db_dependency, customer_id: uuid.UUID):
    return await invoice_handler.get_all_invoices_by_customer_id(
        db_conn=db_conn, customer_id=customer_id
    )
