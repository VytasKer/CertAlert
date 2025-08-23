# backend/app/test_email.py

from app.notifications import send_email

# Replace with your test recipient email
to_email = "vytaske11@gmail.com"
subject = "Test Email from CertAlert"
body = "This is a test email from your CertAlert backend."

send_email(to_email, subject, body)
print("Email sent!")