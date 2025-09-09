from datetime import datetime
from gettext import Catalog
import uuid
from typing import List
from sqlalchemy import (
    ARRAY,
    Boolean,
    ForeignKey,
    String,
    Integer,
    Index,
    TEXT,
    Float,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.root.abstract_database import AbstractBase
from geoalchemy2 import Geometry


class HandyTenet(AbstractBase):
    __tablename__: str = "handy_tenet"
    contact_email: Mapped[str] = mapped_column(String, nullable=True)
    contact_phone_number: Mapped[str] = mapped_column(String, nullable=True)
    faq: Mapped[str] = mapped_column(String, nullable=True)


class UserTable(AbstractBase):
    __tablename__ = "users"
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    referral_code: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    phone_no: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    biodata: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String)
    two_fa_auth_code: Mapped[str] = mapped_column(String, nullable=True)
    two_fa_auth_expiry_time: Mapped[int] = mapped_column(Integer, default=0)
    two_fa: Mapped[bool] = mapped_column(Boolean, default=False)
    token_jit: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    profile_pic: Mapped[str] = mapped_column(String, nullable=True)
    referral_code: Mapped[str] = mapped_column(String, nullable=True)
    account_type: Mapped[str] = mapped_column(String)

    __table_args__ = (
        Index(
            "idx_id",  # Index name
            "id",
            "email",
            unique=True,  # Unique index
            postgresql_using="btree",  # PostgreSQL specific index type
        ),
    )


class ServiceProviderTable(AbstractBase):
    __tablename__ = "service_providers"
    name: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(JSONB, nullable=True)
    category: Mapped[str] = mapped_column(ARRAY(String), nullable=True)
    zip_code: Mapped[str] = mapped_column(String, nullable=True)
    closing_hours: Mapped[str] = mapped_column(String, nullable=True)
    opening_hours: Mapped[str] = mapped_column(String, nullable=True)
    services_provided: Mapped[dict] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_pic: Mapped[str] = mapped_column(String, nullable=True)
    catalogue_pic: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    __table_args__ = (
        Index(
            "idx_id_service",  # Index name
            "id",
            unique=True,  # Unique index
            postgresql_using="btree",  # PostgreSQL specific index type
        ),
    )


class LocationTable(AbstractBase):
    __tablename__ = "locations"
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    service_provider_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    coordinates: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326))

    __table_args__ = (
        Index(
            "idx_location_id",  # Index name
            "id",
            unique=True,  # Unique index
            postgresql_using="btree",  # PostgreSQL specific index type
        ),
        Index("idx_location_geom", "coordinates", postgresql_using="gist"),
        Index(
            "idx_service_provider_id",  # Index name
            "service_provider_id",
            unique=True,  # Unique index
            postgresql_using="btree",  # PostgreSQL specific index type
        ),
    )


class notificationPreferences(AbstractBase):
    __tablename__ = "notifications"
    push_notification: Mapped[dict] = mapped_column(JSONB, nullable=True)
    promotional_notification: Mapped[dict] = mapped_column(JSONB, nullable=True)


class ServicesTags(AbstractBase):
    __tablename__ = "services"
    service_provider_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    sub_service: Mapped[str] = mapped_column(String, nullable=True)
    service: Mapped[str] = mapped_column(String, nullable=True)


class ServiceHistory(AbstractBase):
    __tablename__ = "service_history"
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    service_provider_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    price: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    services_provided: Mapped[dict] = mapped_column(JSONB, nullable=True)
    schduled_date: Mapped[datetime] = mapped_column()


class ReferralTable(AbstractBase):
    __tablename__ = "referrals"
    name: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(JSONB, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    biodata: Mapped[dict] = mapped_column(JSONB, nullable=True)
    role: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String)
    two_fa_auth_code: Mapped[str] = mapped_column(String, nullable=True)
    two_fa_auth_expiry_time: Mapped[int] = mapped_column(Integer, nullable=True)
    two_fa: Mapped[bool] = mapped_column(Boolean, default=False)
    token_jit: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    profile_pic: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index(
            "idx_referral",  # Index name
            "id",
            "email",
            unique=True,  # Unique index
            postgresql_using="btree",  # PostgreSQL specific index type
        ),
    )


class MessagesTable(AbstractBase):
    __tablename__ = "messages"
    sender: Mapped[str] = mapped_column(String, nullable=True)
    receiver: Mapped[str] = mapped_column(String, nullable=True)
    contact_email: Mapped[str] = mapped_column(String, nullable=True)
