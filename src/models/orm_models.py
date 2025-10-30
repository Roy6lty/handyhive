import uuid
from pydantic import field_validator
from shapely.wkb import loads
from src.root.abstract_base import AbstractBaseModel
from datetime import datetime
from src.models.token_models import Roles
from geoalchemy2.elements import WKBElement


class UserTableModel(AbstractBaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    phone_no: str
    address: list[dict] | None
    social_links: list[dict] | None
    country_code: str
    role: Roles
    hashed_password: str
    email: str
    is_active: bool
    account_type: str
    two_fa_auth_code: str | None
    two_fa_auth_expiry_time: int = 0
    two_fa: bool = False
    token_jit: uuid.UUID | None
    profile_pic: str | None
    biodata: dict | None = None
    referral_code: str | None
    push_notifications: bool | None = None
    promotional_notifications: dict | None
    date_created: datetime
    last_updated: datetime


class LocationTableModel(AbstractBaseModel):
    id: uuid.UUID
    service_provider_id: uuid.UUID
    coordinates: str | None
    longitude: float | str | None
    latitude: float | str | None
    # name: str | None
    date_created: datetime
    last_updated: datetime

    @field_validator("coordinates", mode="before")
    @classmethod
    def parse_wkb(cls, value):
        if isinstance(value, WKBElement):
            point = loads(bytes(value.data))
            return f"{point.y}, {point.x}"
        return value


class ServiceProviderTableModel(AbstractBaseModel):
    id: uuid.UUID
    name: str
    bio: str | None
    category: list | None
    zip_code: str | None
    opening_hours: dict | None
    services_provided: dict | list | None
    is_active: bool
    profile_pic: str | None
    catalogue_pic: list | None
    rating: str | None
    address: list | dict | None
    tags: list | None
    date_created: datetime
    last_updated: datetime


class NotificationsTableModel(AbstractBaseModel):
    id: uuid.UUID
    title: str
    body: str
    image: str | None = None
    timestamp: int
    read: bool = False
    user_id: str
    date_created: datetime
    last_updated: datetime


class NotificationsPreferenceTableModel(AbstractBaseModel):
    id: uuid.UUID
    push_notifications: bool
    promotional_notifications: dict
    date_created: datetime
    last_updated: datetime


class MessageTableModel(AbstractBaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    read: bool
    edited: bool


class BookingsTableModel(AbstractBaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    service_provider_id: uuid.UUID
    price: int | None = 0
    description: str | None
    services_requested: dict | list
    rating: int | None
    review: str | None
    date_created: datetime
    last_updated: datetime
    address: dict | None
    scheduled_date: datetime | None


class InvoiceTableModel(AbstractBaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    service_provider_id: uuid.UUID
    status: str
    due_date: datetime
    price: uuid.UUID
    description: str | None
    services_requested: dict | list
    rating: int | None
    review: str | None
    date_created: datetime
    last_updated: datetime
