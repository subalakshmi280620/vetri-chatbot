"""Verified Tamil KB replies — same facts as English fallbacks, curated wording only."""

from .knowledge import (
    COMPANY_STATS,
    CONTACT_ADDRESS,
    CONTACT_EMAIL,
    CONTACT_PHONE,
    COURSE_DURATION,
    COURSE_INTERNSHIP,
    ECOMMERCE_WEBSITE_PRICE,
    ELIGIBILITY_REQUIREMENT,
    GENERIC_FALLBACK_MARKER,
    ORG_NAME,
    PORTFOLIO_PROJECTS,
    REPLY_STYLE_BRIEF,
    RETAIL_SHOP_WEBSITE_PRICE,
    SHORT_PRODUCT_SUMMARIES,
    _is_course_context,
    _matches_about_intent,
    _matches_apply_intent,
    _matches_consultation_intent,
    _matches_contact_intent,
    _matches_demo_intent,
    _matches_portfolio_intent,
    _matches_products_intent,
    _matches_quotation_intent,
    _matches_sales_intent,
    _matches_services_intent,
    _matches_vision_mission_intent,
    _matches_website_price_intent,
    _matches_why_vis_intent,
    is_greeting,
    match_course_id,
    match_course_name,
    match_product_id,
    normalize_reply_style,
)
TAMIL_GREETING_REPLY = "வணக்கம்! இன்று நான் எப்படி உதவலாம்?"

TAMIL_GENERIC_FALLBACK = (
    "VIS தயாரிப்புகள், சேவைகள், பயிற்சி பாடங்கள், quotation மற்றும் நிறுவன தகவல் "
    "பற்றி நான் உதவ முடியும்."
)

TAMIL_AI_UNAVAILABLE = (
    "AI சேவை தற்போது பிஸியாக இருக்கலாம். ஒரு நிமிடம் கழித்து மீண்டும் முயற்சிக்கவும், "
    f"அல்லது {CONTACT_PHONE} அழைக்கவும்."
)

_TAMIL_PRODUCT_SUMMARIES = {
    "vetri_bills": (
        "Vetri Bills என்பது GST-ready billing software — inventory, barcode scanning, "
        "sales analytics உடன்."
    ),
    "vetri_files": (
        "Vetri Files என்பது secure document management — OCR search, versioning, audit trails உடன்."
    ),
    "vetri_pm": (
        "Project Management Tool — Kanban, Gantt charts, time tracking, team workflows உடன்."
    ),
    "coach_ai": (
        "Coach AI என்பது VIS learning assistant — courses, quizzes, progress tracking உடன்."
    ),
    "vetri_crm": (
        "Vetri CRM — lead capture, follow-up automation, AI-scored pipeline உடன்."
    ),
}


def get_tamil_greeting() -> str:
    return TAMIL_GREETING_REPLY


def get_tamil_ai_unavailable() -> str:
    return TAMIL_AI_UNAVAILABLE


def get_tamil_generic_fallback() -> str:
    return TAMIL_GENERIC_FALLBACK


def reply_to_short_yes_tamil(history=None) -> str:
    from .knowledge import _bot_offered_action, _last_bot_text

    last = _last_bot_text(history).lower()
    if any(word in last for word in ("enroll", "join", "course", "internship", "சேர")):
        return (
            "ஆம். Enroll now அழுத்தி உங்கள் பெயர், email, phone பகிருங்கள். "
            "VIS குழு தொடர்பு கொள்ளும். website sign-in தேவையில்லை."
        )
    if any(word in last for word in ("demo",)):
        return "ஆம். Request demo தேர்வு செய்து எந்த product பார்க்க வேண்டும் என்று சொல்லுங்கள்."
    if any(word in last for word in ("quotation", "quote", "pricing", "price")):
        return "ஆம். Enquiry → Quotation தேர்வு செய்து உங்கள் தேவையை அனுப்புங்கள்."
    if last:
        return "ஆம். அடுத்து எது விளக்க வேண்டும் — course, product, அல்லது enroll?"
    return "ஆம். எதில் உதவ வேண்டும் — course, product, அல்லது website?"


