import uuid
from datetime import datetime
from src.root.abstract_base import AbstractBaseModel
from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CreateInvoiceModel(AbstractBaseModel):
    customer_id: uuid.UUID
    due_date: datetime
    services_provided: dict
    quantity: int | None
    description: str | None
    items: list[dict] | None
    booking_id: uuid.UUID | None = None
    total_amount: int
    due_date: datetime


class InvoiceResponseModel(AbstractBaseModel):
    id: uuid.UUID
    service_provider_id: uuid.UUID
    customer_id: uuid.UUID
    status: str
    due_date: datetime
    price: str
    description: str
    services_provided: dict
    date_created: datetime


class UpdateInvoiceModel(AbstractBaseModel):
    status: str | None = None
    due_date: datetime | None = None
    price: str | None = None
    description: str | None = None
    services_provided: dict | None = None
    date_created: datetime | None = None
    last_updated: datetime | None = None
