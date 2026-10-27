"""Contextual follow-up question suggestions for Coach AI."""

DEFAULT_SUGGESTIONS = (
    "What products does VIS offer?",
    "What services does VIS provide?",
    "How can I get a quotation?",
)

TOPIC_SUGGESTIONS = {
    "products": (
        "Tell me about Vetri Bills",
        "What services does VIS provide?",
        "How can I get a quotation?",
    ),
    "services": (
        "What products does VIS offer?",
        "Tell me about AI Solutions",
        "How can I contact the VIS team?",
    ),
    "portfolio": (
        "What products does VIS offer?",
        "What is your mission and vision?",
        "How can I get a quotation?",
    ),
    "about": (
        "What products does VIS offer?",
        "What services does VIS provide?",
        "Why should I choose VIS?",
    ),
    "quotation": (
        "I want to book a consultation",
        "I want to request a product demo",
        "What products does VIS offer?",
    ),
    "consultation": (
        "How can I get a quotation?",
        "I want to request a product demo",
        "How can I contact the VIS team?",
    ),
    "demo": (
        "What products does VIS offer?",
        "How can I get a quotation?",
        "I want to book a consultation",
    ),
    "contact": (
        "What products does VIS offer?",
        "What services does VIS provide?",
        "How can I get a quotation?",
    ),
   
    "ai_solutions": (
        "What products does VIS offer?",
        "What services does VIS provide?",
        "How can I get a quotation?",
    ),
    "vision": (
        "Why should I choose VIS?",
        "What products does VIS offer?",
        "How can I contact the VIS team?",
    ),
}



def _detect_topic(user_message: str, reply: str) -> str:
    combined = f"{user_message}\n{reply}".lower()

    if "book a consultation" in combined:
        return "consultation"
    if "request a product demo" in combined or "product demo" in combined:
        return "demo"
    if "get quotation" in combined or "pricing & quotation" in combined:
        return "quotation"
    if "mission & vision" in combined or "our vision" in combined:
        return "vision"
    if "ai solutions" in combined or "data → context" in combined:
        return "ai_solutions"
    if "contact" in combined and (
        "support@vetri-it.com" in combined or "+91" in combined
    ):
        return "contact"
    if "our products" in combined or "vetri bills" in combined:
        return "products"
    if "our services" in combined or "end-to-end capability" in combined:
        return "services"
    if "portfolio" in combined:
        return "portfolio"
    if any(phrase in combined for phrase in ("about vetri", "about vis", "about us")):
        return "about"

    return ""



def get_follow_up_suggestions(user_message: str, reply: str, source: str) -> list[str]:
    topic = _detect_topic(user_message, reply)
    suggestions = list(TOPIC_SUGGESTIONS.get(topic, DEFAULT_SUGGESTIONS))

    asked = user_message.strip().lower()
    return [item for item in suggestions if item.lower() != asked][:3]
