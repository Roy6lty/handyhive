from enum import StrEnum
from datetime import datetime, time
from src.root.abstract_base import AbstractBaseModel
from pydantic import Field
import time
from uuid import UUID


class AllCategory(AbstractBaseModel):
    category: dict[str, list[dict]]


class Address(AbstractBaseModel):
    street: str
    state: str
    local_government: str


class Coordinates(AbstractBaseModel):
    longitude: float
    latitude: float


class CreateLocation(AbstractBaseModel):
    coordinates: Coordinates
    service_provider_id: UUID


class CreateService(AbstractBaseModel):
    name: str
    category: list[str]
    opening_hours: str
    closing_hours: str
    address: Address
    services_provided: dict[str, list[dict]]  # catetory: list of services
    tags: list
    location: Coordinates | None = None


class ServiceResponse(AbstractBaseModel):
    name: str
    opening_hours: str
    closing_hours: str
    address: Address
    services_provided: dict  # catetory: list of services
    tags: list | None


class LocationCoordinates(AbstractBaseModel):
    longitude: float
    latitude: float


class SearchServices(AbstractBaseModel):
    coordinates: LocationCoordinates
    category: list[str]
    location: str | None = None


class UpdateServices(AbstractBaseModel):
    name: str | None = None
    opening_hours: str | None = None
    closing_hours: str | None = None
    profile_pic: str | None = None
    address: Address | None = None
    catalogue_pic: list[str] | None = None
    services_provided: dict | None = None  # catetory: list of services
    tags: list = []
