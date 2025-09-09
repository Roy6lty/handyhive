from src.root.abstract_base import AbstractBaseModel
from pydantic import UUID4
from datetime import datetime
from src.models.token_models import Roles
from uuid import UUID


class UserTableModel(AbstractBaseModel):
    id: UUID4
    first_name: str
    last_name: str
    phone_no: str
    country_code: str
    role: Roles
    hashed_password: str
    email: str
    is_active: bool
    account_type: str
    two_fa_auth_code: str | None
    two_fa_auth_expiry_time: int = 0
    two_fa: bool = False
    token_jit: UUID | None
    profile_pic: str | None
    biodata: dict | None = None
    referral_code: str | None
    date_created: datetime
    last_updated: datetime


class ServiceProviderTableModel(AbstractBaseModel):
    id: UUID4
    name: str
    category: list | None
    zip_code: str | None
    closing_hours: str | None
    opening_hours: str | None
    services_provided: dict | None
    is_active: bool
    profile_pic: str | None
    catalogue_pic: list | None
    rating: str | None
    address: dict | None
    tags: list | None
    date_created: datetime
    last_updated: datetime


class LocationTableModel(AbstractBaseModel):
    id: UUID4
    service_provider_id: UUID4
    coordinates: str | None
    longitude: float | None
    latitude: float | None
    name: str | None
    date_created: datetime
    last_updated: datetime
