# backend/app/certificates.py

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
import random
from app.auth import get_current_user
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime
#import hashlib
from cryptography.hazmat.primitives import hashes
from fastapi import Form
from app.utils import days_until_expiry

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.post("/upload")
async def upload_certificate(
    file: UploadFile = File(...),
    name: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Restrict all users to max 20 certs
    user_certs_count = db.query(models.Certificate).filter_by(owner_user_id=current_user.id).count()
    if user_certs_count >= 20:
        raise HTTPException(status_code=403, detail="You can only upload up to 20 certificates per account.")
    # Restrict free_user to only 1 cert
    if getattr(current_user, 'level', None) == 'free_user' and user_certs_count >= 1:
        raise HTTPException(status_code=403, detail="You have to be subscribed to upload more than 1 certificate.")

    contents = await file.read()

    try:
        cert = x509.load_pem_x509_certificate(contents, default_backend())
    except Exception:
        try:
            cert = x509.load_der_x509_certificate(contents, default_backend())
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid certificate format")

    fingerprint = cert.fingerprint(hashes.SHA256()).hex()
    serial_number = format(cert.serial_number, 'x')
    issuer = cert.issuer.rfc4514_string()
    subject = cert.subject.rfc4514_string()
    valid_from = cert.not_valid_before_utc
    valid_to = cert.not_valid_after_utc

    # Generate a unique random 8-digit integer ID
    for _ in range(10):
        random_id = random.randint(10_000_000, 99_999_999)
        if not db.query(models.Certificate).filter_by(id=random_id).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique certificate ID")

    db_cert = models.Certificate(
        id=random_id,
        file_name=file.filename,
        name=name,
        content_pem=contents.decode("utf-8", errors="ignore"),
        issuer=issuer,
        subject=subject,
        valid_from=valid_from,
        valid_to=valid_to,
        serial_number=serial_number,
        fingerprint=fingerprint,
        owner_user_id=current_user.id
    )

    db.add(db_cert)
    db.commit()
    db.refresh(db_cert)

    return {"message": "Certificate uploaded", "id": db_cert.id}

@router.patch("/{cert_id}/name", response_model=schemas.Certificate)
def update_certificate_name(
    cert_id: int,
    name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cert = db.query(models.Certificate).filter_by(id=cert_id, owner_user_id=current_user.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    cert.name = name
    db.commit()
    db.refresh(cert)
    days_left = days_until_expiry(cert.valid_to)
    cert_dict = cert.__dict__.copy()
    cert_dict["days_left"] = days_left
    return schemas.Certificate(**cert_dict)

@router.delete("/{cert_id}", status_code=204)
def delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cert = db.query(models.Certificate).filter_by(id=cert_id, owner_user_id=current_user.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    db.delete(cert)
    db.commit()

# Admin-only route to delete any certificate
@router.delete("/admin_delete/{cert_id}", status_code=204)
def admin_delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cert = db.query(models.Certificate).filter_by(id=cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    db.delete(cert)
    db.commit()

@router.get("/", response_model=list[schemas.Certificate])
def list_certificates(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    certs = db.query(models.Certificate).all()
    result = []
    for cert in certs:
        days_left = days_until_expiry(cert.valid_to)
        cert_dict = cert.__dict__.copy()
        cert_dict["days_left"] = days_left
        result.append(schemas.Certificate(**cert_dict))
    return result

@router.get("/user", response_model=list[schemas.Certificate])
def list_user_certificates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Returns a list of certificates owned by the authenticated user.
    """
    certs = db.query(models.Certificate).filter_by(owner_user_id=current_user.id).all()
    result = []
    for cert in certs:
        days_left = days_until_expiry(cert.valid_to)
        cert_dict = cert.__dict__.copy()
        cert_dict["days_left"] = days_left
        result.append(schemas.Certificate(**cert_dict))
    return result

@router.get("/{cert_id}", response_model=schemas.Certificate)
def get_certificate(cert_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id, models.Certificate.owner_user_id == current_user.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    days_left = days_until_expiry(cert.valid_to)
    cert_dict = cert.__dict__.copy()
    cert_dict["days_left"] = days_left
    return schemas.Certificate(**cert_dict)


@router.patch("/update_valid_to/{cert_id}", response_model=schemas.Certificate)
def test_update_valid_to(
    cert_id: int,
    new_valid_to: datetime = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Test-only: Update the valid_to date of a certificate you own.
    """
    cert = db.query(models.Certificate).filter(
        models.Certificate.id == cert_id,
        models.Certificate.owner_user_id == current_user.id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    cert.valid_to = new_valid_to
    db.commit()
    db.refresh(cert)
    days_left = days_until_expiry(cert.valid_to)
    cert_dict = cert.__dict__.copy()
    cert_dict["days_left"] = days_left
    return schemas.Certificate(**cert_dict)