from src.root.abstract_base import AbstractBaseModel
import uuid
from datetime import datetime
from src.models.invoice_models import Status


class BookingAddress(AbstractBaseModel):
    longitude: float
    latitude: float
    street: str
    state: str
    local_government: str


class CreateBookingModel(AbstractBaseModel):
    service_provider_id: uuid.UUID
    services_requested: dict
    price: str
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
