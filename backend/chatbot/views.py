import logging
import uuid

from django.conf import settings
from django.db.models import Count, Max, Q
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from .attachments import build_user_message_with_attachments, parse_attachments
from .throttles import ChatRateThrottle

from .deepseek import ask_deepseek
from .gemini import GeminiAPIError, ask_gemini
from .grok import GrokAPIError, ask_grok
from .eligibility import handle_eligibility, is_non_eligibility_faq
from .knowledge import (
    AI_FULLY_UNAVAILABLE_MESSAGE,
    GENERIC_FALLBACK_MARKER,
    SHORT_GREETING_REPLY,
    SYSTEM_PROMPT,
    detect_suggested_enquiry_type,
    get_conversational_fallback,
    get_grounding_facts,
    is_greeting,
)
from .verified_facts import enforce_verified_facts, get_verified_facts_prompt
from .email_notifications import dispatch_enquiry_notification
from .models import Conversation, Enquiry, Message
from .rag import format_context, retrieve
from .suggestions import get_follow_up_suggestions

SOURCE_VERIFIED_KB = "verified_kb"
SOURCE_ELIGIBILITY = "eligibility"
SOURCE_AI = "ai"
SOURCE_UNVERIFIED = "unverified"

logger = logging.getLogger(__name__)
HISTORY_LIMIT = 12


def build_prompt(user_message: str) -> str:
    parts = [SYSTEM_PROMPT, get_verified_facts_prompt()]
    context = format_context(retrieve(user_message, limit=settings.GEMINI_RAG_LIMIT))
    if context:
        parts.append(context)
    grounding = get_grounding_facts(user_message)
    if grounding:
        parts.append(
            "Facts for this reply (do not copy verbatim — rewrite in your own warm, "
            "conversational words; complete sentences; 2–4 short lines):\n"
            f"{grounding}"
        )
    return "\n\n".join(parts)


def build_compact_prompt(user_message: str) -> str:
    """Smaller prompt for a last-chance Gemini retry after rate-limit errors."""
    parts = [
        (
            "You are Coach AI for Vetri IT Systems (VIS). Reply warmly in 2–4 complete "
            "sentences. Use only verified facts below — never invent pricing."
        ),
        get_verified_facts_prompt(),
    ]
    grounding = get_grounding_facts(user_message)
    if grounding:
        parts.append(grounding)
    return "\n\n".join(parts)


def _try_grok_reply(user_message: str, prompt: str, history=None) -> str | None:
    if not settings.XAI_API_KEY:
        return None
    try:
        return ask_grok(user_message, prompt, history)
    except GrokAPIError as exc:
        logger.warning(
            "Grok fallback unavailable: HTTP=%s",
            exc.code or "unknown",
        )
        return None
    except Exception as exc:
        detail = str(exc).replace(settings.XAI_API_KEY, "***")[:240]
        logger.warning("Grok fallback unavailable: %s", detail or type(exc).__name__)
        return None


def _try_deepseek_reply(user_message: str, prompt: str, history=None) -> str | None:
    if not settings.DEEPSEEK_API_KEY:
        return None
    try:
        return ask_deepseek(user_message, prompt, history)
    except Exception as exc:
        # Log safe detail (HTTP code/message) — never log API keys.
        detail = str(exc).replace(settings.DEEPSEEK_API_KEY, "***")[:240]
        logger.warning("DeepSeek fallback unavailable: %s", detail or type(exc).__name__)
        return None


def _ai_providers_configured() -> bool:
    return bool(
        settings.AI_ENABLED
        and (settings.GEMINI_API_KEY or settings.XAI_API_KEY or settings.DEEPSEEK_API_KEY)
    )


