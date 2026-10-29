
"""Read current active Django Admin knowledge for chatbot answers."""

import re
from decimal import Decimal

from django.db import DatabaseError


def _normalize(value):
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def _contains_name(message, name):
    query = _normalize(message)
    target = _normalize(name)
    if not query or not target:
        return False

    # Match a complete product or service name.
    return f" {target} " in f" {query} "

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


def _price_text(product):
    amount = (
        f"₹{product.price:,.0f}"
        if product.price == product.price.to_integral_value()
        else f"₹{product.price:,.2f}"
    )
    if product.price_note.strip():
        amount = f"{amount} ({product.price_note.strip()})"
    details = [f"{product.name} is listed at {amount}."]
    if product.description.strip():
        details.append(product.description.strip())
    if product.features.strip():
        details.append(f"Features: {product.features.strip()}")
    return " ".join(details)


def _budget_amount(message):
    text = (message or "").lower().replace(",", "")
    patterns = (
        r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d{1,2})?)",
        r"\b(\d+(?:\.\d{1,2})?)\s*(?:rupees?|rs\.?|inr)\b",
        r"\b(?:under|below|within|budget(?:\s+of)?)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return Decimal(match.group(1))
    return None


def get_admin_pricing_reply(message, website_offer=None):
    """Answer pricing questions only from active Admin product prices."""
    from .models import Product, Service

    text = (message or "").lower()
    if "course" in text or "training" in text:
        return None

    asks_price = website_offer or any(term in text for term in (
        "price", "pricing", "cost", "how much", "cheapest", "lowest",
        "least expensive", "most affordable", "budget", "under ", "below ",
        "within ", "cheap", "affordable", "rate",
    ))
    if not asks_price:
        return None

    try:
        active_products = list(
            Product.objects.filter(is_active=True).order_by("sort_order", "name")
        )
        services = list(
            Service.objects.filter(is_active=True).order_by("sort_order", "name")
        )
        from .knowledge import match_product_id

        known_product_question = bool(match_product_id(message))
    except DatabaseError:
        return (
            "I can't verify current Admin pricing data right now, so I won't guess. "
            "Please try again later or request a quotation through Enquiry."
        )

    catalog_terms = (
        "product", "products", "service", "services", "website", "web site",
        "webpage", "web page", "online store", "online shop", "ecommerce",
        "e-commerce", "retail shop", "software", "app", "option", "options",
        "cheapest", "lowest", "least expensive", "affordable", "budget",
    )
    named_admin_item = any(
        _contains_name(message, item.name)
        for item in (*active_products, *services)
    )
    if not (
        website_offer
        or known_product_question
        or named_admin_item
        or any(term in text for term in catalog_terms)
    ):
        return None

    matched_service = next(
        (service for service in services if _contains_name(message, service.name)),
        None,
    )
    if matched_service:
        return (
            f"{matched_service.name} is listed in Admin, but no confirmed price "
            "is currently recorded for this service."
        )
    if "service" in text or "services" in text:
        return "No confirmed service prices are currently recorded in Admin."

    matched_product = next(
        (item for item in active_products if _contains_name(message, item.name)),
        None,
    )
    if matched_product:
        if matched_product.price is None:
            return (
                f"{_record_text(matched_product.name, matched_product.description, matched_product.features)}\n"
                "No confirmed price is currently recorded for this product."
            )
        active_products = [matched_product]

    if website_offer or any(term in text for term in (
        "website", "web site", "webpage", "web page", "online store", "online shop",
    )):
        website_terms = ("website", "web site", "web development", "ecommerce",
                         "e-commerce", "retail shop", "shop website", "site")
        active_products = [
            item for item in active_products
            if any(
                term in " ".join((item.name, item.description, item.features)).lower()
                for term in website_terms
            )
        ]

    if website_offer == "ecommerce":
        active_products = [
            item for item in active_products
            if any(term in " ".join((item.name, item.description, item.features)).lower()
                   for term in ("ecommerce", "e-commerce", "online store", "online shop"))
        ]
    elif website_offer == "retail":
        active_products = [
            item for item in active_products
            if any(term in " ".join((item.name, item.description, item.features)).lower()
                   for term in ("retail", "small shop", "kirana"))
        ]

    products = sorted(
        (item for item in active_products if item.price is not None),
        key=lambda item: (item.price, item.sort_order, item.name.lower()),
    )
    if not products:
        return (
            "I don't have an active Admin product with a confirmed price for that "
            "request, so I can't verify a price. Please use Enquiry to request a quotation."
        )

    budget = _budget_amount(message)
    if budget is not None:
        within_budget = [item for item in products if item.price <= budget]
        if within_budget:
            return (
                f"These current Admin-listed options fit within your ₹{budget:,.0f} budget:\n"
                + "\n\n".join(_price_text(item) for item in within_budget)
            )
        cheapest = products[0]
        return (
            f"I don't see a current Admin-listed option at or below ₹{budget:,.0f}. "
            f"The lowest-priced matching option currently listed is {_price_text(cheapest)}"
        )

    if any(term in text for term in (
        "cheapest", "lowest", "least expensive", "most affordable", "budget friendly",
    )):
        lowest_price = products[0].price
        cheapest = [item for item in products if item.price == lowest_price]
        return (
            "The lowest-priced current Admin option"
            + ("s are:\n" if len(cheapest) > 1 else " is ")
            + "\n\n".join(_price_text(item) for item in cheapest)
        )

    return "Current prices from Admin-listed products:\n" + "\n\n".join(
        _price_text(item) for item in products
    )


