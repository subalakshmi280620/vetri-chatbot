import json
import logging
import threading
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def dispatch_enquiry_notification(enquiry) -> None:
    """Send enquiry email in a background thread so the API responds immediately."""
    thread = threading.Thread(
        target=send_enquiry_notification,
        args=(enquiry,),
        daemon=True,
    )
    thread.start()


def _build_enquiry_email(enquiry) -> tuple[str, str]:
    subject = f"Coach AI enquiry — {enquiry.get_enquiry_type_display()}"
    body = (
        f"A new Coach AI enquiry was submitted.\n\n"
        f"Type: {enquiry.get_enquiry_type_display()}\n"
        f"Name: {enquiry.full_name}\n"
        f"Company: {enquiry.company or '—'}\n"
        f"Email: {enquiry.email}\n"
        f"Phone: {enquiry.phone or '—'}\n"
        f"Interest: {enquiry.interest or '—'}\n\n"
        f"Message:\n{enquiry.message}\n\n"
        f"Enquiry ID: {enquiry.id}\n"
        f"Submitted: {enquiry.created_at:%Y-%m-%d %H:%M UTC}\n"
    )
    return subject, body


def _send_via_resend(recipient: str, subject: str, body: str) -> bool:
    api_key = getattr(settings, "RESEND_API_KEY", "").strip()
    if not api_key:
        return False

    from_email = (
        getattr(settings, "RESEND_FROM_EMAIL", "").strip()
        or settings.DEFAULT_FROM_EMAIL
    )
    payload = json.dumps({
        "from": from_email,
        "to": [recipient],
        "subject": subject,
        "text": body,
    }).encode("utf-8")
    request = urllib.request.Request(
        RESEND_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return 200 <= response.status < 300
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        logger.warning("Resend enquiry email failed (%s): %s", exc.code, detail)
        return False
    except Exception as exc:
        logger.warning("Resend enquiry email failed: %s", exc)
        return False


def send_enquiry_notification(enquiry) -> bool:
    """Email VIS when a new enquiry is submitted. Returns True if sent."""
    recipient = getattr(settings, "ENQUIRY_NOTIFY_EMAIL", "").strip()
    if not recipient:
        return False

    subject, body = _build_enquiry_email(enquiry)

    if getattr(settings, "RESEND_API_KEY", "").strip():
        return _send_via_resend(recipient, subject, body)

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.warning("Enquiry notification email failed: %s", exc)
        return False