def _try_ai_reply(user_message: str, history=None, attachments=None) -> str | None:
    """Gemini first (images + primary). Grok, then DeepSeek, when Gemini fails."""
    if not settings.AI_ENABLED:
        return None
    if not (settings.XAI_API_KEY or settings.DEEPSEEK_API_KEY or settings.GEMINI_API_KEY):
        return None

    prompt = build_prompt(user_message)
    images = attachments.images if attachments else None

    if settings.GEMINI_API_KEY:
        try:
            return ask_gemini(user_message, prompt, history, images=images)
        except GeminiAPIError as exc:
            logger.warning(
                "Gemini unavailable: model=%s HTTP=%s — trying fallbacks",
                exc.model or "unknown",
                exc.code or "unknown",
            )
        except Exception as exc:
            logger.warning(
                "Gemini unavailable: %s — trying Grok/DeepSeek fallbacks",
                type(exc).__name__,
            )

    # Backup AI for text chat when Gemini is down (503, 429, timeout, etc.)
    if not images:
        grok_reply = _try_grok_reply(user_message, prompt, history)
        if grok_reply:
            return grok_reply
        return _try_deepseek_reply(user_message, prompt, history)

    return None


def _kb_fallback_reply(user_message: str, ai_was_attempted: bool) -> tuple[str, str]:
    """Verified KB fallback when AI is unavailable."""
    fallback = get_conversational_fallback(user_message)
    if not ai_was_attempted:
        return fallback, SOURCE_VERIFIED_KB
    if GENERIC_FALLBACK_MARKER in fallback:
        return AI_FULLY_UNAVAILABLE_MESSAGE, SOURCE_UNVERIFIED
    # Specific verified answer — read naturally; UI source badge shows verified_kb.
    return fallback, SOURCE_VERIFIED_KB


def generate_reply(
    user_message: str,
    history=None,
    attachments=None,
) -> tuple[str, str]:
    if user_message and is_greeting(user_message) and not (attachments and (attachments.images or attachments.document_text)):
        return SHORT_GREETING_REPLY, SOURCE_AI

    ai_configured = _ai_providers_configured()
    ai_reply = _try_ai_reply(user_message, history, attachments)
    if ai_reply:
        return enforce_verified_facts(ai_reply.strip()), SOURCE_AI

    if attachments and (attachments.images or attachments.document_text):
        names = ", ".join(attachments.display_labels) or "your file"
        return (
            f"I received {names}, but I could not analyse it right now. "
            f"Please try again shortly or email support@vetri-it.com."
        ), SOURCE_UNVERIFIED

    if not is_non_eligibility_faq(user_message):
        eligibility = handle_eligibility(user_message, history)
        if eligibility:
            return eligibility, SOURCE_ELIGIBILITY

    return _kb_fallback_reply(user_message, ai_was_attempted=ai_configured)


def parse_client_token(value):
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def get_client_token_from_request(request):
    if request.method == "POST":
        return parse_client_token(request.data.get("client_token"))
    return parse_client_token(request.query_params.get("client_token"))


def resolve_conversation(conversation_id, client_token):
    if conversation_id:
        try:
            conversation = Conversation.objects.get(pk=uuid.UUID(str(conversation_id)))
        except (Conversation.DoesNotExist, ValueError, TypeError):
            return Conversation.objects.create(client_token=client_token)
        if conversation.client_token != client_token:
            return None
        return conversation
    return Conversation.objects.create(client_token=client_token)


def serialize_message(message: Message) -> dict:
    return {
        "id": message.id,
        "role": message.role,
        "text": message.text,
        "source": message.source or "",
        "feedback": message.feedback or "",
        "created_at": message.created_at.isoformat(),
    }