def _get_admin_product_record(message):
    from .models import Product

    try:
        products = Product.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        for product in products:
            if _contains_name(message, product.name):
                return product
    except DatabaseError:
        return None

    return None


def get_admin_product(message):
    """Return current active product facts for grounding."""
    product = _get_admin_product_record(message)
    if not product:
        return None

    return _record_text(
        product.name,
        product.description,
        product.features,
        product.price,
        product.price_note,
    )


def get_admin_product_reply(message):
    """Answer a named product question with only relevant active Admin details."""
    product = _get_admin_product_record(message)
    if not product:
        return None

    reply = f"{product.name}: {product.description.strip()}".strip()
    query = _normalize(message)
    if product.features.strip() and any(
        term in query for term in ("feature", "capability", "include", "what does", "how does", "tell me about", "details")
    ):
        reply += f" Key features include: {product.features.strip()}"
    return reply



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


def get_admin_services_text():
    """Return all active Admin-managed services for broad service questions."""
    from .models import Service

    try:
        services = Service.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        rows = [
            _record_text(service.name, service.description, service.features)
            for service in services
        ]
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


def get_inactive_admin_content_reply(message):
    """Prevent disabled Admin records from being repeated by static KB or AI."""
    from .models import CompanyInformation, FAQ, Product, Service

    query = _normalize(message)
    if not query:
        return None

    try:
        for model, label in ((Product, "product"), (Service, "service")):
            for item in model.objects.filter(is_active=False).only("name"):
                if _contains_name(message, item.name):
                    return (
                        f"{item.name} is no longer active in Admin, so I can't verify "
                        f"current {label} details."
                    )

        query_words = set(query.split())
        for faq in FAQ.objects.filter(is_active=False).only("question"):
            question_words = set(_normalize(faq.question).split())
            overlap = len(query_words & question_words)
            if question_words and overlap >= 2 and overlap / len(question_words) >= 0.5:
                return "I can't find a current active Admin answer for that question."

        from .knowledge import (
            _matches_about_intent,
            _matches_contact_intent,
            _matches_vision_mission_intent,
            _matches_why_vis_intent,
        )

        company_question = any((
            _matches_about_intent(query),
            _matches_contact_intent(query),
            _matches_vision_mission_intent(query),
            _matches_why_vis_intent(query),
        ))
        if (
            company_question
            and CompanyInformation.objects.filter(is_active=False).exists()
            and not CompanyInformation.objects.filter(is_active=True).exists()
        ):
            return "Current company information is not available in active Admin records."
    except DatabaseError:
        return (
            "I can't verify current Admin content right now, so I won't repeat older details."
        )

    return None
