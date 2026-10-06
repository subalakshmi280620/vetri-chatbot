"""Verified-facts rules for Coach AI — natural replies, exact official data."""

import re

from .knowledge import (
    COMPANY_STATS,
    CONTACT_ADDRESS,
    CONTACT_EMAIL,
    CONTACT_PHONE,
    COURSE_DURATION,
    COURSE_INTERNSHIP,
    COURSES,
    ECOMMERCE_WEBSITE_PRICE,
    ELIGIBILITY_REQUIREMENT,
    ORG_NAME,
    PORTFOLIO_PROJECTS,
    PRODUCTS,
    RETAIL_SHOP_WEBSITE_PRICE,
    SERVICES,
)

# Topics the bot must never invent — redirect to contact/quotation instead.
NEVER_INVENT = (
    (
        "Prices other than the official website packages: "
        f"ecommerce website {ECOMMERCE_WEBSITE_PRICE}, "
        f"small retail shop website {RETAIL_SHOP_WEBSITE_PRICE}"
    ),
    "Portfolio projects, clients, or metrics not in verified VIS website content",
    "Product features or services not listed on the VIS website",
    "Guaranteed job placement, salary, or admission outcomes",
    "Competitor comparisons unless explicitly in verified content",
)

# Topics that must match the knowledge base exactly.
MUST_BE_EXACT = (
    f"Company name: {ORG_NAME}",
    f"Phone: {CONTACT_PHONE}",
    f"Email: {CONTACT_EMAIL}",
    f"Address: {CONTACT_ADDRESS}",
    f"Course duration: {COURSE_DURATION}",
    f"Internship with every course: {COURSE_INTERNSHIP}",
    f"Ecommerce website package: {ECOMMERCE_WEBSITE_PRICE}",
    f"Small retail shop website: {RETAIL_SHOP_WEBSITE_PRICE}",
    f"Course eligibility: {ELIGIBILITY_REQUIREMENT}",
    f"Products: {', '.join(PRODUCTS)}",
    f"Services: {', '.join(SERVICES)}",
    f"Training courses: {', '.join(COURSES)}",
    (
        "Company stats: "
        f"{COMPANY_STATS['projects']} projects, {COMPANY_STATS['years']} years, "
        f"{COMPANY_STATS['clients']} clients, {COMPANY_STATS['team']} team experts"
    ),
    f"Featured portfolio: {', '.join(p['name'] for p in PORTFOLIO_PROJECTS)}",
)

_INVENTED_PRICE_RE = re.compile(
    r"(₹|rs\.?\s*\d+|\$\s*\d+|inr\s*\d+|\d{1,3}(?:,\d{3})+\s*(?:per|/)\s*(?:month|year)|"
    r"\d+\s*(?:per month|/month|per year|/year))",
    re.IGNORECASE,
)
_ALLOWED_PRICE_RE = re.compile(
    r"(?:₹|rs\.?|inr)\s*(?:9,?999|3,?000)\b",
    re.IGNORECASE,
)

_PRICING_REDIRECT = (
    f"Exact pricing depends on your scope — I can't quote a fixed amount here. "
    f"Request a tailored quotation at {CONTACT_EMAIL} or {CONTACT_PHONE}."
)


def get_verified_facts_prompt(reply_style: str = "brief", language: str = "en") -> str:
    """Prompt block injected before every AI call."""
    from .knowledge import REPLY_STYLE_BRIEF, normalize_reply_style
    from .language import get_response_language_instruction

    never = "\n".join(f"- {item}" for item in NEVER_INVENT)
    exact = "\n".join(f"- {item}" for item in MUST_BE_EXACT)
    length_hint = (
        "Use 1 to 2 short sentences with the key facts included."
        if normalize_reply_style(reply_style) == REPLY_STYLE_BRIEF
        else "Use 2 to 4 short sentences."
    )
    return (
        f"{get_response_language_instruction(language)}\n\n"
        "VERIFIED FACTS ONLY (critical):\n"
        "Reply like a friendly human on chat — warm, clear, and complete. "
        f"{length_hint} Never copy grounding labels or sound like a brochure. "
        "Answer the user's exact question first. Do NOT default to 'contact our team' — "
        "only suggest contact for exact pricing or when they want a human.\n\n"
        "Never invent:\n"
        f"{never}\n\n"
        "Must be exact when mentioned:\n"
        f"{exact}\n\n"
        "If something is not in verified content, share what you do know, then note the gap briefly. "
        "Do not guess."
    )


_STAT_FIXES = (
    (re.compile(r"\bdelivering\s+15\b(?!\s*\+)", re.I), "delivering 150+ projects"),
    (re.compile(r"\bover\s+8\s+years\b", re.I), f"over {COMPANY_STATS['years']} years"),
    (re.compile(r"\b15\s+projects\b", re.I), f"{COMPANY_STATS['projects']} projects"),
    (re.compile(r"\b50\s+clients\b(?!\s*\+)", re.I), f"{COMPANY_STATS['clients']} clients"),
)


def polish_ai_reply(reply: str) -> str:
    """Light cleanup so AI replies stay complete and natural."""
    text = (reply or "").strip()
    if not text:
        return text

    for pattern, replacement in _STAT_FIXES:
        text = pattern.sub(replacement, text)

    # Drop accidental copied meta-labels from grounding blocks
    for prefix in (
        "Company identity:",
        "Why choose VIS (differentiators — not a company intro):",
        "Contact details only:",
    ):
        text = text.replace(prefix, "").strip()

    if text and text[-1] not in ".!?":
        text = f"{text}."
    return text


def _has_disallowed_price(sentence: str) -> bool:
    if not _INVENTED_PRICE_RE.search(sentence):
        return False
    without_allowed = _ALLOWED_PRICE_RE.sub("", sentence)
    return bool(_INVENTED_PRICE_RE.search(without_allowed))


def enforce_verified_facts(reply: str) -> str:
    """Strip risky invented pricing from AI replies. Keep the two official website prices."""
    text = polish_ai_reply(reply)
    if not text or not _has_disallowed_price(text):
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    safe = [s for s in sentences if not _has_disallowed_price(s)]
    cleaned = " ".join(safe).strip()
    if not cleaned:
        cleaned = (
            "I don't have a verified fixed price for that in our official information."
        )
    if _PRICING_REDIRECT not in cleaned:
        cleaned = f"{cleaned} {_PRICING_REDIRECT}"
    return polish_ai_reply(cleaned)
