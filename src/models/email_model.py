from enum import StrEnum
from src.root.abstract_base import AbstractBaseModel


class EmailTemplates(StrEnum):
    TWO_FACTOR_AUTHENTICATION = "authorization_code.html"


class EmailSchema(AbstractBaseModel):
    subject: str
    recipients: list[str]
