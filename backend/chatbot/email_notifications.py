import logging
import threading

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

RESEND_TEST_FROM = "Coach AI <onboarding@resend.dev>"


def dispatch_enquiry_notification(enquiry) -> None:
    """Send enquiry email in a background thread so the API responds immediately."""
    thread = threading.Thread(
        target=send_enquiry_notification,
        args=(enquiry,),
        daemon=True,
    )
    thread.start()


def _interest_label(enquiry) -> str:
    labels = {
        "quotation": "Product / service for quotation",
        "consultation": "Consultation topic",
        "demo": "Product to demo",
        "sales": "Sales interest",
        "general": "Interest",
    }
    return labels.get(enquiry.enquiry_type, "Interest")


def _build_enquiry_email(enquiry) -> tuple[str, str]:
    subject = f"Coach AI enquiry — {enquiry.get_enquiry_type_display()}"
    interest_label = _interest_label(enquiry)
    body = (
        f"A new Coach AI enquiry was submitted.\n\n"
        f"Type: {enquiry.get_enquiry_type_display()}\n"
        f"Name: {enquiry.full_name}\n"
        f"Company: {enquiry.company or '—'}\n"
        f"Email: {enquiry.email}\n"
        f"Phone: {enquiry.phone or '—'}\n"
        f"{interest_label}: {enquiry.interest or '—'}\n\n"
        f"Details:\n{enquiry.message}\n\n"
        f"Enquiry ID: {enquiry.id}\n"
        f"Submitted: {enquiry.created_at:%Y-%m-%d %H:%M UTC}\n"
    )
    return subject, body


def _resend_from_address() -> str:
    configured = getattr(settings, "RESEND_FROM_EMAIL", "").strip()
    return configured or RESEND_TEST_FROM


def _using_resend_test_domain(from_email: str) -> bool:
    return "resend.dev" in from_email.lower()


def _send_via_resend(recipient: str, subject: str, body: str) -> bool:
    api_key = getattr(settings, "RESEND_API_KEY", "").strip()
    if not api_key:
        logger.warning("RESEND_API_KEY is not set — enquiry email skipped.")
        return False

    from_email = _resend_from_address()
    if _using_resend_test_domain(from_email):
        logger.info(
            "Resend test mode: sending enquiry notification to %s "
            "(onboarding@resend.dev only delivers to your Resend account email).",
            recipient,
        )

    try:
        import resend
        from resend.exceptions import ResendError

        resend.api_key = api_key
        result = resend.Emails.send({
            "from": from_email,
            "to": [recipient],
            "subject": subject,
            "text": body,
        })
        message_id = result.get("id") if isinstance(result, dict) else result
        logger.info("Resend enquiry email sent to %s (id=%s)", recipient, message_id)
        return True
    except ResendError as exc:
        logger.warning(
            "Resend enquiry email failed to %s from %s: %s. "
            "If using onboarding@resend.dev, set ENQUIRY_NOTIFY_EMAIL to the "
            "exact email you used to sign up for Resend.",
            recipient,
            from_email,
            exc,
        )
        return False
    except Exception as exc:
        logger.warning("Resend enquiry email failed to %s: %s", recipient, exc)
        return False


def send_enquiry_notification(enquiry) -> bool:
    """Email VIS when a new enquiry is submitted. Returns True if sent."""
    recipient = getattr(settings, "ENQUIRY_NOTIFY_EMAIL", "").strip()
    if not recipient:
        logger.warning("ENQUIRY_NOTIFY_EMAIL is not set — enquiry email skipped.")
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
