"""Export verified knowledge.py facts as indexable text chunks for vector RAG."""

from . import knowledge as kb

EXPORT_VERSION = "1"


def _chunk(source: str, section: str, text: str, index: int) -> dict:
    cleaned = " ".join(text.split()).strip()
    return {
        "source": source,
        "section": section,
        "text": cleaned,
        "index": index,
    }


def export_knowledge_chunks() -> list[dict]:
    """Structured VIS facts from knowledge.py (single source of truth)."""
    chunks: list[dict] = []
    index = 0

    def add(section: str, text: str) -> None:
        nonlocal index
        if not text.strip():
            return
        chunks.append(_chunk("knowledge.py", section, text, index))
        index += 1

    add(
        "company",
        f"{kb.ORG_NAME} ({kb.ORG_LEGAL})\n"
        f"Tagline: {kb.TAGLINE}\n"
        f"Phone: {kb.CONTACT_PHONE}\n"
        f"Email: {kb.CONTACT_EMAIL}\n"
        f"Address: {kb.CONTACT_ADDRESS}\n"
        f"Stats: {kb.COMPANY_STATS['projects']} projects, "
        f"{kb.COMPANY_STATS['years']} years, "
        f"{kb.COMPANY_STATS['clients']} clients, "
        f"{kb.COMPANY_STATS['team']} team members.\n"
        f"Highlights: {', '.join(kb.COMPANY_HIGHLIGHTS)}.",
    )

    add(
        "products_overview",
        "VIS software products:\n" + "\n".join(f"• {name}" for name in kb.PRODUCTS),
    )

    for product_id, detail in kb.PRODUCT_DETAILS.items():
        add(f"product:{product_id}", detail)

    add(
        "services_overview",
        "VIS services:\n" + "\n".join(f"• {name}" for name in kb.SERVICES),
    )

    for service_name, detail in kb.SERVICE_DETAILS.items():
        add(f"service:{service_name}", detail)

    add(
        "courses_overview",
        f"VIS training programmes (duration: {kb.COURSE_DURATION}, "
        f"internship: {kb.COURSE_INTERNSHIP} with every course, "
        f"eligibility: {kb.ELIGIBILITY_REQUIREMENT}):\n"
        + "\n".join(f"• {name}" for name in kb.COURSES)
        + "\nExplain the course first. Enroll in chat when the user wants to join. No website sign-in.",
    )
    add(
        "website_packages",
        f"Ecommerce website package: {kb.ECOMMERCE_WEBSITE_PRICE}. "
        f"Small retail shop website: {kb.RETAIL_SHOP_WEBSITE_PRICE}. "
        "These are the only fixed website prices. Other work needs a quotation.",
    )

    for course_id, detail in kb.COURSE_DETAILS.items():
        add(f"course:{course_id}", detail)

    for project in kb.PORTFOLIO_PROJECTS:
        tech = ", ".join(project["tech"])
        add(
            f"portfolio:{project['name']}",
            f"{project['name']} ({project['type']}) — {project['metric']}\n"
            f"{project['description']}\nTech: {tech}.",
        )

    add(
        "enquiry",
        f"Contact VIS: {kb.CONTACT_PHONE}, {kb.CONTACT_EMAIL}. "
        f"{kb.ENQUIRY_FORM_HINT}",
    )

    return chunks
