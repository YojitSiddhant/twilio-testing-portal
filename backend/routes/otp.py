import logging

from fastapi import APIRouter, HTTPException
from twilio.base.exceptions import TwilioRestException

from schemas.otp import OtpResponse, SendOtpRequest, VerifyOtpRequest
from services.twilio_verify import (
    TwilioConfigError,
    check_verification_code,
    send_verification_code,
)

logger = logging.getLogger("otp")

router = APIRouter(prefix="/api/otp", tags=["otp"])


# Common Twilio Verify error codes we want to explain to a learner instead of
# leaking a raw Twilio error message/stack trace to the frontend.
_TWILIO_ERROR_MESSAGES = {
    60200: "Invalid phone number format.",
    60203: "Too many send attempts. Try again later.",
    60202: "Too many incorrect attempts for this verification.",
    20404: "Verification not found or already expired. Request a new OTP.",
    21608: (
        "Trial account restriction: this number is not verified in your "
        "Twilio Console. Verify it under Phone Numbers > Verified Caller IDs."
    ),
    21211: "Invalid 'To' phone number.",
}


def _friendly_twilio_error(exc: TwilioRestException) -> str:
    return _TWILIO_ERROR_MESSAGES.get(exc.code, "Twilio was unable to process this request.")


@router.post("/send", response_model=OtpResponse)
def send_otp(payload: SendOtpRequest):
    # Browser -> FastAPI -> Twilio Verify: ask Twilio to send an SMS OTP.
    try:
        status = send_verification_code(payload.phone_number)
    except TwilioConfigError as exc:
        logger.error("Twilio configuration missing")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except TwilioRestException as exc:
        logger.error("Twilio error on /api/otp/send (code=%s)", exc.code)
        raise HTTPException(status_code=400, detail=_friendly_twilio_error(exc)) from exc

    return OtpResponse(success=True, status=status)


@router.post("/verify", response_model=OtpResponse)
def verify_otp(payload: VerifyOtpRequest):
    # User enters OTP -> FastAPI -> Twilio Verify: check the submitted code.
    try:
        status = check_verification_code(payload.phone_number, payload.code)
    except TwilioConfigError as exc:
        logger.error("Twilio configuration missing")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except TwilioRestException as exc:
        logger.error("Twilio error on /api/otp/verify (code=%s)", exc.code)
        raise HTTPException(status_code=400, detail=_friendly_twilio_error(exc)) from exc

    success = status == "approved"
    return OtpResponse(success=success, status=status)
