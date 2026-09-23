"""Eligibility checks using only verified course rules. Never invent criteria."""

from .knowledge import (
    CONTACT_LINE,
    COURSES,
    ELIGIBILITY_REQUIREMENT,
    eligibility_reply,
    general_eligibility_reply,
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
    "qualification is required",
    "what qualification",
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

NON_ELIGIBILITY_FAQ_PHRASES = (
    "fee", "fees", "tuition", "course cost", "course fee", "price", "pricing",
    "how to apply", "how do i apply", "how can i apply", "application process",
    "admission process", "how to enroll", "how to join", "how to register",
    "contact", "phone", "call", "mobile number",
    "duration", "how long", "how many months", "how many days",
    "which courses", "what courses", "courses available", "courses are available",
    "mock interview", "login", "sign up", "get started",
)


def is_eligibility_intent(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in ELIGIBILITY_PHRASES)


def _qualification_from_text(text: str) -> str:
    lowered = text.lower()
    if any(hint in lowered for hint in QUALIFICATION_HINTS):
        return text.strip()
    return ""


def extract_qualification(text: str) -> str:
    return _qualification_from_text(text)


def extract_qualification_from_context(history, current_text: str) -> str:
    if qualification := _qualification_from_text(current_text):
        return qualification
    for item in reversed(history or []):
        if item.get("role") != "user":
            continue
        if qualification := _qualification_from_text(item.get("text", "")):
            return qualification
    return ""


def _last_bot(history) -> str:
    for item in reversed(history or []):
        if item.get("role") == "bot":
            return item.get("text", "")
    return ""


def _user_history_text(history) -> str:
    return " ".join(
        item.get("text", "")
        for item in (history or [])
        if item.get("role") == "user"
    )


def is_non_eligibility_faq(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in NON_ELIGIBILITY_FAQ_PHRASES)


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
            f"Good news — based on your qualification ({qualification}), you appear to "
            f"meet the requirements for {course_name}.\n\n"
            f"Requirement: {rule}\n\n"
            "Would you like to know how to apply or about course fees? I can help with that.\n\n"
            f"{CONTACT_LINE}"
        )

    return (
        "Eligibility Assessment\n"
        "Outcome: NOT ELIGIBLE\n\n"
        f"Based on the available VIS requirements, a completed degree is needed for "
        f"{course_name}, and your shared qualification may not meet that yet.\n\n"
        f"Your qualification: {qualification}\n"
        f"Requirement: {rule}\n\n"
        f"{CONTACT_LINE}"
    )


def _is_eligibility_outcome(last_bot: str) -> bool:
    return any(
        phrase in last_bot
        for phrase in (
            "outcome: eligible",
            "outcome: not eligible",
            "outcome: cannot determine",
        )
    )


def _is_waiting_for_eligibility_details(last_bot: str) -> bool:
    if _is_eligibility_outcome(last_bot):
        return False
    return any(
        phrase in last_bot
        for phrase in (
            "please select the course you are interested",
            "to proceed, please share your education qualification",
            "please share your education qualification",
            "qualification and the course you are interested",
            "help check your eligibility",
        )
    )


def handle_eligibility(user_message: str, history=None) -> str | None:
    text = user_message.strip()
    if is_non_eligibility_faq(text):
        return None

    last_bot = _last_bot(history).lower()
    waiting = _is_waiting_for_eligibility_details(last_bot)
    if not is_eligibility_intent(text) and not waiting:
        return None

    explicit_course_id = match_course_id(text)
    explicit_course_name = match_course_name(explicit_course_id)

    if not is_self_check(text) and not waiting:
        if explicit_course_id:
            return eligibility_reply(explicit_course_name)
        return general_eligibility_reply()

    user_combined = f"{_user_history_text(history)} {text}"
    course_id = explicit_course_id or (match_course_id(user_combined) if waiting else None)
    course_name = match_course_name(course_id) if course_id else ""
    qualification = extract_qualification(text) or (
        extract_qualification_from_context(history, text) if waiting else ""
    )

    if not course_id and not qualification:
        return general_eligibility_reply()

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
