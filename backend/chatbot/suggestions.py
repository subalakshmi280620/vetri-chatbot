"""Contextual follow-up question suggestions for Coach AI."""

DEFAULT_SUGGESTIONS = (
    "What courses are available?",
    "What are the eligibility requirements?",
    "How do I apply for a course?",
)

TOPIC_SUGGESTIONS = {
    "courses": (
        "What are the eligibility requirements?",
        "How do I apply for a course?",
        "What is the course duration?",
    ),
    "eligibility": (
        "How do I apply for a course?",
        "What are the fees?",
        "How can I contact the VIS team?",
    ),
    "apply": (
        "What are the eligibility requirements?",
        "What courses are available?",
        "How can I contact the VIS team?",
    ),
    "fees": (
        "How do I apply for a course?",
        "What courses are available?",
        "How can I contact the VIS team?",
    ),
    "contact": (
        "What courses are available?",
        "How do I apply for a course?",
        "What are the eligibility requirements?",
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
}


def _detect_topic(user_message: str, reply: str) -> str:
    combined = f"{user_message}\n{reply}".lower()
    if "eligibility assessment" in combined or "general eligibility" in combined:
        return "eligibility"
    if "how to apply" in combined or "step 1:" in combined:
        return "apply"
    if "course fee" in combined or "fee amounts" in combined:
        return "fees"
    if "contact" in combined and "+91" in combined:
        return "contact"
    if "course duration" in combined or "180 days" in combined:
        return "duration"
    if "available courses" in combined or "course overview" in combined:
        return "courses" if "available courses" in combined else "course_detail"
    if any(word in combined for word in ("course", "fullstack", "data science", "ui/ux")):
        return "course_detail"
    return ""


def get_follow_up_suggestions(user_message: str, reply: str, source: str) -> list[str]:
    topic = _detect_topic(user_message, reply)
    suggestions = list(TOPIC_SUGGESTIONS.get(topic, DEFAULT_SUGGESTIONS))

    asked = user_message.strip().lower()
    return [item for item in suggestions if item.lower() != asked][:3]
