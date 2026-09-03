import logging
import uuid

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .deepseek import ask_deepseek
from .gemini import ask_gemini
from .knowledge import SYSTEM_PROMPT, get_reply, is_greeting
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
    if is_greeting(user_message):
        return get_reply(user_message)

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

    return get_reply(user_message)


def get_or_create_conversation(conversation_id):
    if conversation_id:
        try:
            return Conversation.objects.get(pk=uuid.UUID(str(conversation_id)))
        except (Conversation.DoesNotExist, ValueError, TypeError):
            pass
    return Conversation.objects.create()


def serialize_message(message: Message) -> dict:
    return {
        "role": message.role,
        "text": message.text,
        "created_at": message.created_at.isoformat(),
    }


@api_view(["POST"])
def chat(request):
    message = request.data.get("message")

    if not message:
        return Response(
            {"error": "Message is required"},
            status=400
        )

    user_message = str(message)
    conversation = get_or_create_conversation(request.data.get("conversation_id"))
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
    items = []
    for conversation in Conversation.objects.order_by("-created_at")[:30]:
        first = conversation.messages.filter(role=Message.ROLE_USER).first()
        items.append({
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "preview": (first.text[:80] if first else "Empty chat"),
        })
    return Response({"conversations": items})


@api_view(["GET"])
def conversation_detail(request, conversation_id):
    try:
        conversation = Conversation.objects.get(pk=uuid.UUID(str(conversation_id)))
    except (Conversation.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Conversation not found"}, status=404)

    messages = [serialize_message(item) for item in conversation.messages.all()]
    return Response({
        "conversation_id": str(conversation.id),
        "messages": messages,
    })
