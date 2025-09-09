from src.root.abstract_base import AbstractBaseModel
from src.models import user_model
from pydantic import Field, UUID4


class SuccessfulResponse(AbstractBaseModel):
    message: str = "successful"


class PasswordChangeSchema(AbstractBaseModel):
    old_password: str
    new_password: str


class LoginResponse(AbstractBaseModel):
    id: UUID4
    access_token: str
    refresh_token: str
    first_name: str
    last_name: str
    account_type: str
    role: user_model.Roles


class LoginSchema(AbstractBaseModel):
    email: str
    password: str


class TwoFAResponse(AbstractBaseModel):
    message: str = "2FA code sent to your email"


class CreateUserSchema(AbstractBaseModel):
    first_name: str
    last_name: str
    email: str
    phone_no: str
    country_code: str
    hashed_password: str = Field(serialization_alias="password")
    account_type: user_model.AccountType


class CreateUserResponse(AbstractBaseModel):
    message: str = "account successfully created"


class OpenIDUserDataModel(AbstractBaseModel):
    email: str
    first_name: str
    last_name: str
    profile_pic: str
