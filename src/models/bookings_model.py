import uuid
from datetime import datetime
from pydantic import Field
from src.root.abstract_base import AbstractBaseModel
from src.models.invoice_models import Status


class BookingAddress(AbstractBaseModel):
    longitude: float | None = None
    latitude: float | None = None
    street: str | None = None
    state: str | None = None
    local_government: str | None = None
    nickname: str | None = None


class CreateBookingModel(AbstractBaseModel):
    service_provider_id: uuid.UUID
    services_requested: dict | list = Field(
        examples=[
            [
                {
                    "id": "0b27f6a7-22b9-4b1e-bae0-0358428fa355",
                    "name": "Oil Change",
                    "price": 5000,
                },
                {
                    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                    "name": "Engine Diagnostics",
                    "price": 150000,
                },
                {
                    "id": "9c858901-8a57-4791-81fe-4c455b099bc9",
                    "name": "Fuel Injection Service",
                    "price": 90000,
                },
                {
                    "id": "a2b4c5d6-e7f8-4901-9abc-1234567890de",
                    "name": "Timing Belt Replacement",
                    "price": 1000,
                },
            ]
        ]
    )
    price: int
    description: str | None = None
    address: BookingAddress | None = None
    scheduled_date: datetime
    quick_fix: bool = False


class UpdateBookingModel(AbstractBaseModel):
    services_requested: dict | None = None
    price: str | None = None
    description: str | None = None
    scheduled_date: datetime | None = None


class UpdateBookingStatus(AbstractBaseModel):
    status: Status


class BookingResponse(AbstractBaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    service_provider_id: uuid.UUID
    price: int
    services_requested: dict | list
    scheduled_date: datetime
    address: dict | None = None
