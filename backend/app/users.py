# backend/app/users.py

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.schemas import TokenWithUser
from app.auth import get_current_user
from app.database import get_db
from app.logging_config import logger
from app.auth import get_password_hash, create_access_token
from fastapi import status
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=TokenWithUser)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user: {user.username}")
    # Check if user already exists by email or username
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration failed: email already taken ({user.email})")
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        logger.warning(f"Registration failed: username already taken ({user.username})")
        raise HTTPException(status_code=400, detail="Username already registered")
    # Create user using CRUD to ensure random 10-digit user_id
    db_user = crud.create_user(db, user)
    logger.info(f"User registered successfully: {user.username}")
    # Create access token for new user
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

@router.patch("/level")
def change_user_level(
    user_id: int = Body(...),
    new_level: str = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logger.info(f"Attempting to change level for user_id={user_id} to {new_level}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.warning(f"User not found for level change: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if user.level == "admin_user":
        logger.warning(f"Attempt to change level of admin user: user_id={user_id}")
        raise HTTPException(status_code=403, detail="Cannot change level of admin user.")
    if new_level == "admin_user":
        logger.warning(f"Attempt to set user level to admin_user via API: user_id={user_id}")
        raise HTTPException(status_code=403, detail="Cannot set user level to admin_user via API.")
    user.level = new_level
    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} level changed to {new_level}")
    return {"message": f"User {user_id} level changed to {new_level}", "user": user}

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, updated_user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"Attempting to update user_id={user_id}")
    user = crud.update_user(db, user_id, updated_user)
    if not user:
        logger.warning(f"User not found for update: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User {user_id} updated successfully")
    return user

@router.patch("/{user_id}", response_model=schemas.UserOut)
def patch_user(user_id: int, partial_user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"PATCH request for user_id={user_id}")
    user = crud.update_user_partial(db, user_id, partial_user)
    if not user:
        logger.error(f"User with ID {user_id} not found for partial update")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User {user_id} updated successfully")
    return user

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"Listing all users")
    users = crud.get_all_users(db)
    logger.info(f"Returned {len(users)} users")
    return users

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"Fetching user_id={user_id}")
    user = crud.get_user_by_id(db, user_id=user_id)
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User {user_id} fetched successfully")
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"Attempting to delete user_id={user_id}")
    success = crud.delete_user(db, user_id)
    if not success:
        logger.warning(f"User not found for deletion: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User {user_id} deleted successfully")
    return {"message": f"User {user_id} deleted successfully"}

@router.patch("/deactivate/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logger.info(f"Attempting to deactivate user_id={user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.warning(f"User not found for deactivation: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if user.level == "inactive_user":
        raise HTTPException(status_code=400, detail="User already inactive")
    # Delete all certificates owned by the user
    certs = db.query(models.Certificate).filter(models.Certificate.owner_user_id == user_id).all()
    for cert in certs:
        db.delete(cert)
    # Set user level to inactive_user
    user.level = "inactive_user"
    db.commit()
    db.refresh(user)
    return {"message": f"User {user_id} deactivated and all certificates deleted", "user": user}