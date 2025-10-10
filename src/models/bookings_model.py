from src.root.abstract_base import AbstractBaseModel
import uuid
from datetime import datetime


class CreateBookingModel(AbstractBaseModel):
    service_provider_id: uuid.UUID
    services_requested: dict[str, list]
    price: str
    description: str | None
    scheduled_date: datetime


class UpdateBookingModel(AbstractBaseModel):
    services_requested: dict | None = None
    price: str | None = None
    description: str | None = None
    scheduled_date: datetime | None = None
    status: str | None = None


class BookingResponse(AbstractBaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    service_provider_id: uuid.UUID
    price: int
    services_requested: dict
    scheduled_date: datetime
    address: dict
