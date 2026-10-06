"""Recognise common user questions phrased in different ways."""

from __future__ import annotations

import re

FEE_REGEX = (
    r"\bfee?s?\b",
    r"\btuition\b",
    r"\bpricing\b",
    r"\bprice\b",
    r"\bcost\b",
    r"\bcharge?s?\b",
    r"\bpayment\b",
    r"\bpay for\b",
    r"\bhow much\b",
    r"\bhow many rupees\b",
    r"\bwhat(?:'s| is) the (?:fee|fees|price|cost)\b",
    r"\bhow much does (?:it|the course|this)\s+cost\b",
    r"\bhow much (?:do|does|will) (?:i|we|it)\b",
    r"\bexpensive\b",
    r"\bafford\b",
    r"\bevlo\b",
    r"\bselavu\b",
    r"\bfees enna\b",
)

DURATION_PHRASES = (
    "duration",
    "how long",
    "how many months",
    "how many days",
    "time period",
    "length of course",
    "course length",
    "how many week",
    "period of course",
    "ethana naal",
    "ethana month",
)

APPLY_PHRASES = (
    "how to apply",
    "how do i apply",
    "how can i apply",
    "application process",
    "admission process",
    "how to enroll",
    "how to enrol",
    "how to join",
    "how to register",
    "joining process",
    "enrollment process",
    "enrolment process",
    "apply pannanum",
    "join pannanum",
)

CONTACT_PHRASES = (
    "contact",
    "phone",
    "call",
    "mobile number",
    "email address",
    "where are you",
    "location",
    "address",
    "office",
)

COURSE_LIST_PHRASES = (
    "which courses",
    "what courses",
    "courses available",
    "courses are available",
    "list of courses",
    "course list",
    "training programmes",
    "training programs",
    "what can i study",
    "what programmes",
)

BUSINESS_PHRASES = (
    "product",
    "products",
    "service",
    "services",
    "portfolio",
    "lms",
    "crm",
    "vetri bills",
    "web development",
    "printing",
    "hardware",
    "networking",
    "backup",
    "maintenance",
    "amc",
    "quotation",
    "quote",
    "about vis",
    "about company",
    "about vetri",
    "mock interview",
    "login",
    "sign up",
    "get started",
)

TRAINING_CONTEXT_MARKERS = (
    "course",
    "training",
    "fullstack",
    "full stack",
    "eligib",
    "degree",
    "enroll",
    "enrol",
    "programme",
    "program",
    "internship",
    "python",
    "java",
    "ui/ux",
    "testing",
    "admission",
    "qualification",
)


def _matches_regex(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def _matches_phrases(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def matches_fee_intent(text: str) -> bool:
    return _matches_regex(text, FEE_REGEX)


def matches_duration_intent(text: str) -> bool:
    return _matches_phrases(text, DURATION_PHRASES)


def matches_apply_intent(text: str) -> bool:
    return _matches_phrases(text, APPLY_PHRASES)


def has_training_context(text: str, history=None) -> bool:
    combined = text.lower()
    for item in (history or [])[-8:]:
        combined += " " + str(item.get("text", "")).lower()
    return any(marker in combined for marker in TRAINING_CONTEXT_MARKERS)


def is_non_eligibility_topic(text: str) -> bool:
    """Topics that should not be handled by the eligibility flow."""
    if not text.strip():
        return False
    if matches_fee_intent(text):
        return True
    if matches_duration_intent(text):
        return True
    if matches_apply_intent(text):
        return True
    return _matches_phrases(
        text,
        CONTACT_PHRASES + COURSE_LIST_PHRASES + BUSINESS_PHRASES,
    )
