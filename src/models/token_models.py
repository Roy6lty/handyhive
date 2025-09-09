import time
from enum import StrEnum
from typing import Annotated, Any

from pydantic import UUID4, Field, StringConstraints, field_validator, model_validator
from sqlalchemy import UUID
from typing_extensions import TypedDict

from src.root.abstract_base import AbstractBaseModel


class Roles(StrEnum):
    USER = "user"
    ADMIN = "admin"


class TokenType(StrEnum):
    access_token = "access_token"
    refresh_token = "refresh_token"


class OpenIDToken(StrEnum):
    APPLE = "apple"
    GOOGLE = "google"


class UserStatus(StrEnum):
    active = "active"
    suspended = "suspended"
    archived = "archived"


class RolePermission(AbstractBaseModel):
    role: Roles
    permissions: list[Roles]


# RoleSetterSchema = {
#     "general": RolePermission(
#         role=Roles.staff, permissions=[Roles.super_admin, Roles.admin, Roles.staff]
#     ),
#     "record_creation": RolePermission(
#         role=Roles.staff, permissions=[Roles.super_admin, Roles.admin, Roles.staff]
#     ),
#     "record_access": RolePermission(
#         role=Roles.staff, permissions=[Roles.super_admin, Roles.admin, Roles.staff]
#     ),
#     "custom_access": RolePermission(role=Roles.user, permissions=[]),
#     "admin": RolePermission(
#         role=Roles.admin, permissions=[Roles.super_admin, Roles.admin]
#     ),
#     "super_admin": RolePermission(
#         role=Roles.super_admin, permissions=[Roles.super_admin]
#     ),
# }


class AccountData(TypedDict):
    id: UUID
    is_active: bool
    first_name: str
    last_name: str
    role: str


class AccessTokenEncode(AbstractBaseModel):
    id: str
    is_active: bool
    role: Roles

    @field_validator("id", mode="before")
    @classmethod
    def convert_to_str(cls, value: Any) -> str | None:
        if value is None:
            return None
        value = str(value)
        return value.strip()


class RefreshTokenDataEncode(AccessTokenEncode):
    token_jit: str | None

    @field_validator("id", "token_jit", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, value: Any):  # type: ignore
        if value is None:
            return None
        value = str(value)
        return value.strip()


class AccessTokenData(AbstractBaseModel):
    id: UUID4
    is_active: bool
    role: str


class RefreshTokenData(AccessTokenData):
    token_jit: UUID4 | None


class AccessTokenResponse(AbstractBaseModel):
    token_type: str = "bearer"
    access_token: Annotated[str, StringConstraints(max_length=1000)]


class RefreshTokenResponse(AccessTokenResponse):
    refresh_token: Annotated[str, StringConstraints(max_length=1000)]


class LoginResponse(RefreshTokenResponse):
    id: UUID4
    email: str
    is_active: bool | None = False
    role: str
    first_name: str
    last_name: str


class TwoFAResponse(AbstractBaseModel):
    message: str = "enter code sent to email for verification"


class UpdateProfileTokenSchema(AbstractBaseModel):
    token_jit: UUID4 | None = None


class PaymentTokenSchema(AbstractBaseModel):
    token: str | None
    payment_platform: str
    notification_message: str | None = None
    subscription_id: str | None

    @field_validator("token", mode="before")
    @classmethod
    def convert_to_str(cls, value: Any):
        if value is None:
            return None
        value = str(value)
        return value.strip()


class AppleOAuthToken(AbstractBaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    token: Annotated[str, StringConstraints(max_length=1000)]

    @field_validator("email", "first_name", "last_name", mode="before")
    @classmethod
    def convert_to_str(cls, value: Any):
        if value is None:
            return None
        value = str(value)
        return value.strip()