@api_view(["POST"])
@throttle_classes([ChatRateThrottle])
def chat(request):
    message = request.data.get("message", "")
    raw_attachments = request.data.get("attachments") or []

    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    user_message = str(message).strip()
    if not user_message and not raw_attachments:
        return Response({"error": "Message or attachment is required"}, status=400)

    max_length = settings.CHAT_MAX_MESSAGE_LENGTH
    if user_message and len(user_message) > max_length:
        return Response(
            {
                "error": (
                    f"Message is too long. Maximum length is {max_length} characters."
                ),
            },
            status=400,
        )

    try:
        processed_attachments = parse_attachments(
            raw_attachments,
            max_count=settings.CHAT_MAX_ATTACHMENTS,
            max_bytes=settings.CHAT_MAX_ATTACHMENT_BYTES,
            max_document_chars=settings.CHAT_MAX_DOCUMENT_CHARS,
        )
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)

    prompt_message = build_user_message_with_attachments(
        user_message,
        processed_attachments,
    )

    conversation = resolve_conversation(
        request.data.get("conversation_id"),
        client_token,
    )
    if conversation is None:
        return Response(
            {"error": "You do not have access to this conversation."},
            status=403,
        )
    history = list(
        conversation.messages.order_by("-created_at")[:HISTORY_LIMIT]
        .values("role", "text")
    )
    history.reverse()

    try:
        reply, source = generate_reply(prompt_message, history, processed_attachments)
    except Exception as exc:
        logger.exception("generate_reply failed: %s", type(exc).__name__)
        reply, source = _kb_fallback_reply(
            prompt_message,
            ai_was_attempted=_ai_providers_configured(),
        )
    suggestions = get_follow_up_suggestions(prompt_message, reply, source)
    suggest_enquiry = detect_suggested_enquiry_type(user_message)

    stored_user_text = user_message or "Shared attachment(s)"
    if processed_attachments.display_labels:
        labels = ", ".join(processed_attachments.display_labels)
        stored_user_text = f"{stored_user_text}\n[Attached: {labels}]".strip()

    Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_USER,
        text=stored_user_text,
    )
    bot_message = Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_BOT,
        text=reply,
        source=source,
    )

    return Response({
        "reply": reply,
        "conversation_id": str(conversation.id),
        "message_id": bot_message.id,
        "source": source,
        "suggestions": suggestions,
        "suggest_enquiry": suggest_enquiry,
    })


@api_view(["GET"])
def conversation_list(request):
    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    items = []
    queryset = (
        Conversation.objects.filter(client_token=client_token)
        .annotate(
            last_message_at=Max("messages__created_at"),
            message_count=Count("messages"),
            question_count=Count(
                "messages",
                filter=Q(messages__role=Message.ROLE_USER),
            ),
        )
        .filter(question_count__gt=0)
        .order_by("-last_message_at", "-created_at")[:30]
    )
    for conversation in queryset:
        latest_user = (
            conversation.messages.filter(role=Message.ROLE_USER)
            .order_by("-created_at")
            .first()
        )
        first_user = (
            conversation.messages.filter(role=Message.ROLE_USER)
            .order_by("created_at")
            .first()
        )
        latest_text = latest_user.text[:80] if latest_user else "New chat"
        first_text = first_user.text[:80] if first_user else ""
        items.append({
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": (
                conversation.last_message_at.isoformat()
                if conversation.last_message_at
                else conversation.created_at.isoformat()
            ),
            "title": latest_text,
            "preview": latest_text,
            "first_question": first_text,
            "message_count": conversation.message_count,
            "question_count": conversation.question_count,
        })
    return Response({"conversations": items})


