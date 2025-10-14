from enum import StrEnum
from uuid import UUID
from src.root.abstract_base import AbstractBaseModel
from pydantic import Field
from src.models.token_models import Roles
from src.models.service_provider_model import Address


class AccountType(StrEnum):
    service_provider = "SERVICE PROVIDER"
    customer = "CUSTOMER"


class CreateUserSchema(AbstractBaseModel):
    first_name: str
    last_name: str
    email: str
    phone_no: str
    country_code: str
    hasheded_password: str = Field(serialization_alias="password")
    account_type: AccountType


class Update2faCode(AbstractBaseModel):
    two_fa_auth_code: str | None
    two_fa_auth_expiry_time: int


class SocialLinks(AbstractBaseModel):
    platform: str
    url: str


class UpdateUser(AbstractBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_no: str | None = None
    country_code: str | None = None
    profile_pic: str | None = None
    two_fa: bool | None = None
    address: list[Address] | None = None
    social_links: list[SocialLinks]


class UpdateUserProfile(UpdateUser):
    token_jit: UUID | None = None
    hashed_password: str | None = None
    is_active: bool | None = None
    role: Roles | None = None
    push_notifications: bool | None = None
    promotional_notifications: dict | None = None


class VerifyOTP(AbstractBaseModel):
    email: str
    otp: str


class UserProfileResponse(AbstractBaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone_no: str
    country_code: str
    address: list[dict] | None
    social_links: list[dict] | None
    is_active: bool
    role: Roles
    two_fa: bool
    profile_pic: str | None
    referral_code: str | None


class NotificationSchema(AbstractBaseModel):
    push_notifications: bool | None = None
    promotional_notifications: dict | None = None
