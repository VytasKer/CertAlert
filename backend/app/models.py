# backend/app/models.py

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Date, ForeignKey, func, Enum, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False, unique=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    level = Column(String(32), nullable=True, default='free_user')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # OAuth fields for Google authentication
    google_id = Column(String(255), nullable=True, index=True)
    google_email = Column(String(255), nullable=True)
    profile_picture_url = Column(String(512), nullable=True)
    auth_provider = Column(String(50), nullable=False, default='local', index=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    last_google_sync = Column(DateTime(timezone=True), nullable=True)

    certificates = relationship("Certificate", back_populates="owner", cascade="all, delete")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(BigInteger, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=True)  # Optional user-defined name
    file_name = Column(String, nullable=True)  # Original filename of uploaded file
    content_pem = Column(Text, nullable=True)  # Raw PEM format or extracted from upload
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    issuer = Column(String, nullable=True)  # From certificate metadata
    subject = Column(String, nullable=True)  # From certificate metadata
    valid_from = Column(DateTime, nullable=True)  # NotBefore
    valid_to = Column(DateTime, nullable=True)  # NotAfter
    serial_number = Column(String, nullable=True)  # Unique serial
    fingerprint = Column(String, nullable=True)  # SHA1 or SHA256 hash

    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="certificates")

# Subscription status enum
class SubscriptionStatus(enum.Enum):
    INITIATED = "INITIATED"
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"

class Subscription(Base):
    __tablename__ = "subscriptions"

    sub_id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    sub_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sub_source = Column(String(64), nullable=False, default="certalert_page")
    sub_status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.INITIATED)
    sub_amount = Column(Float, nullable=True)
    sub_start_date = Column(DateTime, nullable=False)
    sub_end_date = Column(DateTime, nullable=False)
    sub_ended = Column(Boolean, nullable=False, default=False)
    sub_cancelled = Column(Boolean, nullable=False, default=False)
    stripe_session_id = Column(String(128), nullable=True)
    stripe_payment_intent_id = Column(String(128), nullable=True)

    user = relationship("User", backref="subscriptions")

# Stripe Checkout logging
class StripeCheckout(Base):
    __tablename__ = "stripe_checkouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sub_id = Column(Integer, ForeignKey("subscriptions.sub_id", ondelete="SET NULL"), nullable=True)
    price_id = Column(String(64), nullable=False)
    session_id = Column(String(256), nullable=True)
    success_url = Column(Text, nullable=True)
    cancel_url = Column(Text, nullable=True)
    status = Column(String(32), nullable=True)
    raw_request = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)  # Already Text, no change needed

# Stripe Webhook logging
class StripeWebhook(Base):
    __tablename__ = "stripe_webhooks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    received_at = Column(DateTime, server_default=func.now(), nullable=False)
    event_id = Column(String(128), nullable=True)
    event_type = Column(String(64), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sub_id = Column(Integer, ForeignKey("subscriptions.sub_id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(128), nullable=True)
    payment_intent_id = Column(String(128), nullable=True)
    raw_payload = Column(Text, nullable=True)
    processing_status = Column(String(32), nullable=True)
    error_message = Column(Text, nullable=True)


class TrafficLog(Base):
    """Model for storing traffic logs in database for persistence across restarts"""
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)  # For efficient date-based queries
    log_data = Column(JSON, nullable=False)  # Store the full JSON log entry
    ip_hash = Column(String(64), nullable=True, index=True)  # For efficient IP-based queries
    path = Column(String(255), nullable=True, index=True)  # For efficient path-based queries
    status_code = Column(Integer, nullable=True, index=True)  # For efficient status queries


class AdminSetting(Base):
    """Model for storing admin configurable settings"""
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)