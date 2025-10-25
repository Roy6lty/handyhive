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


class CreateBookingModel(AbstractBaseModel):
    service_provider_id: uuid.UUID
    services_requested: dict = Field(
        examples=[{"Plumbing": {"Leak Detection": 4000, "Pipe Replacement": 8500}}]
    )
    price: int
    description: str | None
    address: BookingAddress
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
    services_requested: dict
    scheduled_date: datetime
    address: dict
