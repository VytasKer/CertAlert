# backend/app/crud.py

from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash
from app.logging_config import logger

#user operations

import random

def generate_unique_user_id(db: Session):
    # Generate 9-digit number to stay within PostgreSQL integer range (max 2,147,483,647)
    # Range: 100,000,000 to 999,999,999
    while True:
        user_id = random.randint(100_000_000, 999_999_999)
        if not db.query(models.User).filter(models.User.id == user_id).first():
            return user_id

def create_user(db: Session, user: schemas.UserCreate):
    logger.debug(f"Creating user in DB: {user.username}")
    user_id = generate_unique_user_id(db)
    db_user = models.User(
        id=user_id,
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        level=getattr(user, 'level', 'free_user') or 'free_user'
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created in DB: {db_user.username} (id={user_id})")
    return db_user

def update_user(db: Session, user_id: int, user_data: schemas.UserCreate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    user.username = user_data.username
    user.email = user_data.email
    user.hashed_password = get_password_hash(user_data.password)
    db.commit()
    db.refresh(user)
    return user

def update_user_partial(db: Session, user_id: int, user_data: schemas.UserUpdate):
    logger.debug(f"Updating user {user_id} with data: {user_data}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.warning(f"User {user_id} not found during update")
        return None

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} updated in DB")
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True