import re

from pydantic import BaseModel, field_validator

# Lightweight email shape check. Good enough to catch obviously malformed
# input without adding an extra dependency (pydantic's EmailStr needs the
# separate email-validator package, which this project doesn't otherwise use).
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SendEmailRequest(BaseModel):
    recipient_email: str
    subject: str
    message: str

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, value: str) -> str:
        value = value.strip()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("recipient_email must be a valid email address")
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("subject is required")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message is required")
        return value


class EmailResponse(BaseModel):
    success: bool
    status_code: int
