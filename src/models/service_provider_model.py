from src.root.abstract_base import AbstractBaseModel
from uuid import UUID
from pydantic import field_validator
from shapely.wkb import loads
from geoalchemy2.elements import WKBElement
from datetime import datetime


class AllCategory(AbstractBaseModel):
    category: dict


class Address(AbstractBaseModel):
    longitude: float
    latitude: float
    street: str
    state: str
    local_government: str
    default: bool = False


class Coordinates(AbstractBaseModel):
    longitude: float
    latitude: float


class CreateLocation(AbstractBaseModel):
    coordinates: Coordinates
    service_provider_id: UUID


class CreateService(AbstractBaseModel):
    name: str
    bio: str | None = None
    opening_hours: dict[str, dict]  # day: opening time
    address: list[Address]
    services_provided: dict


class ServiceResponse(AbstractBaseModel):
    id: UUID
    name: str
    bio: str | None = None
    category: list | None
    zip_code: str | None
    opening_hours: dict | None
    services_provided: dict | None
    is_active: bool
    profile_pic: str | None
    catalogue_pic: list | None
    rating: str | None
    address: list | None
    tags: list | None
    date_created: datetime
    coordinates: str | None = None

    @field_validator("coordinates", mode="before")
    @classmethod
    def parse_wkb(cls, value):
        if isinstance(value, WKBElement):
            point = loads(bytes(value.data))
            return f"{point.y}, {point.x}"
        return value


class LocationCoordinates(AbstractBaseModel):
    longitude: float
    latitude: float


class SearchServices(AbstractBaseModel):
    coordinates: LocationCoordinates
    category: list[str]
    location: str | None = None


class UpdateServices(AbstractBaseModel):
    name: str | None = None
    opening_hours: dict | None = None
    profile_pic: str | None = None
    address: Address | None = None
    catalogue_pic: list[str] | None = None
    services_provided: dict | None = None  # catetory: list of services
    tags: list = []
