"""Verified-facts rules for Coach AI — natural replies, exact official data."""

import re

from .knowledge import (
    CONTACT_ADDRESS,
    CONTACT_EMAIL,
    CONTACT_PHONE,
    COURSE_DURATION,
    COURSES,
    ELIGIBILITY_REQUIREMENT,
    ORG_NAME,
    PRODUCTS,
    SERVICES,
)

# Topics the bot must never invent — redirect to contact/quotation instead.
NEVER_INVENT = (
    "Exact product or course prices (₹, Rs, INR, $ amounts)",
    "Client names, logos, or portfolio case studies not in verified content",
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
        "Answer the user's question directly from verified VIS content. "
        "Do NOT default to 'contact our team' — only suggest contact for exact "
        "pricing quotes or when the user explicitly wants a human.\n\n"
        "Never invent:\n"
        f"{never}\n\n"
        "Must be exact when mentioned:\n"
        f"{exact}\n\n"
        "If something is truly not in verified content, say what you DO know about "
        "related VIS topics, then briefly note the gap. Do not guess."
    )


def enforce_verified_facts(reply: str) -> str:
    """Strip risky invented pricing from AI replies."""
    if not reply or not _INVENTED_PRICE_RE.search(reply):
        return reply

    sentences = re.split(r"(?<=[.!?])\s+", reply.strip())
    safe = [s for s in sentences if not _INVENTED_PRICE_RE.search(s)]
    cleaned = " ".join(safe).strip()
    if not cleaned:
        cleaned = "I don't have verified pricing for that in our official information."
    if _PRICING_REDIRECT not in cleaned:
        cleaned = f"{cleaned} {_PRICING_REDIRECT}"
    return cleaned
