from src.root.abstract_base import AbstractBaseModel
from uuid import UUID
from pydantic import field_validator, Field
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
    opening_hours: dict[str, dict] = Field(
        examples=[
            {
                "opening_hours": {
                    "Monday": {"open": "09:00", "close": "17:00"},
                    "Tuesday": {"open": "09:00", "close": "17:00"},
                    "Wednesday": {"open": "09:00", "close": "17:00"},
                    "Thursday": {"open": "09:00", "close": "17:00"},
                    "Friday": {"open": "09:00", "close": "17:00"},
                    "Saturday": {"open": "10:00", "close": "14:00"},
                    "Sunday": {"open": None, "close": None},
                }
            }
        ]
    )  # day: opening time
    address: list[Address]
    services_provided: dict = Field(
        examples=[
            {
                "services_provided": {
                    "Auto-Mechanic": {
                        "Oil Change": 5000,
                        "Engine Diagnostics": 3000,
                        "Timing Belt Replacement": 900,
                        "Fuel Injection Service": 7000,
                        "Radiator Flush": 6700,
                    }
                }
            }
        ]
    )


class ServiceResponse(AbstractBaseModel):
    id: UUID
    name: str
    bio: str | None = None
    category: list | None
    zip_code: str | None
    opening_hours: dict | None
    services_provided: dict | list | None
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
    longitude: float | None = 139.6917
    latitude: float | None = 35.6895


class SearchServices(AbstractBaseModel):
    coordinates: LocationCoordinates | None = None
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
