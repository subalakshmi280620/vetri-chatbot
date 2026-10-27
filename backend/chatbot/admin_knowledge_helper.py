
"""Read current active Django Admin knowledge for chatbot answers."""

import re

from django.db import DatabaseError


def _normalize(value):
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def _contains_name(message, name):
    query = _normalize(message)
    target = _normalize(name)
    if not query or not target:
        return False

    # Match a complete product or service name.
    return target in query

def _record_text(name, description="", features="", price=None, price_note=""):
    parts = [f"{name}: {description.strip()}"]
    if features and features.strip():
        parts.append(f"Features: {features.strip()}")
    if price is not None:
        formatted_price = f"{price:,.0f}" if price == price.to_integral_value() else f"{price:,.2f}"
        parts.append(f"Price: ₹{formatted_price}")
    if price_note and price_note.strip():
        parts.append(f"Pricing note: {price_note.strip()}")
    return "\n".join(parts)



def get_admin_product(message):
    """Return current active product details, including any Admin-managed price."""
    from .models import Product

    try:
        products = Product.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        for product in products:
            if _contains_name(message, product.name):
                return _record_text(
                    product.name,
                    product.description,
                    product.features,
                    product.price,
                    product.price_note,
                )
    except DatabaseError:
        return None

    return None



def get_admin_products_text(message="", website_only=False):
    """Return active Admin products for broad product or website questions."""
    from .models import Product

    website_terms = ("website", "web site", "web development", "ecommerce",
                     "e-commerce", "retail shop", "shop website", "site")
    try:
        products = Product.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        rows = []
        for product in products:
            searchable = " ".join((
                product.name or "",
                product.description or "",
                product.features or "",
            )).lower()

            if website_only and not any(term in searchable for term in website_terms):
                continue

            rows.append(_record_text(
                product.name,
                product.description,
                product.features,
                product.price,
                product.price_note,
            ))

        return "\n".join(rows) if rows else None
    except DatabaseError:
        return None

def get_admin_service(message):
    """Return current active service details."""
    from .models import Service

    try:
        services = Service.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        for service in services:
            if _contains_name(message, service.name):
                return _record_text(
                    service.name, service.description, service.features
                )
    except DatabaseError:
        return None

    return None


def get_admin_course_text(message):
    """Return current active course information."""
    from .admin_course_helper import get_admin_course

    course = get_admin_course(message)
    if not course:
        return None

    return "\n".join([
        f"Course: {course.name}",
        f"Description: {course.description}",
        f"Duration: {course.duration or 'Not specified'}",
        f"Eligibility: {course.eligibility or 'Not specified'}",
        f"Internship: {course.internship or 'Not specified'}",
        f"Additional details: {course.additional_details or 'Not specified'}",
    ])


def get_admin_company_text(message):
    """Return relevant fields from the latest active company record."""
    from .models import CompanyInformation

    query = _normalize(message)

    try:
        company = (
            CompanyInformation.objects.filter(is_active=True)
            .order_by("-updated_at")
            .first()
        )
    except DatabaseError:
        return None

    if not company:
        return None

    fields = []

    def add(label, value):
        if value and value.strip():
            fields.append(f"{label}: {value.strip()}")

    add("Company", company.company_name)
    add("Legal name", company.legal_name)
    add("Tagline", company.tagline)

    if any(word in query for word in ("mission", "vision", "goal", "purpose")):
        add("Mission", company.mission)
        add("Vision", company.vision)
    elif any(word in query for word in ("phone", "contact", "email", "address",
                                         "location", "website", "hours",
                                         "facebook", "instagram", "linkedin",
                                         "youtube", "map")):
        add("Phone", company.phone)
        add("Alternate phone", company.alternate_phone)
        add("Email", company.email)
        add("Address", company.address)
        add("Website", company.website)
        add("Business hours", company.business_hours)
        add("Facebook", company.facebook_url)
        add("Instagram", company.instagram_url)
        add("LinkedIn", company.linkedin_url)
        add("YouTube", company.youtube_url)
        add("Map", company.map_url)
    else:
        add("Description", company.description)
        add("Mission", company.mission)
        add("Vision", company.vision)

    return "\n".join(fields) if fields else None


def get_admin_faq_answer(message):
    """Return an active FAQ answer when its question closely matches."""
    from .models import FAQ

    query_words = set(_normalize(message).split())
    if not query_words:
        return None

    try:
        faqs = FAQ.objects.filter(is_active=True).order_by(
            "sort_order", "question"
        )
        best_answer = None
        best_score = 0

        for faq in faqs:
            question_words = set(_normalize(faq.question).split())
            if not question_words:
                continue

            overlap = len(query_words & question_words)
            score = overlap / len(question_words)

            # Require a meaningful match; don't answer unrelated questions.
            if overlap >= 2 and score >= 0.5 and score > best_score:
                best_score = score
                best_answer = faq.answer

        return best_answer
    except DatabaseError:
        return None
