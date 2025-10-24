from datetime import datetime
from typing import List
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    ForeignKey,
    String,
    Integer,
    Index,
    TEXT,
    Float,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.root.abstract_database import AbstractBase
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from uuid import uuid4


class HandyTenet(AbstractBase):
    __tablename__ = "handy_tenet"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    contact_email: Mapped[str] = mapped_column(String, nullable=True)
    contact_phone_number: Mapped[str] = mapped_column(String, nullable=True)
    faq: Mapped[str] = mapped_column(String, nullable=True)


class UserTable(AbstractBase):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    referral_code: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(ARRAY(JSONB), nullable=True)
    phone_no: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    social_links: Mapped[str] = mapped_column(JSONB, nullable=True)
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
    push_notifications: Mapped[bool] = mapped_column(Boolean, nullable=True)
    promotional_notifications: Mapped[dict] = mapped_column(JSONB, nullable=True)
    message: Mapped[list["MessagesTable"]] = relationship(back_populates="user")

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
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(JSONB, nullable=True)
    category: Mapped[str] = mapped_column(ARRAY(String), nullable=True)
    zip_code: Mapped[str] = mapped_column(String, nullable=True)
    # closing_hours: Mapped[str] = mapped_column(String, nullable=True)
    opening_hours: Mapped[str] = mapped_column(JSONB, nullable=True)
    services_provided: Mapped[dict] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_pic: Mapped[str] = mapped_column(String, nullable=True)
    catalogue_pic: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    location: Mapped[list["LocationTable"]] = relationship(back_populates="provider")
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
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    service_provider_id: Mapped[UUID] = mapped_column(
        ForeignKey(ServiceProviderTable.id), nullable=True
    )
    coordinates: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326)
    )
    provider: Mapped[list["ServiceProviderTable"]] = relationship(
        back_populates="location"
    )

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


class NotificationsTable(AbstractBase):
    __tablename__ = "notifications"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=True)


class FirebaseNotificationsTable(AbstractBase):
    __tablename__ = "firebase_notifications"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    device_token: Mapped[str] = mapped_column(String, nullable=True)
    mode: Mapped[str] = mapped_column(String, nullable=True)


class NotificationPreferencesTable(AbstractBase):
    __tablename__ = "notifications_preferences"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)

    push_notification: Mapped[bool] = mapped_column(Boolean, nullable=True)
    promotional_notification: Mapped[dict] = mapped_column(JSONB, nullable=True)


class ServicesTagsTable(AbstractBase):
    __tablename__ = "services"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    service_provider_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    sub_service: Mapped[str] = mapped_column(String, nullable=True)
    service: Mapped[str] = mapped_column(String, nullable=True)


class BookingsTable(AbstractBase):
    __tablename__ = "bookings"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    service_provider_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    price: Mapped[UUID] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    services_requested: Mapped[dict] = mapped_column(JSONB, nullable=True)
    scheduled_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    address: Mapped[dict] = mapped_column(JSONB, nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)


class InvoiceTable(AbstractBase):
    __tablename__ = "invoices"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    service_provider_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    due_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    services_provided: Mapped[dict] = mapped_column(JSONB, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    booking_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    invoice_items: Mapped[dict] = mapped_column(JSONB, nullable=True)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=True)


class ReferralTable(AbstractBase):
    __tablename__ = "referrals"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
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
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey(UserTable.id))
    sender_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    receiver_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    content: Mapped[str] = mapped_column(TEXT)
    profile_pic: Mapped[str] = mapped_column(
        String, nullable=True
    )  # update this field when the user updates the profile pic
    edited: Mapped[bool] = mapped_column(Boolean, default=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped[UserTable] = relationship(back_populates="message")