def build_tamil_fallback(message: str, reply_style: str = REPLY_STYLE_BRIEF) -> str | None:
    """Return a verified Tamil KB reply when we have one; else None (use English)."""
    text = message.strip().lower()
    detailed = normalize_reply_style(reply_style) != REPLY_STYLE_BRIEF

    if is_greeting(text):
        return TAMIL_GREETING_REPLY

    website_offer = _matches_website_price_intent(text)
    if website_offer == "ecommerce":
        return (
            f"VIS ecommerce website package {ECOMMERCE_WEBSITE_PRICE}. "
            "தொடங்க வேண்டுமென்றால் enroll என்று சொல்லி details பகிருங்கள் — sign-in தேவையில்லை."
        )
    if website_offer == "retail":
        return (
            f"சிறிய retail shop website {RETAIL_SHOP_WEBSITE_PRICE}. "
            "enroll என்று சொல்லி details பகிருங்கள் — குழு தொடர்பு கொள்ளும்."
        )

    if _matches_quotation_intent(text) and not _is_course_context(text):
        return (
            "விலை scope-ஐப் பொறுத்து மாறும் — users, features, timeline. "
            "Enquiry → Quotation தேர்வு செய்து formal quote கேளுங்கள்."
        )

    product_id = match_product_id(text)
    if product_id:
        summary = _TAMIL_PRODUCT_SUMMARIES.get(product_id)
        if not summary and product_id in SHORT_PRODUCT_SUMMARIES:
            return f"{SHORT_PRODUCT_SUMMARIES[product_id]} மேலும் விவரம் வேண்டுமா?"
        if summary:
            return f"{summary} மேலும் விவரம் வேண்டுமா?"

    course_id = match_course_id(text)
    if course_id:
        course_name = match_course_name(course_id)
        if any(k in text for k in ("duration", "how long", "நாள்", "காலம்")):
            return (
                f"{course_name} {COURSE_DURATION} ({COURSE_INTERNSHIP} internship). "
                f"தகுதி: {ELIGIBILITY_REQUIREMENT.lower()}."
            )
        if any(k in text for k in ("fee", "fees", "tuition", "course fee", "price", "cost", "evlo", "fees")):
            if detailed:
                return (
                    f"{course_name} {COURSE_DURATION} programme — degree தகுதி தேவை. "
                    "Fees batch-ஐப் பொறுத்து மாறும். exact quote-க்கு Enquiry form பயன்படுத்துங்கள்."
                )
            return (
                f"{course_name} fees batch-ஐப் பொறுத்து மாறும். Programme {COURSE_DURATION} — "
                "exact quote-க்கு Enquiry."
            )
        if detailed:
            return (
                f"{course_name} ஒரு {COURSE_DURATION} VIS training programme. "
                f"{ELIGIBILITY_REQUIREMENT.lower()} தேவை. "
                f"ஒவ்வொரு course-க்கும் {COURSE_INTERNSHIP} internship உள்ளது. "
                "சேர வேண்டுமென்றால் enroll என்று சொல்லி details பகிருங்கள் — website sign-in தேவையில்லை."
            )
        return (
            f"{course_name}: {COURSE_DURATION} programme, {COURSE_INTERNSHIP} internship. "
            f"{ELIGIBILITY_REQUIREMENT.lower()} தேவை. enroll என்று சொல்லி சேரலாம் — sign-in தேவையில்லை."
        )

    if _matches_why_vis_intent(text):
        stats = COMPANY_STATS
        if detailed:
            return (
                f"VIS-ஐ நம்புவதற்கு enterprise-grade delivery, AI-first engineering, "
                f"{stats['projects']} projects / {stats['years']} years track record — "
                "Vetri Bills, Coach AI போன்ற products உள்ளன. உங்கள் தேவை எது?"
            )
        return (
            f"VIS — trusted delivery, AI-first engineering; {stats['projects']} projects, "
            f"{stats['years']} years; Vetri Bills, Coach AI."
        )

    if _matches_about_intent(text):
        if detailed:
            return (
                f"{ORG_NAME} தமிழ்நாட்டை சேர்ந்த IT நிறுவனம் — websites, mobile apps, enterprise software, "
                "மற்றும் Vetri Bills (GST billing), Coach AI போன்ற products. "
                "product அல்லது custom service எது வேண்டும்?"
            )
        return (
            f"{ORG_NAME} தமிழ்நாட்டில் websites, apps, enterprise software மற்றும் "
            "Vetri Bills, Coach AI products வழங்குகிறது."
        )

    if _matches_contact_intent(text):
        return (
            f"முகவரி: {CONTACT_ADDRESS}. Phone: {CONTACT_PHONE}. Email: {CONTACT_EMAIL}. "
            "இன்று எதில் உதவ வேண்டும்?"
        )

    if _matches_demo_intent(text):
        return (
            "Vetri Bills, Vetri CRM, Coach AI போன்ற products-க்கு live demo உள்ளது. "
            "Enquiry → Product Demo தேர்வு செய்து use case சொல்லுங்கள்."
        )

    if _matches_consultation_intent(text):
        return (
            "VIS consultant உங்கள் business goals பற்றி பேசி சரியான product/service பரிந்துரை செய்வார். "
            "Enquiry → Consultation தேர்வு செய்து details அனுப்புங்கள்."
        )

    if _matches_products_intent(text) and not _is_course_context(text):
        return (
            "VIS products: Vetri Bills (GST billing), project management, HR tool, "
            "Vetri CRM, Coach AI. எது பற்றி விவரம் வேண்டும்?"
        )

    if _matches_services_intent(text) and not _is_course_context(text):
        return (
            "VIS websites, mobile apps, custom software, digital marketing, AI solutions, ERP, "
            "cloud services செய்கிறது. எந்த வகை project திட்டமிடுகிறீர்கள்?"
        )

    if _matches_apply_intent(text):
        return (
            "VIS training-க்கு: (1) degree முடித்திருக்க வேண்டும், (2) course தேர்வு, "
            f"(3) qualification பகிரவும். Programme {COURSE_DURATION}."
        )

    if _matches_portfolio_intent(text):
        sample = ", ".join(p["name"] for p in PORTFOLIO_PROJECTS[:2])
        stats = COMPANY_STATS
        return (
            f"Featured work: {sample} மற்றும் பல — {stats['projects']} projects Tamil Nadu மற்றும் "
            "வெளியிலும். retail, healthcare, mobile, e-commerce எது interest?"
        )

    if _matches_vision_mission_intent(text):
        return (
            "Vision: AI-powered business for everyone. Mission: dependable, intelligent enterprise software."
        )

    return None
