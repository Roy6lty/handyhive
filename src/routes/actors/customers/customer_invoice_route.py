import uuid
from fastapi import APIRouter, Depends
from src.models.token_models import AccessTokenData
from src.services import invoice_service
from src.services.authorization_service import get_user_verification_service
from src.root.database import db_dependency
from src.models import invoice_models

router = APIRouter(tags=["Invoice"], prefix="/api/v1/invoice")


@router.post("/provider", description="Create Invoice")
async def create_invoice(
    db_conn: db_dependency,
    invoice: invoice_models.CreateInvoiceModel,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await invoice_service.create_invoice(
        db_conn=db_conn, invoice=invoice, user_id=token_info.id
    )


@router.patch(
    "/provider",
    description="Update invoice Info",
)
async def update_invoice(
    db_conn: db_dependency,
    invoice: invoice_models.UpdateInvoiceModel,
    invoice_id: uuid.UUID,
):
    return await invoice_service.update_invoice(
        db_conn=db_conn, invoice=invoice, invoice_id=invoice_id
    )


@router.get("/provider/{id}", description="Get provider Invoice by ID")
async def get_invoice_by_provider_id(
    db_conn: db_dependency,
    id: uuid.UUID,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await invoice_service.get_invoice_by_provider_id(
        db_conn=db_conn, invoice_id=id, provider_id=token_info.id
    )


@router.get("/customer/{id}", description="Get customer Invoice by ID")
async def get_invoice_by_customer_id(
    id: uuid.UUID,
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await invoice_service.get_invoice_by_customer_id(
        db_conn=db_conn, invoice_id=id, customer_id=token_info.id
    )


@router.get("/provider", description="Get all service provider Invoices")
async def get_invoices_by_service_provider(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await invoice_service.get_all_invoices_service_provider(
        db_conn=db_conn, service_provider_id=token_info.id
    )


@router.get("/customer", description="Get all customer invoices")
async def get_invoices_by_customer(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await invoice_service.get_all_invoices_customer(
        db_conn=db_conn, customer_id=token_info.id
    )
