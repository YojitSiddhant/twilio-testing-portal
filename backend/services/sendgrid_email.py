"""
SendGrid email service.

Responsible only for talking to SendGrid's Mail Send API to deliver a test
email. The API key and sender address never leave this module; the frontend
only ever talks to our own FastAPI backend.
"""

import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridConfigError(Exception):
    """Raised when required SendGrid environment variables are missing."""


def _get_client() -> tuple[SendGridAPIClient, str]:
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")

    if not api_key or not from_email:
        raise SendGridConfigError(
            "SendGrid is not configured. Set SENDGRID_API_KEY and "
            "SENDGRID_FROM_EMAIL in backend/.env."
        )

    return SendGridAPIClient(api_key), from_email


def send_email(recipient_email: str, subject: str, message: str) -> int:
    """Browser -> FastAPI -> SendGrid: send a plain-text test email.

    Returns the HTTP status code SendGrid's API responded with.
    """
    client, from_email = _get_client()
    mail = Mail(
        from_email=from_email,
        to_emails=recipient_email,
        subject=subject,
        plain_text_content=message,
    )
    response = client.send(mail)
    return response.status_code
