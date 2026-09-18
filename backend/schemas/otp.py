import re
from typing import Literal

from pydantic import BaseModel, field_validator

# E.164: + followed by 8-15 digits, first digit non-zero.
E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


class SendOtpRequest(BaseModel):
    phone_number: str
    channel: Literal["sms", "whatsapp"] = "sms"

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not E164_PATTERN.match(value):
            raise ValueError(
                "phone_number must be in E.164 format, e.g. +919876543210"
            )
        return value


class VerifyOtpRequest(BaseModel):
    phone_number: str
    code: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not E164_PATTERN.match(value):
            raise ValueError(
                "phone_number must be in E.164 format, e.g. +919876543210"
            )
        return value

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("code is required")
        return value


class OtpResponse(BaseModel):
    success: bool
    status: str
