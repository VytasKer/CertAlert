# backend/app/schemas.py
# Imports
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

# User schemas

# Response schema for token + user (for registration/login endpoints)
class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: 'UserOut'

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr
    level: str = 'free_user'

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # allows conversion from SQLAlchemy model

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]

#Certificate schemas

class Certificate(BaseModel):
    id: int
    name: Optional[str]
    file_name: str
    content_pem: str
    uploaded_at: datetime
    issuer: str
    subject: str
    valid_from: datetime
    valid_to: datetime
    serial_number: str
    fingerprint: str
    owner_user_id: Optional[int]
    days_left: int

    class Config:
        orm_mode = True

# --- Password Reset/Change ---
class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetSubmit(BaseModel):
    token: str
    new_password: str
    confirm_password: str

# --- Contact Us ---
class ContactQuery(BaseModel):
    email: EmailStr
    topic: str
    message: str
    # file: Optional[bytes]  # For now, file handling will be added later

# --- Subscription Schemas ---
class SubscriptionStatus(str, Enum):
    INITIATED = "INITIATED"
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"

class SubscriptionBase(BaseModel):
    sub_user_id: int
    sub_source: str = "certalert_page"
    sub_status: SubscriptionStatus = SubscriptionStatus.INITIATED
    sub_amount: float = 0.0
    sub_start_date: datetime
    sub_end_date: datetime
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    sub_status: SubscriptionStatus
    sub_ended: Optional[bool] = None
    sub_cancelled: Optional[bool] = None
    sub_end_date: Optional[datetime] = None
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None

class SubscriptionOut(SubscriptionBase):
    sub_id: int
    sub_ended: bool
    sub_cancelled: bool
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None

    class Config:
        orm_mode = True