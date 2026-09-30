"""Verified-facts rules for Coach AI — natural replies, exact official data."""

import re

from .knowledge import (
    COMPANY_STATS,
    CONTACT_ADDRESS,
    CONTACT_EMAIL,
    CONTACT_PHONE,
    COURSE_DURATION,
    COURSES,
    ELIGIBILITY_REQUIREMENT,
    ORG_NAME,
    PORTFOLIO_PROJECTS,
    PRODUCTS,
    SERVICES,
)

# Topics the bot must never invent — redirect to contact/quotation instead.
NEVER_INVENT = (
    "Exact product or course prices (₹, Rs, INR, $ amounts)",
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

_PRICING_REDIRECT = (
    f"Exact pricing depends on your scope — I can't quote a fixed amount here. "
    f"Request a tailored quotation at {CONTACT_EMAIL} or {CONTACT_PHONE}."
)


def get_verified_facts_prompt() -> str:
    """Prompt block injected before every AI call."""
    never = "\n".join(f"- {item}" for item in NEVER_INVENT)
    exact = "\n".join(f"- {item}" for item in MUST_BE_EXACT)
    return (
        "VERIFIED FACTS ONLY (critical):\n"
        "Reply like a friendly human on chat — warm, clear, and complete. "
        "Use 2 to 4 short sentences. Never copy grounding labels or sound like a brochure. "
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


def enforce_verified_facts(reply: str) -> str:
    """Strip risky invented pricing from AI replies."""
    text = polish_ai_reply(reply)
    if not text or not _INVENTED_PRICE_RE.search(text):
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    safe = [s for s in sentences if not _INVENTED_PRICE_RE.search(s)]
    cleaned = " ".join(safe).strip()
    if not cleaned:
        cleaned = (
            "I don't have a verified fixed price for that in our official information."
        )
    if _PRICING_REDIRECT not in cleaned:
        cleaned = f"{cleaned} {_PRICING_REDIRECT}"
    return polish_ai_reply(cleaned)
