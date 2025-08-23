# test.py

from fastapi import FastAPI
from sqlalchemy import create_engine
from pydantic import BaseModel
from jose import jwt
from passlib.hash import bcrypt
from email_validator import validate_email, EmailNotValidError
import dotenv
import cryptography
import loguru

print("All libraries imported successfully!")