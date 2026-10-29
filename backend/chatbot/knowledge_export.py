
"""Export verified static and Admin-managed VIS knowledge for chatbot retrieval."""

from . import knowledge as kb

EXPORT_VERSION = "2"


def _chunk(source: str, section: str, text: str, index: int) -> dict:
    cleaned = " ".join(str(text).split()).strip()
    return {
        "source": source,
        "section": section,
        "text": cleaned,
        "index": index,
    }


def export_knowledge_chunks() -> list[dict]:
    """Export static facts and active records managed through Django Admin."""
    chunks: list[dict] = []
    index = 0

    def add(source: str, section: str, text: str) -> None:
        nonlocal index
        if not str(text).strip():
            return
        chunks.append(_chunk(source, section, text, index))
        index += 1

    # Existing verified knowledge.py facts (preserved).
    add(
        "knowledge.py",
        "company",
        f"{kb.ORG_NAME} ({kb.ORG_LEGAL})\n"
        f"Tagline: {kb.TAGLINE}\n"
        f"Phone: {kb.CONTACT_PHONE}\n"
        f"Email: {kb.CONTACT_EMAIL}\n"
        f"Address: {kb.CONTACT_ADDRESS}\n"
        f"Website: {kb.CONTACT_WEBSITE}\n"
        f"Stats: {kb.COMPANY_STATS['projects']} projects, "
        f"{kb.COMPANY_STATS['years']} years, "
        f"{kb.COMPANY_STATS['clients']} clients, "
        f"{kb.COMPANY_STATS['team']} team members.\n"
        f"Highlights: {', '.join(kb.COMPANY_HIGHLIGHTS)}.",
    )

    add(
        "knowledge.py",
        "products_overview",
        "VIS software products:\n" + "\n".join(f"• {name}" for name in kb.PRODUCTS),
    )
    for product_id, detail in kb.PRODUCT_DETAILS.items():
        add("knowledge.py", f"product:{product_id}", detail)

    add(
        "knowledge.py",
        "services_overview",
        "VIS services:\n" + "\n".join(f"• {name}" for name in kb.SERVICES),
    )
    for service_name, detail in kb.SERVICE_DETAILS.items():
        add("knowledge.py", f"service:{service_name}", detail)

    add(
        "knowledge.py",
        "courses_overview",
        f"VIS training programmes (duration: {kb.COURSE_DURATION}, "
        f"internship: {kb.COURSE_INTERNSHIP} with every course, "
        f"eligibility: {kb.ELIGIBILITY_REQUIREMENT}):\n"
        + "\n".join(f"• {name}" for name in kb.COURSES)
        + "\nExplain the course first. Enroll in chat when the user wants to join. "
        "No website sign-in.",
    )
    for course_id, detail in kb.COURSE_DETAILS.items():
        add("knowledge.py", f"course:{course_id}", detail)

    for project in kb.PORTFOLIO_PROJECTS:
        tech = ", ".join(project["tech"])
        add(
            "knowledge.py",
            f"portfolio:{project['name']}",
            f"{project['name']} ({project['type']}) — {project['metric']}\n"
            f"{project['description']}\nTech: {tech}.",
        )

    add(
        "knowledge.py",
        "enquiry",
        f"Contact VIS: {kb.CONTACT_PHONE}, {kb.CONTACT_EMAIL}, "
        f"{kb.CONTACT_WEBSITE}. {kb.ENQUIRY_FORM_HINT}",
    )

    # Admin records are loaded at runtime so Admin edits can reach retrieval.
    # Local imports avoid loading models before Django is ready.
    try:
        from django.db import DatabaseError
        from .models import CompanyInformation, Course, FAQ, Product, Service

        company = (
            CompanyInformation.objects.filter(is_active=True)
            .order_by("-updated_at")
            .first()
        )
        if company:
            fields = [
                ("Company", company.company_name),
                ("Legal name", company.legal_name),
                ("Tagline", company.tagline),
                ("Description", company.description),
                ("Mission", company.mission),
                ("Vision", company.vision),
                ("Phone", company.phone),
                ("Alternate phone", company.alternate_phone),
                ("Email", company.email),
                ("Address", company.address),
                ("Website", company.website),
                ("Business hours", company.business_hours),
                ("Facebook", company.facebook_url),
                ("Instagram", company.instagram_url),
                ("LinkedIn", company.linkedin_url),
                ("YouTube", company.youtube_url),
                ("Map", company.map_url),
            ]
            text = "\n".join(f"{label}: {value}" for label, value in fields if value)
            add("admin:company", "company", text)

        for product in Product.objects.filter(is_active=True):
            add(
                "admin:product",
                f"product:{product.name}",
                f"Product: {product.name}\n"
                f"Description: {product.description}\n"
                f"Features: {product.features}\n"
                f"Price: {product.price if product.price is not None else 'Not specified'}\n"
                f"Price note: {product.price_note}",
            )

        for service in Service.objects.filter(is_active=True):
            add(
                "admin:service",
                f"service:{service.name}",
                f"Service: {service.name}\n"
                f"Description: {service.description}\n"
                f"Features: {service.features}",
            )

        for course in Course.objects.filter(is_active=True):
            add(
                "admin:course",
                f"course:{course.name}",
                f"Course: {course.name}\n"
                f"Description: {course.description}\n"
                f"Duration: {course.duration or 'Not specified'}\n"
                f"Eligibility: {course.eligibility or 'Not specified'}\n"
                f"Internship: {course.internship or 'Not specified'}\n"
                f"Additional details: {course.additional_details}",
            )

        for faq in FAQ.objects.filter(is_active=True):
            add(
                "admin:faq",
                f"faq:{faq.category or 'general'}",
                f"Question: {faq.question}\nAnswer: {faq.answer}",
            )

    except DatabaseError:
        # Keep static knowledge available if Admin tables cannot be queried.
        pass

    return chunks
