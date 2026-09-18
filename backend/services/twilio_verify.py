"""
Twilio Verify service.

Responsible only for talking to Twilio Verify — sending an OTP (via SMS or
WhatsApp) and checking a code the user submits. Twilio manages code
generation, storage and expiry; we never generate, store, or see the "real"
OTP value.
"""

import os

from twilio.rest import Client


class TwilioConfigError(Exception):
    """Raised when required Twilio environment variables are missing."""


def _get_client() -> tuple[Client, str]:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")

    if not account_sid or not auth_token or not verify_service_sid:
        raise TwilioConfigError(
            "Twilio is not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN "
            "and TWILIO_VERIFY_SERVICE_SID in backend/.env."
        )

    return Client(account_sid, auth_token), verify_service_sid


def send_verification_code(phone_number: str, channel: str = "sms") -> str:
    """Browser -> FastAPI -> Twilio Verify: request an OTP for phone_number.

    `channel` is passed straight through to Twilio Verify ("sms" or
    "whatsapp") using the same Verify Service.
    """
    client, verify_service_sid = _get_client()
    verification = client.verify.v2.services(verify_service_sid).verifications.create(
        to=phone_number, channel=channel
    )
    return verification.status


def check_verification_code(phone_number: str, code: str) -> str:
    """FastAPI -> Twilio Verify: check whether `code` is valid for phone_number."""
    client, verify_service_sid = _get_client()
    check = client.verify.v2.services(verify_service_sid).verification_checks.create(
        to=phone_number, code=code
    )
    return check.status
