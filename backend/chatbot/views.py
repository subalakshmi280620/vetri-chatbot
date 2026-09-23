import logging
import uuid

from django.conf import settings
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from .throttles import ChatRateThrottle

from .deepseek import ask_deepseek
from .gemini import ask_gemini
from .eligibility import handle_eligibility, is_non_eligibility_faq
from .knowledge import SYSTEM_PROMPT, UNVERIFIED, get_reply, get_structured_reply
from .models import Conversation, Message
from .rag import format_context, retrieve

logger = logging.getLogger(__name__)
HISTORY_LIMIT = 12


def build_prompt(user_message: str) -> str:
    context = format_context(retrieve(user_message))
    if not context:
        return SYSTEM_PROMPT
    return f"{SYSTEM_PROMPT}\n\n{context}"


def generate_reply(user_message: str, history=None) -> str:
    # Fee, apply, contact, and similar FAQs should always use verified KB answers.
    if is_non_eligibility_faq(user_message):
        structured = get_structured_reply(user_message)
        if structured:
            return structured

    eligibility = handle_eligibility(user_message, history)
    if eligibility:
        return eligibility

    # Fast path: answer from verified KB before calling any LLM API.
    structured = get_structured_reply(user_message)
    if structured:
        return structured

    kb_reply = get_reply(user_message)
    if kb_reply and kb_reply != UNVERIFIED:
        return kb_reply

    prompt = build_prompt(user_message)
    if settings.DEEPSEEK_API_KEY:
        try:
            return ask_deepseek(user_message, prompt, history)
        except Exception as exc:
            logger.warning("DeepSeek unavailable: %s", exc)

    if settings.GEMINI_API_KEY:
        try:
            return ask_gemini(user_message, prompt, history)
        except Exception as exc:
            logger.warning("Gemini unavailable: %s", exc)

    return kb_reply or get_reply(user_message)


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
        "role": message.role,
        "text": message.text,
        "created_at": message.created_at.isoformat(),
    }


@api_view(["POST"])
@throttle_classes([ChatRateThrottle])
def chat(request):
    message = request.data.get("message")

    if not message:
        return Response(
            {"error": "Message is required"},
            status=400
        )

    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    user_message = str(message)
    max_length = settings.CHAT_MAX_MESSAGE_LENGTH
    if len(user_message) > max_length:
        return Response(
            {
                "error": (
                    f"Message is too long. Maximum length is {max_length} characters."
                ),
            },
            status=400,
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

    reply = generate_reply(user_message, history)
    Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_USER,
        text=user_message,
    )
    Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_BOT,
        text=reply,
    )

    return Response({
        "reply": reply,
        "conversation_id": str(conversation.id),
    })


@api_view(["GET"])
def conversation_list(request):
    client_token = get_client_token_from_request(request)
    if not client_token:
        return Response({"error": "client_token is required."}, status=400)

    items = []
    queryset = Conversation.objects.filter(client_token=client_token).order_by("-created_at")[:30]
    for conversation in queryset:
        first = conversation.messages.filter(role=Message.ROLE_USER).first()
        items.append({
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "preview": (first.text[:80] if first else "Empty chat"),
        })
    return Response({"conversations": items})


@api_view(["GET"])
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

    messages = [serialize_message(item) for item in conversation.messages.all()]
    return Response({
        "conversation_id": str(conversation.id),
        "messages": messages,
    })
