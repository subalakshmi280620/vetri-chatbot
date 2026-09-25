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
    "courses": (
        "What are the eligibility requirements?",
        "How do I apply for a course?",
        "What is the course duration?",
    ),
    "eligibility": (
        "How do I apply for a course?",
        "What courses are available?",
        "How can I contact the VIS team?",
    ),
    "apply": (
        "What are the eligibility requirements?",
        "What courses are available?",
        "How can I contact the VIS team?",
    ),
    "fees": (
        "How can I get a quotation?",
        "What courses are available?",
        "How can I contact the VIS team?",
    ),
    "duration": (
        "What courses are available?",
        "What are the eligibility requirements?",
        "How do I apply for a course?",
    ),
    "course_detail": (
        "What are the eligibility requirements?",
        "How do I apply for this course?",
        "What is the course duration?",
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
    if "eligibility assessment" in combined or "general eligibility" in combined:
        return "eligibility"
    if "how to apply" in combined or "step 1:" in combined:
        return "apply"
    if "book a consultation" in combined:
        return "consultation"
    if "request a product demo" in combined or "product demo" in combined:
        return "demo"
    if "get quotation" in combined or "pricing & quotation" in combined:
        return "quotation"
    if "course fee" in combined or "indicative pricing" in combined:
        return "fees"
    if "mission & vision" in combined or "our vision" in combined:
        return "vision"
    if "ai solutions" in combined or "data → context" in combined:
        return "ai_solutions"
    if "contact" in combined and ("support@vetri-it.com" in combined or "+91" in combined):
        return "contact"
    if "course duration" in combined or "180 days" in combined:
        return "duration"
    if "our products" in combined or "vetri bills" in combined:
        return "products"
    if "our services" in combined or "end-to-end capability" in combined:
        return "services"
    if "portfolio" in combined:
        return "portfolio"
    if any(phrase in combined for phrase in ("about vetri", "about vis", "about us")):
        return "about"
    if "available courses" in combined or "training courses" in combined:
        return "courses"
    if "course overview" in combined:
        return "course_detail"
    if any(word in combined for word in ("course", "fullstack", "data science")):
        return "course_detail"
    return ""


def get_follow_up_suggestions(user_message: str, reply: str, source: str) -> list[str]:
    topic = _detect_topic(user_message, reply)
    suggestions = list(TOPIC_SUGGESTIONS.get(topic, DEFAULT_SUGGESTIONS))

    asked = user_message.strip().lower()
    return [item for item in suggestions if item.lower() != asked][:3]