@api_view(["GET", "DELETE"])
def conversation_detail(request, conversation_id):
    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    try:
        conversation = Conversation.objects.get(pk=uuid.UUID(str(conversation_id)))
    except (Conversation.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Conversation not found"}, status=404)

    if conversation.client_token != client_token:
        return Response(
            {"error": "You do not have access to this conversation."},
            status=403,
        )

    if request.method == "DELETE":
        conversation.delete()
        return Response(status=204)

    messages = [serialize_message(item) for item in conversation.messages.all()]
    return Response({
        "conversation_id": str(conversation.id),
        "messages": messages,
    })


@api_view(["POST"])
def message_feedback(request):
    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    message_id = request.data.get("message_id")
    rating = str(request.data.get("rating", "")).lower()
    if rating not in {"up", "down"}:
        return Response({"error": "rating must be 'up' or 'down'."}, status=400)

    try:
        message = Message.objects.select_related("conversation").get(pk=message_id)
    except (Message.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Message not found"}, status=404)

    if message.role != Message.ROLE_BOT:
        return Response({"error": "Only assistant messages can be rated."}, status=400)

    if message.conversation.client_token != client_token:
        return Response(
            {"error": "You do not have access to this conversation."},
            status=403,
        )

    message.feedback = rating
    message.save(update_fields=["feedback"])
    return Response({"status": "ok", "feedback": rating})


ENQUIRY_CONFIRMATIONS = {
    Enquiry.TYPE_QUOTATION: (
        "Enquiry Submitted — Get Quotation\n\n"
        "Thank you. Our team will review your requirement and share a tailored "
        "proposal with scope, timeline, and indicative pricing.\n\n"
        "We will contact you at the email or phone you provided."
    ),
    Enquiry.TYPE_CONSULTATION: (
        "Enquiry Submitted — Book a Consultation\n\n"
        "Thank you. A VIS solution consultant will reach out to discuss your "
        "goals and recommend the right next steps.\n\n"
        "We will contact you at the email or phone you provided."
    ),
    Enquiry.TYPE_DEMO: (
        "Enquiry Submitted — Product Demo\n\n"
        "Thank you. Our team will arrange a guided demo for the product or "
        "service you selected.\n\n"
        "We will contact you at the email or phone you provided."
    ),
    Enquiry.TYPE_SALES: (
        "Enquiry Submitted — Sales Team\n\n"
        "Thank you. Our sales team will contact you about your requirement."
    ),
    Enquiry.TYPE_GENERAL: (
        "Enquiry Submitted\n\n"
        "Thank you. The VIS team will review your message and get back to you soon."
    ),
}


def _normalize_enquiry_type(value: str) -> str:
    allowed = {choice[0] for choice in Enquiry.TYPE_CHOICES}
    cleaned = str(value or Enquiry.TYPE_GENERAL).strip().lower()
    return cleaned if cleaned in allowed else Enquiry.TYPE_GENERAL


@api_view(["POST"])
@throttle_classes([ChatRateThrottle])
def submit_enquiry(request):
    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    full_name = str(request.data.get("full_name", "")).strip()
    company = str(request.data.get("company", "")).strip()
    email = str(request.data.get("email", "")).strip()
    phone = str(request.data.get("phone", "")).strip()
    interest = str(request.data.get("interest", "")).strip()
    message = str(request.data.get("message", "")).strip()
    enquiry_type = _normalize_enquiry_type(request.data.get("enquiry_type"))

    if not full_name:
        return Response({"error": "full_name is required."}, status=400)
    if not email:
        return Response({"error": "email is required."}, status=400)
    if not message:
        return Response({"error": "message is required."}, status=400)
    if enquiry_type == Enquiry.TYPE_DEMO and not interest:
        return Response({"error": "Please select a product to demo."}, status=400)
    if enquiry_type == Enquiry.TYPE_QUOTATION and not interest:
        return Response(
            {"error": "Please select a product or service for your quotation."},
            status=400,
        )
    if len(full_name) > 120 or len(company) > 120 or len(phone) > 30 or len(interest) > 120:
        return Response({"error": "One or more fields are too long."}, status=400)
    if len(message) > 2000:
        return Response({"error": "message must be 2000 characters or fewer."}, status=400)

    conversation = None
    conversation_id = request.data.get("conversation_id")
    if conversation_id:
        conversation = resolve_conversation(conversation_id, client_token)
        if conversation is None:
            return Response(
                {"error": "You do not have access to this conversation."},
                status=403,
            )

    enquiry = Enquiry.objects.create(
        enquiry_type=enquiry_type,
        full_name=full_name,
        company=company,
        email=email,
        phone=phone,
        interest=interest,
        message=message,
        client_token=client_token,
        conversation=conversation,
    )
    dispatch_enquiry_notification(enquiry)

    confirmation = ENQUIRY_CONFIRMATIONS.get(
        enquiry_type,
        ENQUIRY_CONFIRMATIONS[Enquiry.TYPE_GENERAL],
    )
    return Response({
        "status": "ok",
        "enquiry_id": enquiry.id,
        "enquiry_type": enquiry_type,
        "confirmation": confirmation,
        "email_queued": True,
    })
