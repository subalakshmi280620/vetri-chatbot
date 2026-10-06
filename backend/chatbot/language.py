"""Detect user language and provide response-language instructions."""

import re

LANG_EN = "en"
LANG_TA = "ta"
VALID_LANGUAGES = {LANG_EN, LANG_TA}

_TAMIL_SCRIPT_RE = re.compile(r"[\u0B80-\u0BFF]")

# Romanized Tamil / Tanglish markers (lowercase).
_TANGLISH_MARKERS = (
    "vanakkam",
    "enna",
    "epdi",
    "eppadi",
    "evlo",
    "evalavu",
    "sollunga",
    "sollu",
    "sollringa",
    "ungal",
    "ungaluku",
    "naan",
    "nan",
    "venum",
    "venam",
    "padikalam",
    "padippu",
    "theriyuma",
    "theriyadha",
    "irukka",
    "irukku",
    "enga",
    "eng",
    "pathi",
    "patti",
    "pannanum",
    "pannunga",
    "puriyudhu",
    "puriyala",
    "innum",
    "konjam",
    "aparam",
    "illaya",
    "details venum",
    "explain pannu",
    "explain pannunga",
)


def normalize_language(value) -> str:
    lang = str(value or LANG_EN).strip().lower()
    return lang if lang in VALID_LANGUAGES else LANG_EN


def _last_user_text(history) -> str:
    for item in reversed(history or []):
        if item.get("role") == "user":
            return (item.get("text") or "").strip()
    return ""


def detect_language(message: str, history=None) -> str:
    """Return LANG_TA for Tamil script or clear Tanglish; otherwise LANG_EN."""
    text = (message or "").strip()
    if not text:
        if history:
            prior = _last_user_text(history)
            if prior:
                return detect_language(prior)
        return LANG_EN

    if _TAMIL_SCRIPT_RE.search(text):
        return LANG_TA

    lowered = text.lower()
    marker_hits = sum(1 for marker in _TANGLISH_MARKERS if marker in lowered)
    word_count = len(lowered.split())
    if marker_hits >= 2 or (marker_hits >= 1 and word_count <= 6):
        return LANG_TA

    # Short follow-ups inherit the previous user language.
    if history and word_count <= 4:
        prior = _last_user_text(history)
        if prior and prior.lower() != lowered:
            prior_lang = detect_language(prior)
            if prior_lang == LANG_TA:
                return LANG_TA

    return LANG_EN


def get_response_language_instruction(language: str) -> str:
    """Prompt block telling the LLM which language to use."""
    lang = normalize_language(language)
    if lang == LANG_TA:
        return (
            "RESPONSE LANGUAGE (critical):\n"
            "The user is writing in Tamil or Tanglish. Reply in natural Tamil (தமிழ்). "
            "You may mix simple English product names (Vetri Bills, Coach AI) where needed. "
            "Keep exact verified facts unchanged: prices (₹9,999 + GST, ₹3,000 + GST), "
            f"phone, email, addresses, course duration, and product names. "
            "Do not invent facts — only translate/explain verified information below."
        )
    return (
        "RESPONSE LANGUAGE:\n"
        "Reply in clear, natural English."
    )
