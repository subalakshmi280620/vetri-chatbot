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
    "who can study",
    "qualification required",
    "qualification is required",
    "qualification needed",
    "what qualification",
    "qualifications required",
    "minimum qualification",
    "educational requirement",
    "entry requirement",
    "eligibility criteria",
    "degree required",
    "need a degree",
    "qualify",
    "admission",
    "can i join",
    "can i apply",
    "can i enroll",
    "can freshers",
    "am i eligible",
    "requirements for admission",
    "who is eligible",
    "thaguthi",
    "padikalaama",
    "padikalam",
    "join pannalaama",
    "serthalama",
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
    from .query_intents import is_non_eligibility_topic

    return is_non_eligibility_topic(text)


def is_self_check(text: str) -> bool:
    lowered = text.lower().strip()

    if any(
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
    ):
        return True

    personal_education_phrases = (
        "i have completed",
        "i have finished",
        "i have passed",
        "i finished",
        "i passed",
        "i graduated",
        "i am studying",
        "i'm studying",
        "i am pursuing",
        "i'm pursuing",
        "i haven't completed",
        "i have not completed",
        "i am still studying",
        "i'm still studying",
    )

    return bool(_qualification_from_text(text)) and any(
        phrase in lowered for phrase in personal_education_phrases
    )


def _evaluate_eligibility(course_id: str, course_name: str, qualification: str) -> str:
    rule = COURSE_ELIGIBILITY.get(course_id)
    if not rule:
        return (
            f"Thanks for sharing ({qualification}). I don't have enough verified info "
            f"to confirm eligibility for {course_name}. "
            f"{CONTACT_LINE}"
        )

    if qualification_meets_degree_requirement(qualification):
        return (
            "Good news! You meet the requirement for "
            f"{course_name} ({rule.lower()}). "
            "Would you like to know about fees or how to apply?"
        )

    return (
        f"For {course_name}, a completed degree is required ({rule.lower()}). "
        f"Based on what you shared ({qualification}), you may not meet that yet. "
        f"{CONTACT_LINE}"
    )


def _is_eligibility_outcome(last_bot: str) -> bool:
    return any(
        phrase in last_bot
        for phrase in (
            "you meet the requirement",
            "may not meet that yet",
            "don't have enough verified info",
            "outcome: eligible",
            "outcome: not eligible",
        )
    )


def _is_waiting_for_eligibility_details(last_bot: str) -> bool:
    if _is_eligibility_outcome(last_bot):
        return False
    return any(
        phrase in last_bot
        for phrase in (
            "which course you're interested",
            "which course are you interested",
            "what's your qualification",
            "share your qualification",
            "check your eligibility",
            "please select the course",
        )
    )


def _eligibility_reply_in_language(english_reply: str, language: str) -> str:
    from .language import LANG_TA, normalize_language

    if normalize_language(language) != LANG_TA:
        return english_reply
    if "you meet the requirement" in english_reply.lower():
        return english_reply.replace(
            "Good news — with your",
            "நல்ல செய்தி — உங்கள்",
        ).replace(
            "Would you like to know about fees or how to apply?",
            "கட்டணம் அல்லது எப்படி விண்ணப்பிப்பது என்பதைத் தெரிந்துகொள்ள விரும்புகிறீர்களா?",
        )
    if "may not meet that yet" in english_reply.lower():
        return english_reply.replace(
            "For ",
            "",
        ).replace(
            ", a completed degree is required",
            " — முடித்த பட்டப்படிப்பு அவசியம்",
        ).replace(
            "Based on what you shared",
            "நீங்கள் பகிர்ந்த தகவலின்படி",
        )
    if "Which course are you interested in" in english_reply:
        return (
            "நன்றி! எந்தப் பயிற்சிப் பாடத்தில் சேர விரும்புகிறீர்கள்? Python Fullstack, Java Fullstack, UI/UX, "
            "Software Testing உள்ளிட்ட பாடங்கள் உள்ளன."
        )
    if "What's your qualification" in english_reply:
        return english_reply.replace(
            "What's your qualification?",
            "உங்கள் கல்வித் தகுதி என்ன? (எ.கா., B.Tech, B.Sc, BCA, B.Com, MBA, MCA)",
        )
    if "don't have enough verified info" in english_reply.lower():
        return (
            english_reply.replace(
                "Thanks for sharing",
                "பகிர்ந்த தகவலுக்கு நன்றி",
            )
        )
    return english_reply


def handle_eligibility(user_message: str, history=None, language: str = "en") -> str | None:
    text = user_message.strip()
    if is_non_eligibility_faq(text):
        return None

    last_bot = _last_bot(history).lower()
    waiting = _is_waiting_for_eligibility_details(last_bot)
    if (
        not is_eligibility_intent(text)
        and not waiting
        and not (
            is_self_check(text)
            and _qualification_from_text(text)
        )
    ):
        return None

    explicit_course_id = match_course_id(text)
    explicit_course_name = match_course_name(explicit_course_id)

    if not is_self_check(text) and not waiting:
        if explicit_course_id:
            reply = eligibility_reply(explicit_course_name)
            reply = (
                f"For {explicit_course_name}, the course duration is 180 days "
                "and includes a 3-month internship. "
                + reply
            )
            return _eligibility_reply_in_language(reply, language)
        return _eligibility_reply_in_language(general_eligibility_reply(), language)

    user_combined = f"{_user_history_text(history)} {text}"
    course_id = explicit_course_id or (match_course_id(user_combined) if waiting else None)
    course_name = match_course_name(course_id) if course_id else ""
    qualification = extract_qualification(text) or (
        extract_qualification_from_context(history, text) if waiting else ""
    )

    if not course_id and not qualification:
        if waiting and not is_eligibility_intent(text) and not is_self_check(text):
            return None
        return _eligibility_reply_in_language(general_eligibility_reply(), language)

    if not course_id:
        if qualification and not qualification_meets_degree_requirement(qualification) and not waiting:
            reply = (
                f"A completed degree is required for our courses "
                f"({ELIGIBILITY_REQUIREMENT.lower()}). "
                f"Based on what you shared ({qualification}), you may not meet "
                f"that requirement yet. {CONTACT_LINE}"
            )
            return _eligibility_reply_in_language(reply, language)

        course_sample = ", ".join(COURSES[:4]) + ", and more"
        return _eligibility_reply_in_language(
            (
                f"Thanks! Which course are you interested in? We offer programmes like "
                f"{course_sample}."
            ),
            language,
        )


    if not qualification:
        return _eligibility_reply_in_language(
            (
                f"For {course_name}, you need {ELIGIBILITY_REQUIREMENT.lower()}. "
                "What's your qualification? (e.g. B.Tech, B.Sc, BCA, B.Com, MBA, MCA)"
            ),
            language,
        )

    return _eligibility_reply_in_language(
        _evaluate_eligibility(course_id, course_name, qualification),
        language,
    )
