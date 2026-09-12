"""Eligibility checks using only verified course rules. Never invent criteria."""

from .knowledge import (
    COURSES,
    CONTACT_LINE,
    ELIGIBILITY_REQUIREMENT,
    eligibility_reply,
    match_course_id,
    match_course_name,
    qualification_meets_degree_requirement,
)

COURSE_ELIGIBILITY: dict[str, str] = {
    "java": ELIGIBILITY_REQUIREMENT,
    "python": ELIGIBILITY_REQUIREMENT,
    "prompt": ELIGIBILITY_REQUIREMENT,
    "uiux": ELIGIBILITY_REQUIREMENT,
    "testing": ELIGIBILITY_REQUIREMENT,
    "analytics": ELIGIBILITY_REQUIREMENT,
    "mobile": ELIGIBILITY_REQUIREMENT,
    "aws": ELIGIBILITY_REQUIREMENT,
    "datascience": ELIGIBILITY_REQUIREMENT,
    "marketing": ELIGIBILITY_REQUIREMENT,
}

ELIGIBILITY_PHRASES = (
    "eligib",
    "who can apply",
    "who can join",
    "qualification required",
    "qualifications required",
    "qualify",
    "admission",
    "can i join",
    "can i apply",
    "can i enroll",
    "am i eligible",
    "requirements for admission",
    "who is eligible",
)

QUALIFICATION_HINTS = (
    "10th", "12th", "sslc", "hsc", "diploma", "degree", "graduate",
    "ug", "pg", "btech", "b.tech", "b.e", "bsc", "bca", "b.com", "bcom",
    "mba", "mca", "engineering", "arts", "commerce", "science",
    "fresher", "professional", "iti", "plus two", "+2",
)


def is_eligibility_intent(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in ELIGIBILITY_PHRASES)


def extract_qualification(text: str) -> str:
    lowered = text.lower()
    if any(hint in lowered for hint in QUALIFICATION_HINTS):
        return text.strip()
    return ""


def _last_bot(history) -> str:
    for item in reversed(history or []):
        if item.get("role") == "bot":
            return item.get("text", "")
    return ""


def _history_text(history) -> str:
    return " ".join(item.get("text", "") for item in (history or []))


def is_self_check(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in (
            "am i eligible",
            "can i join",
            "can i apply",
            "can i enroll",
            "my qualification",
            "i completed",
            "i have a",
            "i am a",
            "i'm a",
        )
    )


def _evaluate_eligibility(course_id: str, course_name: str, qualification: str) -> str:
    rule = COURSE_ELIGIBILITY.get(course_id)
    if not rule:
        return (
            "Eligibility Assessment\n"
            "Outcome: CANNOT DETERMINE\n\n"
            f"Thank you for sharing your details. I do not have enough verified information "
            f"to confirm your eligibility for {course_name}.\n\n"
            f"Qualification provided: {qualification}\n\n"
            f"{CONTACT_LINE}"
        )

    if qualification_meets_degree_requirement(qualification):
        return (
            "Eligibility Assessment\n"
            "Outcome: ELIGIBLE\n\n"
            f"Based on the information you provided, you appear to be eligible for "
            f"{course_name} because you meet the listed eligibility requirements.\n\n"
            f"Qualification provided: {qualification}\n"
            f"Listed requirement: {rule}\n\n"
            f"{CONTACT_LINE}"
        )

    return (
        "Eligibility Assessment\n"
        "Outcome: NOT ELIGIBLE\n\n"
        f"Based on the eligibility requirements currently available, you may not meet the "
        f"requirements for {course_name} because a completed degree is required.\n\n"
        f"Qualification provided: {qualification}\n"
        f"Listed requirement: {rule}\n\n"
        f"{CONTACT_LINE}"
    )


def handle_eligibility(user_message: str, history=None) -> str | None:
    text = user_message.strip()
    last_bot = _last_bot(history).lower()
    waiting = (
        "which course are you interested" in last_bot
        or "education qualification" in last_bot
        or "to check eligibility" in last_bot
        or "eligibility assessment" in last_bot
    )
    if not is_eligibility_intent(text) and not waiting:
        return None

    combined = f"{_history_text(history)} {text}"
    course_id = match_course_id(text) or match_course_id(combined)
    course_name = match_course_name(course_id) if course_id else ""

    if not is_self_check(text) and not waiting:
        if not course_id:
            return (
                "Eligibility Requirements\n\n"
                f"• Requirement: {ELIGIBILITY_REQUIREMENT}\n"
                "• Accepted examples: B.Tech, B.Sc, BCA, B.Com, MBA, MCA, or any other "
                "completed undergraduate or postgraduate degree.\n\n"
                "Please let me know which course you would like eligibility details for:\n"
                + "\n".join(f"• {name}" for name in COURSES)
            )
        return eligibility_reply(course_name)

    qualification = extract_qualification(text) or extract_qualification(combined)

    if not course_id:
        return (
            "Eligibility Check\n\n"
            "I can review eligibility using only the official VIS course information we have.\n\n"
            "Please select the course you are interested in:\n"
            + "\n".join(f"• {name}" for name in COURSES)
        )

    if not qualification:
        return (
            f"Eligibility Check — {course_name}\n\n"
            "To proceed, please share your education qualification.\n\n"
            f"Requirement: {ELIGIBILITY_REQUIREMENT}\n"
            "Examples: B.Tech, B.Sc, BCA, B.Com, MBA, or MCA."
        )

    return _evaluate_eligibility(course_id, course_name, qualification)
