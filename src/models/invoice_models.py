import uuid
from enum import StrEnum
from datetime import datetime
from pydantic import Field
from src.root.abstract_base import AbstractBaseModel


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
    items: list[dict] = Field(
        examples=[
            [
                {
                    "item": "Paint Brush",
                    "quantity": 5,
                    "description": "This is a very important item to be used for the job",
                    "price": 200,
                }
            ]
        ]
    )
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
