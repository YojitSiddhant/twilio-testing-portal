import logging

from fastapi import APIRouter, HTTPException
from python_http_client.exceptions import HTTPError

from schemas.email import EmailResponse, SendEmailRequest
from services.sendgrid_email import SendGridConfigError, send_email

logger = logging.getLogger("email")

router = APIRouter(prefix="/api/email", tags=["email"])


def _friendly_sendgrid_error(exc: HTTPError) -> str:
    body_text = ""
    try:
        body_text = exc.body.decode("utf-8") if isinstance(exc.body, bytes) else str(exc.body or "")
    except (UnicodeDecodeError, AttributeError):
        body_text = ""

    if "verified Sender Identity" in body_text:
        return (
            "SendGrid rejected this request: the 'from' address is not a "
            "verified Sender Identity. Verify it in the SendGrid Console "
            "under Settings > Sender Authentication before sending."
        )

    if exc.status_code == 401:
        return "SendGrid rejected the API key. Check SENDGRID_API_KEY in backend/.env."
    if exc.status_code == 403:
        return (
            "SendGrid forbade this request — likely an unverified sender "
            "identity or an API key without mail-send permission."
        )
    if exc.status_code == 429:
        return "SendGrid rate limit exceeded. Try again shortly."

    return "SendGrid was unable to process this request."


@router.post("/send", response_model=EmailResponse)
def send_email_route(payload: SendEmailRequest):
    # Browser -> FastAPI -> SendGrid: send a plain-text test email.
    try:
        status_code = send_email(payload.recipient_email, payload.subject, payload.message)
    except SendGridConfigError as exc:
        logger.error("SendGrid configuration missing")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except HTTPError as exc:
        logger.error("SendGrid error on /api/email/send (status=%s)", exc.status_code)
        raise HTTPException(status_code=400, detail=_friendly_sendgrid_error(exc)) from exc

    return EmailResponse(success=True, status_code=status_code)
