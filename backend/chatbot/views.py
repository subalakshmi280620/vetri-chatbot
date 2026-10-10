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
from .groq import GroqAPIError, ask_groq
from .eligibility import handle_eligibility, is_non_eligibility_faq
from .knowledge import (
    AI_FULLY_UNAVAILABLE_MESSAGE,
    GENERIC_FALLBACK_MARKER,
    apply_reply_style,
    detect_suggested_enquiry_type,
    get_conversational_fallback,
    get_contextual_follow_up_reply,
    get_grounding_facts,
    get_system_prompt,
    is_contextual_follow_up,
    is_greeting,
    infer_reply_style,
    normalize_reply_style,
    resolve_follow_up_query,
)
from .language import LANG_TA, detect_language, normalize_language
from .tamil_replies import get_tamil_ai_unavailable
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


def build_prompt(
    user_message: str,
    history=None,
    reply_style: str = "brief",
    language: str = "en",
) -> str:
    style = normalize_reply_style(reply_style)
    query = resolve_follow_up_query(user_message, history)
    length_hint = (
        "1–2 short sentences"
        if style == "brief"
        else "2–4 short lines"
    )
    parts = [get_system_prompt(style), get_verified_facts_prompt(style, language)]
    context = format_context(retrieve(query, limit=settings.GEMINI_RAG_LIMIT))
    if context:
        parts.append(context)
    grounding = get_grounding_facts(query)
    if grounding:
        parts.append(
            "Facts for this reply (do not copy verbatim — rewrite in your own warm, "
            f"conversational words; complete sentences; {length_hint}):\n"
            f"{grounding}"
        )
    return "\n\n".join(parts)


def build_compact_prompt(
    user_message: str,
    history=None,
    reply_style: str = "brief",
    language: str = "en",
) -> str:
    """Smaller prompt for a last-chance Gemini retry after rate-limit errors."""
    style = normalize_reply_style(reply_style)
    query = resolve_follow_up_query(user_message, history)
    sentence_hint = "1–2 complete sentences" if style == "brief" else "2–4 complete sentences"
    parts = [
        (
            f"You are Coach AI for Vetri IT Systems (VIS). Reply warmly in {sentence_hint}. "
            "Use only verified facts below — never invent pricing."
        ),
        get_verified_facts_prompt(style, language),
    ]
    grounding = get_grounding_facts(query)
    if grounding:
        parts.append(grounding)
    return "\n\n".join(parts)


def _try_groq_reply(user_message: str, prompt: str, history=None) -> str | None:
    if not settings.GROQ_API_KEY:
        return None

    try:
        reply = ask_groq(user_message, prompt, history)
        logger.info(
            "AI provider success: groq fallback model=%s",
            settings.GROQ_MODEL,
        )
        return reply
    except GroqAPIError as exc:
        logger.warning(
            "AI provider error: groq fallback HTTP=%s",
            exc.code or "unknown",
        )
        return None
    except Exception as exc:
        detail = str(exc).replace(settings.GROQ_API_KEY, "***")[:240]
        logger.warning(
            "AI provider error: groq fallback %s",
            detail or type(exc).__name__,
        )
        return None


def _try_deepseek_reply(user_message: str, prompt: str, history=None) -> str | None:
    if not settings.DEEPSEEK_API_KEY:
        return None
    try:
        reply = ask_deepseek(user_message, prompt, history)
        logger.info(
            "AI provider success: deepseek fallback model=%s",
            settings.DEEPSEEK_MODEL,
        )
        return reply
    except Exception as exc:
        # Log safe detail (HTTP code/message) — never log API keys.
        detail = str(exc).replace(settings.DEEPSEEK_API_KEY, "***")[:240]
        logger.warning(
            "AI provider error: deepseek fallback %s",
            detail or type(exc).__name__,
        )
        return None


def _ai_providers_configured() -> bool:
    return bool(
        settings.AI_ENABLED
        and (
            settings.GEMINI_API_KEY
            or settings.GROQ_API_KEY
            or settings.DEEPSEEK_API_KEY
        )
    )


