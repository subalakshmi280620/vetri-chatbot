import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_enquiry_notification(enquiry) -> bool:
    """Email VIS when a new enquiry is submitted. Returns True if sent."""
    recipient = getattr(settings, "ENQUIRY_NOTIFY_EMAIL", "").strip()
    if not recipient:
        return False

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
