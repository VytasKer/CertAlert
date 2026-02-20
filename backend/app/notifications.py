# backend/app/notifications.py

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.utils import days_until_expiry
import os
from app.env_loader import load_env
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

load_env()

# Hardcoded alert days for MVP
ALERT_DAYS = [30, 14, 7, 5, 4, 3, 2, 1]

# Email server config
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())

def send_email_with_attachment(to_email: str, subject: str, body: str, attachment: bytes = None, filename: str = None):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    msg.attach(MIMEText(body))
    if attachment and filename:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())

def notify_users_of_expiring_certs(db: Session):
    users = db.query(models.User).all()
    for user in users:
        certs = db.query(models.Certificate).filter_by(owner_user_id=user.id).all()
        for cert in certs:
            days_left = days_until_expiry(cert.valid_to)
            if days_left in ALERT_DAYS:
                subject = f"Certificate Expiry Alert: {cert.id}"
                body = (
                    f"Hello {user.username},\n\n"
                    f"Your certificate '{cert.name}' (ID: {cert.id}) will expire in {days_left} day(s) on {cert.valid_to.date()}.\n"
                    f"Issuer: {cert.issuer}\n"
                    f"Subject: {cert.subject}\n\n"
                    "Please take action to renew or replace it.\n\n"
                    "Best regards,\nCertAlert"
                )
                send_email(user.email, subject, body)
