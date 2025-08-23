# backend/app/auth.py

# --- Imports and router setup ---
from fastapi import Request, APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app import schemas
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from app.notifications import send_email
import logging

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

router = APIRouter(prefix="/auth", tags=["Auth"])

logger = logging.getLogger("password_reset")

# FastAPI dependency that reads the token from the Authorization header
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

bearer_scheme = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == user_email).first()
    if user is None:
        raise credentials_exception
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Password Reset/Change ---
def create_password_reset_token(email: str, expires_minutes: int = 60):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": email, "exp": expire, "purpose": "password_reset"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None

@router.post("/login")
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Patch: If user.level is None, set to 'free_user' for legacy users
    if not getattr(user, 'level', None):
        user.level = 'free_user'
        db.commit()
        db.refresh(user)
    if user.level == "inactive_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    # Patch: If user.level is None, set to 'free_user' for legacy users
    if not getattr(current_user, 'level', None):
        current_user.level = 'free_user'
    return current_user

@router.post("/request-password-reset")
def request_password_reset(data: schemas.PasswordResetRequest, db: Session = Depends(get_db), request: Request = None):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    # Always return success for privacy
    if user:
        expires_minutes = 60  # Default, but can be changed if needed
        token = create_password_reset_token(user.email, expires_minutes)
        reset_url = f"{FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={token}"
        body = (
            f"Hello {user.username},\n\n"
            f"You requested a password reset for your CertAlert account. "
            f"Click the link below to reset your password. This link will expire in {expires_minutes} minutes.\n\n"
            f"Reset Password: {reset_url}\n\n"
            f"If you did not request this, you can ignore this email.\n\n"
            f"Best regards,\nCertAlert Team"
        )
        send_email(user.email, "CertAlert Password Reset", body)
        logger.info(f"Password reset email sent to {user.email}")
    return {"message": "If your email is registered, a password reset link has been sent."}

@router.post("/reset-password")
def reset_password(data: schemas.PasswordResetSubmit, db: Session = Depends(get_db)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    email = verify_password_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    logger.info(f"Password changed for user {user.email} (id={user.id}) at {datetime.utcnow().isoformat()}.")
    return {"message": "Your password has been changed successfully."}

# --- Contact Us API ---
@router.post("/contact-query")
async def contact_query(
    email: str = Form(...),
    topic: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(None)
):
    from_email = os.getenv("FROM_EMAIL")
    subject = f"Contact query from {email}"
    body = (
        f"Topic: {topic}\n\n"
        f"Concern: {message}\n\n"
    )
    attachment = None
    filename = None
    if file:
        attachment = await file.read()
        filename = file.filename
    from app.notifications import send_email_with_attachment
    send_email_with_attachment(from_email, subject, body, attachment, filename)
    return {"message": "We will come back to you as soon as possible."}