def _try_ai_reply(
    user_message: str,
    history=None,
    attachments=None,
    reply_style: str = "brief",
    language: str = "en",
) -> str | None:
    """Gemini first; Groq and then DeepSeek are text-chat fallbacks."""
    if not settings.AI_ENABLED:
        return None
    if not (
    settings.GROQ_API_KEY
    or settings.DEEPSEEK_API_KEY
    or settings.GEMINI_API_KEY
):
        return None

    prompt = build_prompt(user_message, history, reply_style, language)
    images = attachments.images if attachments else None

    if settings.GEMINI_API_KEY:
        try:
            reply = ask_gemini(user_message, prompt, history, images=images)
            logger.info("AI provider success: gemini")
            return reply
        except GeminiAPIError as exc:
            logger.warning(
                "AI provider error: gemini model=%s HTTP=%s — trying fallbacks",
                exc.model or "unknown",
                exc.code or "unknown",
            )
        except Exception as exc:
            logger.warning(
                "AI provider error: gemini %s — trying fallbacks",
                type(exc).__name__,
            )

    # Backup AI for text chat when Gemini is down (503, 429, timeout, etc.)
    if not images:
        groq_reply = _try_groq_reply(user_message, prompt, history)
    if groq_reply:
        return groq_reply
        return _try_deepseek_reply(user_message, prompt, history)

    return None


def _kb_fallback_reply(
    user_message: str,
    ai_was_attempted: bool,
    reply_style: str = "brief",
    language: str = "en",
    history=None,
) -> tuple[str, str]:
    """Verified KB fallback when AI is unavailable."""
    fallback = get_conversational_fallback(
        user_message, reply_style, language, history=history
    )
    if not ai_was_attempted:
        return fallback, SOURCE_VERIFIED_KB
    if GENERIC_FALLBACK_MARKER in fallback:
        if normalize_language(language) == LANG_TA:
            return get_tamil_ai_unavailable(), SOURCE_UNVERIFIED
        return AI_FULLY_UNAVAILABLE_MESSAGE, SOURCE_UNVERIFIED
    # Specific verified answer — read naturally; UI source badge shows verified_kb.
    return fallback, SOURCE_VERIFIED_KB


def generate_reply(
    user_message: str,
    history=None,
    attachments=None,
    reply_style: str | None = None,
    language: str | None = None,
) -> tuple[str, str]:
    from .knowledge import get_greeting_reply

    style = normalize_reply_style(reply_style or infer_reply_style(user_message, history))
    lang = normalize_language(language or detect_language(user_message, history))

    if user_message and is_greeting(user_message) and not (attachments and (attachments.images or attachments.document_text)):
        return apply_reply_style(get_greeting_reply(lang), style), SOURCE_AI

    if (
        user_message
        and is_contextual_follow_up(user_message)
        and not (attachments and (attachments.images or attachments.document_text))
    ):
        contextual = get_contextual_follow_up_reply(user_message, history, style, lang)
        if contextual:
            return apply_reply_style(contextual, style), SOURCE_VERIFIED_KB

    ai_configured = _ai_providers_configured()
    ai_reply = _try_ai_reply(user_message, history, attachments, style, lang)
    if ai_reply:
        return apply_reply_style(enforce_verified_facts(ai_reply.strip()), style), SOURCE_AI

    if attachments and (attachments.images or attachments.document_text):
        names = ", ".join(attachments.display_labels) or "your file"
        return (
            f"I received {names}, but I could not analyse it right now. "
            f"Please try again shortly or email support@vetri-it.com."
        ), SOURCE_UNVERIFIED

    if not is_non_eligibility_faq(user_message):
        eligibility = handle_eligibility(user_message, history, lang)
        if eligibility:
            return apply_reply_style(eligibility, style), SOURCE_ELIGIBILITY

    reply, source = _kb_fallback_reply(
        user_message,
        ai_was_attempted=ai_configured,
        reply_style=style,
        language=lang,
        history=history,
    )
    return apply_reply_style(reply, style), source


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

    reply_style = infer_reply_style(user_message, history)
    language = detect_language(user_message, history)

    try:
        reply, source = generate_reply(
            prompt_message,
            history,
            processed_attachments,
            reply_style,
            language,
        )
    except Exception as exc:
        logger.exception("generate_reply failed: %s", type(exc).__name__)
        reply, source = _kb_fallback_reply(
            prompt_message,
            ai_was_attempted=_ai_providers_configured(),
            reply_style=reply_style,
            language=language,
        )
    suggestions = get_follow_up_suggestions(prompt_message, reply, source)
    suggest_enquiry = detect_suggested_enquiry_type(user_message, history)

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
    Enquiry.TYPE_ENROLL: (
        "Enrollment request received\n\n"
        "Thank you. Our team will use the details you shared and contact you "
        "about the course, website, product, or service you chose.\n\n"
        "You do not need to sign in on the website."
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
    if enquiry_type == Enquiry.TYPE_ENROLL and not interest:
        return Response(
            {"error": "Please select a course, website, product, or service to enroll."},
            status=400,
        )
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
