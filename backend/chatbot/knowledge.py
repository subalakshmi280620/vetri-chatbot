"""Answers grounded in the new VIS website Figma design — not the old live site."""

import re

ORG_NAME = "Vetri IT Systems (VIS)"
ORG_LEGAL = "Vetri IT Systems Pvt Ltd"
TAGLINE = (
    "Enterprise Software, Applied AI And Digital Transformation "
    "For Businesses That Intend To Lead Their Category."
)

CONTACT_PHONE = "+91 84381 54827"
CONTACT_EMAIL = "support@vetri-it.com"
CONTACT_ADDRESS = "Vetri Academy, Aerial Complex, Behind Bus Stand, Surandai"

CONTACT_LINE = (
    f"Please contact our team: {CONTACT_PHONE} or {CONTACT_EMAIL}"
)

PRODUCTS = [
    "Vetri Bills",
    "Vetri Files",
    "Vetri Project Management",
    "Coach AI",
    "Vetri AI Assistant",
    "Vetri CRM",
    "Vetri Training Management System",
]

SERVICES = [
    "Website Development",
    "Mobile App Development",
    "UI/UX Design",
    "AI Solutions",
    "Generative AI",
    "Simplify Operations",
    "CRM Development",
    "Google Ads",
    "ERP Development",
    "Digital Marketing",
    "SEO",
    "Meta Ads",
    "Cloud Services",
]

COURSES = [
    "Python Fullstack",
    "Prompt Engineering",
    "Java Fullstack",
    "UI/UX",
    "Software Testing",
    "Data Analytics",
    "Mobile App Development",
    "AWS & DevOps",
    "Data Science",
    "Digital Marketing",
]

COURSE_DURATION = "180 days"
ELIGIBILITY_REQUIREMENT = "Any degree completion"

DEGREE_INDICATORS = (
    "degree", "graduate", "graduation", "graduated", "bachelor", "master",
    "btech", "b.tech", "b.e", "bsc", "b.sc", "bca", "b.com", "bcom",
    "mba", "mca", "m.tech", "mtech", "engineering", "ug", "pg",
    "post graduate", "postgraduate", "completed degree", "degree holder",
    "ba ", "b.a", "ma ", "m.a", "phd", "doctorate",
)

PRODUCT_DETAILS = {
    "vetri_bills": (
        "Vetri Bills — GST Billing & Invoicing\n\n"
        "Fast, compliant billing for retail and distribution — from customer entry "
        "to GST invoice download in seconds.\n\n"
        "Features: GST Ready, POS, E-Invoice, Reports.\n\n"
        f"For a demo or quotation, {CONTACT_LINE.lower()}."
    ),
    "vetri_files": (
        "Vetri Files — Document Management\n\n"
        "Secure enterprise document vault with OCR indexing, granular permissions "
        "and a complete audit trail.\n\n"
        "Features: OCR Search, Versioning, Audit Trail, Cloud.\n\n"
        f"For a demo or quotation, {CONTACT_LINE.lower()}."
    ),
    "vetri_pm": (
        "Vetri Project Management — Project & Delivery\n\n"
        "Plan sprints, track effort and forecast delivery with resource heatmaps "
        "and real-time project health.\n\n"
        "Features: Sprints, Timesheets, Gantt, Analytics.\n\n"
        f"For a demo or quotation, {CONTACT_LINE.lower()}."
    ),
    "coach_ai": (
        "Coach AI — AI Learning Platform\n\n"
        "Adaptive AI coaching that assesses skill gaps and builds personalised "
        "learning journeys for every employee.\n\n"
        "Coach AI also supports VIS training programmes. Ask about available "
        "courses, eligibility, duration, or how to apply.\n\n"
        f"For a product demo, {CONTACT_LINE.lower()}."
    ),
    "vetri_ai_assistant": (
        "Vetri AI Assistant — Generative AI\n\n"
        "A private AI assistant trained on your company knowledge that answers, "
        "drafts and triggers real actions.\n\n"
        f"For a demo or deployment discussion, {CONTACT_LINE.lower()}."
    ),
    "vetri_crm": (
        "Vetri CRM — Sales & Customer\n\n"
        "Capture every lead, automate follow-ups and close faster with AI-scored "
        "pipelines and instant quotations.\n\n"
        f"For a demo or quotation, {CONTACT_LINE.lower()}."
    ),
    "vetri_tms": (
        "Vetri Training Management System\n\n"
        "Enterprise training management for institutes and teams.\n\n"
        f"For product details or a demo, {CONTACT_LINE.lower()}."
    ),
}

PRODUCT_ALIASES = (
    ("vetri_bills", ("vetri bills", "vetribills", "gst billing", "invoicing", "billing software")),
    ("vetri_files", ("vetri files", "vetrifiles", "document management", "document vault")),
    ("vetri_pm", (
        "vetri project management", "project management", "project & delivery",
        "project and delivery",
    )),
    ("coach_ai", ("coach ai", "coachai", "ai learning platform", "ai coaching")),
    ("vetri_ai_assistant", ("vetri ai assistant", "ai assistant", "generative ai assistant")),
    ("vetri_crm", ("vetri crm", "vetricrm", "crm software", "sales crm")),
    ("vetri_tms", (
        "vetri training management", "training management system",
        "vetri lms", "learning management",
    )),
)

SERVICE_DETAILS = {
    "website development": (
        "Website Development\n\n"
        "High-performance static and dynamic websites engineered for conversion."
    ),
    "mobile app development": (
        "Mobile App Development\n\n"
        "Native-grade Android & iOS apps with offline-first architecture."
    ),
    "ui/ux design": (
        "UI/UX Design\n\n"
        "Research-led interfaces, design systems and usability testing."
    ),
    "ai solutions": (
        "AI Solutions\n\n"
        "Custom models, assistants and agents mapped to real business KPIs.\n\n"
        "VIS AI process: DATA → CONTEXT → MODEL → ACTION → IMPACT."
    ),
    "generative ai": (
        "Generative AI\n\n"
        "Content, code and document intelligence built on secure LLM pipelines."
    ),
    "simplify operations": (
        "Simplify Operations\n\n"
        "Replace scattered tools and manual processes with one connected platform "
        "that handles billing, HR, projects and customer management."
    ),
    "crm development": (
        "CRM Development\n\n"
        "Pipeline, quotation and follow-up automation tailored to your sales motion."
    ),
    "google ads": (
        "Google Ads\n\n"
        "Search and performance-max campaigns tuned for cost per qualified lead."
    ),
    "erp development": (
        "ERP Development\n\n"
        "Inventory, production and finance modules that fit how you operate."
    ),
    "digital marketing": (
        "Digital Marketing\n\n"
        "Full-funnel campaigns with attribution you can actually trust."
    ),
    "seo": (
        "SEO\n\n"
        "Technical SEO, content strategy and authority building that compounds."
    ),
    "meta ads": (
        "Meta Ads\n\n"
        "Creative testing and re-targeting engines across Facebook & Instagram."
    ),
    "cloud services": (
        "Cloud Services\n\n"
        "Cloud architecture, deployment and managed support for modern businesses."
    ),
}

UNVERIFIED = (
    "Thank you for your question.\n\n"
    "I could not find that information in the available VIS website content.\n\n"
    f"{CONTACT_LINE}."
)


def qualification_meets_degree_requirement(qualification: str) -> bool:
    lowered = qualification.lower()
    return any(indicator in lowered for indicator in DEGREE_INDICATORS)


def duration_reply(course_name: str = "") -> str:
    topic = f" — {course_name}" if course_name else ""
    return (
        f"Course Duration{topic}\n\n"
        f"The verified course duration is {COURSE_DURATION}.\n\n"
        f"{CONTACT_LINE}."
    )


def general_eligibility_reply() -> str:
    return (
        "General Eligibility\n\n"
        f"• Requirement: {ELIGIBILITY_REQUIREMENT}.\n"
        "• Accepted examples include B.Tech, B.Sc, BCA, B.Com, MBA, MCA, and other "
        "completed undergraduate or postgraduate degrees.\n\n"
        "If you tell me your qualification and the course you are interested in, "
        "I can help check your eligibility."
    )


def eligibility_reply(course_name: str = "") -> str:
    topic = f" — {course_name}" if course_name else ""
    return (
        f"Eligibility Requirements{topic}\n\n"
        f"• Requirement: {ELIGIBILITY_REQUIREMENT}\n"
        "• Accepted examples: B.Tech, B.Sc, BCA, B.Com, MBA, MCA, or any other "
        "completed undergraduate or postgraduate degree.\n\n"
        "If you would like a personal eligibility check, please share your qualification."
    )


def course_card(name: str, extra: str = "") -> str:
    extra_block = f"\n{extra.strip()}\n" if extra else ""
    return (
        f"Course Overview — {name}\n\n"
        f"{name} is a VIS training programme supported by Coach AI — our AI Learning Platform.\n"
        f"{extra_block}\n"
        f"Duration: {COURSE_DURATION}\n"
        f"Eligibility: {ELIGIBILITY_REQUIREMENT}\n\n"
        f"For fees or enrollment, {CONTACT_LINE.lower()}."
    )


COURSE_DETAILS = {
    "java": course_card("Java Fullstack"),
    "python": course_card("Python Fullstack"),
    "prompt": course_card("Prompt Engineering"),
    "uiux": course_card("UI/UX"),
    "testing": course_card("Software Testing"),
    "analytics": course_card("Data Analytics"),
    "mobile": course_card("Mobile App Development"),
    "aws": course_card("AWS & DevOps"),
    "datascience": course_card("Data Science"),
    "marketing": course_card("Digital Marketing"),
}

COURSE_ALIASES = (
    ("java", ("javafullstack", "java fullstack", "java full stack", "java backend", "core java")),
    ("python", ("pythonfullstack", "python fullstack", "python full stack")),
    ("prompt", ("prompt engineering", "promptengineering")),
    ("uiux", ("ui/ux", "uiux", "ui ux", "ux design")),
    ("testing", ("software testing", "qa testing", "manual testing", "automation testing")),
    ("analytics", ("data analytics", "dataanalytics")),
    ("mobile", ("mobile app development", "mobileapp", "android", "flutter")),
    ("aws", ("aws", "devops", "deveops")),
    ("datascience", ("data science", "datascience")),
    ("marketing", ("digital marketing course", "digitalmarketing course")),
)

COURSE_NAMES = {
    "java": "Java Fullstack",
    "python": "Python Fullstack",
    "prompt": "Prompt Engineering",
    "uiux": "UI/UX",
    "testing": "Software Testing",
    "analytics": "Data Analytics",
    "mobile": "Mobile App Development",
    "aws": "AWS & DevOps",
    "datascience": "Data Science",
    "marketing": "Digital Marketing",
}


def products_reply() -> str:
    return (
        f"Our Products — {ORG_NAME}\n\n"
        + "\n".join(f"• {name}" for name in PRODUCTS)
        + "\n\n"
        "Enterprise products with live workflow previews:\n"
        "• Vetri Bills — GST billing & invoicing (GST Ready, POS, E-Invoice, Reports)\n"
        "• Vetri Files — document management (OCR Search, Versioning, Audit Trail, Cloud)\n"
        "• Vetri Project Management — sprints, timesheets, Gantt, analytics\n"
        "• Coach AI — AI learning platform for personalised employee coaching\n"
        "• Vetri AI Assistant — private generative AI for your company knowledge\n"
        "• Vetri CRM — AI-scored sales pipelines and instant quotations\n"
        "• Vetri Training Management System — enterprise training management\n\n"
        f"Request a product demo: {CONTACT_LINE.lower()}."
    )


def services_reply() -> str:
    lines = "\n".join(
        f"• {name} — {SERVICE_DETAILS[name.lower()].split(chr(10), 2)[-1].strip()}"
        for name in SERVICES
        if name.lower() in SERVICE_DETAILS
    )
    return (
        f"Our Services — {ORG_NAME}\n\n"
        "End-to-end capability, from idea to scale — one accountable partner across "
        "design, engineering, AI, cloud and growth.\n\n"
        f"{lines}\n\n"
        f"Book a consultation or request a quotation: {CONTACT_LINE.lower()}."
    )


def ai_solutions_reply() -> str:
    return (
        "AI Solutions — Vetri IT Systems\n\n"
        "Intelligence layered across every business process.\n\n"
        "We design AI systems that are grounded, governed and measurable — deployed "
        "inside your workflows, not bolted on beside them.\n\n"
        "Our AI process: DATA → CONTEXT → MODEL → ACTION → IMPACT\n\n"
        "Capabilities:\n"
        "• Generative AI — content, code and document generation on secure pipelines\n"
        "• Smart Productivity Tools — meeting notes, summaries and drafting\n"
        "• Business Intelligence — live dashboards and forecasting\n"
        "• AI Agents — goal-driven agents for multi-step business tasks\n"
        "• AI Assistants — domain assistants trained on your knowledge base\n"
        "• Workflow Automation — approvals, data entry and hand-offs\n"
        "• Future AI Products — new AI products on a quarterly R&D roadmap\n\n"
        f"{CONTACT_LINE}."
    )


def vision_mission_reply() -> str:
    return (
        "Mission & Vision — Vetri IT Systems\n\n"
        "Our Vision: An AI-Powered Business For Everyone\n"
        "To become the trusted AI and digital transformation partner for growing "
        "enterprises — where every process is automated, every decision is data-backed, "
        "and every team is amplified by AI.\n\n"
        "Our Mission: Make Enterprise Technology Effortless\n"
        "To deliver dependable, intelligent software that removes manual work, gives "
        "leaders real-time clarity, and lets businesses of every size compete with "
        "the very best."
    )


def why_vis_reply() -> str:
    return (
        "Why VIS — Vetri IT Systems\n\n"
        "Technology Built Around Your Business.\n\n"
        "Focus areas:\n"
        "• Digital Transformation — Process → Platform\n"
        "• Applied AI — Assistants, agents & automation\n"
        "• Engineering Depth — Web, mobile, cloud, data\n\n"
        "What sets us apart:\n"
        "• Enterprise Trust — compliance, security and support in every engagement\n"
        "• Cloud Native — scalable, secure modern cloud architectures\n"
        "• Product Mindset — seven shipped enterprise products\n"
        "• AI-first Engineering — intelligence and automation at the core\n\n"
        "Track record: 50+ projects delivered · 10+ enterprise products · "
        "20+ business clients · 10+ AI solutions · 2+ years of experience\n\n"
        "ISO-grade delivery · 24x7 support · Made in India"
    )


REPLIES = {
    "greeting": (
        f"Welcome to {ORG_NAME}.\n\n"
        "I am Coach AI, your VIS assistant. I can help with:\n"
        "• Products — Vetri Bills, Vetri Files, Vetri CRM, Coach AI, and more\n"
        "• Services — web development, AI solutions, digital marketing, ERP, and more\n"
        "• Company info — about us, mission, vision, and why VIS\n"
        "• Training courses — duration, eligibility, and how to apply\n"
        "• Contact — phone, email, address, quotations, and demos\n\n"
        "How may I assist you today?"
    ),
    "about": (
        f"About {ORG_NAME}\n\n"
        f"{TAGLINE}\n\n"
        "At Vetri IT Systems, we believe technology should solve real business "
        "problems — not create more complexity.\n\n"
        "We work with businesses to understand their goals, identify the right "
        "technology approach and build solutions that are practical, scalable and "
        "ready for the future — from custom software and digital applications to "
        "AI-powered solutions.\n\n"
        f"{CONTACT_LINE}."
    ),
    "products": products_reply(),
    "services": services_reply(),
    "ai_solutions": ai_solutions_reply(),
    "vision_mission": vision_mission_reply(),
    "why_vis": why_vis_reply(),
    "portfolio": (
        f"Portfolio — {ORG_NAME}\n\n"
        "VIS has delivered 50+ projects across enterprise software, applied AI, "
        "and digital transformation for 20+ business clients.\n\n"
        f"For portfolio details or case studies, {CONTACT_LINE.lower()}."
    ),
    "quotation": (
        "Get Quotation — Vetri IT Systems\n\n"
        "Tell us what you're trying to achieve. You'll get a tailored proposal, "
        "timeline and indicative pricing — no obligation.\n\n"
        "You can also:\n"
        "• Book a Consultation\n"
        "• Request a Product Demo\n"
        "• Contact Sales Team\n\n"
        f"Phone: {CONTACT_PHONE}\n"
        f"Email: {CONTACT_EMAIL}\n"
        f"Address: {CONTACT_ADDRESS}"
    ),
    "contact": (
        f"Contact {ORG_NAME}\n\n"
        f"• Phone: {CONTACT_PHONE}\n"
        f"• Email: {CONTACT_EMAIL}\n"
        f"• Address: {CONTACT_ADDRESS}\n\n"
        "Enquiry options:\n"
        "• Request a quotation\n"
        "• Book a consultation\n"
        "• Request a product demo\n"
        "• Contact sales team"
    ),
    "courses": (
        f"Training Courses — Coach AI / {ORG_NAME}\n\n"
        + "\n".join(f"• {name}" for name in COURSES)
        + f"\n\nDuration: {COURSE_DURATION}\n"
        f"Eligibility: {ELIGIBILITY_REQUIREMENT}\n\n"
        f"For fees or enrollment, {CONTACT_LINE.lower()}."
    ),
    "pricing": (
        "Pricing & Quotation\n\n"
        "Exact pricing depends on your product or service requirement.\n\n"
        "Tell us what you're trying to achieve and our team will share a tailored "
        "proposal, timeline and indicative pricing — no obligation.\n\n"
        f"Phone: {CONTACT_PHONE}\n"
        f"Email: {CONTACT_EMAIL}"
    ),
    "who_can_apply": general_eligibility_reply(),
    "apply": (
        "How to Apply — VIS Training Programmes\n\n"
        "Step 1: Confirm eligibility — any completed degree (UG/PG)\n"
        "Step 2: Choose your preferred course\n"
        "Step 3: Contact the VIS team with your qualification and course choice\n"
        "Step 4: Complete enrollment with VIS team guidance\n\n"
        f"Phone: {CONTACT_PHONE}\n"
        f"Email: {CONTACT_EMAIL}"
    ),
}

STRUCTURED_TRIGGERS = (
    "duration", "how long", "fee", "fees", "course", "courses", "contact", "phone",
    "email", "address", "eligib", "who can apply", "how to apply", "product", "products",
    "service", "services", "portfolio", "quotation", "quote", "consultation", "demo",
    "vision", "mission", "about", "why vis", "ai solution", "generative ai", "vetri bills",
    "vetri files", "vetri crm", "coach ai", "erp", "seo", "google ads", "meta ads",
    "cloud", "crm", "lms", "training management",
)

SYSTEM_PROMPT = f"""You are Coach AI, the official assistant for {ORG_NAME}.
Answer only from the verified VIS new website content below. Be professional and concise.
Never invent pricing, clients, or features not listed.
If unsure, direct users to {CONTACT_PHONE} or {CONTACT_EMAIL}.

Organization: {ORG_LEGAL}. {TAGLINE}
Hero: Transforming Businesses with AI-Powered Digital Solutions.
Stats: 50+ projects, 10+ enterprise products, 20+ business clients, 10+ AI solutions, 2+ years experience.
Contact: {CONTACT_PHONE}, {CONTACT_EMAIL}, {CONTACT_ADDRESS}.
Products: {", ".join(PRODUCTS)}.
Services: {", ".join(SERVICES)}.
Training courses (Coach AI): {", ".join(COURSES)}. Duration {COURSE_DURATION}. Eligibility: {ELIGIBILITY_REQUIREMENT}.
AI process: DATA → CONTEXT → MODEL → ACTION → IMPACT.
Enquiries: quotation, consultation, product demo, contact sales.
"""


def _compact(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


def match_product_id(message: str) -> str | None:
    lowered = message.lower()
    compact = _compact(message)
    for product_id, aliases in PRODUCT_ALIASES:
        for alias in aliases:
            if alias in lowered or alias.replace(" ", "") in compact:
                return product_id
    return None


def match_product(message: str) -> str | None:
    product_id = match_product_id(message)
    if not product_id:
        return None
    return PRODUCT_DETAILS.get(product_id)


def match_service(message: str) -> str | None:
    lowered = message.lower()
    for service_name, detail in SERVICE_DETAILS.items():
        if service_name in lowered:
            return f"{detail}\n\n{CONTACT_LINE}."
    return None


def match_course_id(message: str) -> str | None:
    compact = _compact(message)
    lowered = message.lower()
    for course_id, aliases in COURSE_ALIASES:
        for alias in aliases:
            if alias.replace(" ", "") in compact or alias in lowered:
                return course_id
    return None


def match_course_name(course_id: str | None) -> str:
    if not course_id:
        return ""
    return COURSE_NAMES.get(course_id, "")


def match_course(message: str) -> str | None:
    course_id = match_course_id(message)
    if not course_id:
        return None
    return COURSE_DETAILS[course_id]


def is_greeting(message: str) -> bool:
    compact = _compact(message)
    if re.fullmatch(r"(h+i+|hey+|hello+|hai+|helo+|hlo+|yo+|hai+)", compact):
        return True
    words = "".join(ch.lower() if ch.isalnum() else " " for ch in message).split()
    if not words or len(words) > 5:
        return False
    greet_words = {"hi", "hii", "hiii", "hello", "hey", "hai", "helo", "hlo", "yo"}
    return words[0] in greet_words


def _matches_products_intent(text: str) -> bool:
    return any(k in text for k in (
        "product", "products", "our product", "what products", "software product",
    ))


def _matches_services_intent(text: str) -> bool:
    return any(k in text for k in (
        "service", "services", "our service", "what services", "what do you offer",
        "explore our services", "end-to-end capability",
    ))


def _is_course_context(text: str) -> bool:
    return any(marker in text for marker in (
        "course", "training programme", "training program", "fullstack", "eligib",
        "duration", "apply for course", "admission", "degree", "enroll",
    ))


def _matches_apply_intent(text: str) -> bool:
    return any(k in text for k in (
        "how to apply", "how do i apply", "how can i apply", "application process",
        "admission process", "how to enroll", "apply for course", "apply for admission",
    ))


INTENTS = (
    ("greeting", ("hi", "hello", "hey", "good morning", "good evening")),
    ("quotation", (
        "quotation", "quote", "get quotation", "request a quotation", "pricing",
        "how much", "cost", "price", "book a consultation", "book consultation",
        "request a product demo", "request demo", "product demo", "contact sales",
    )),
    ("portfolio", ("portfolio", "portfolios", "case study", "projects delivered", "our work")),
    ("why_vis", ("why vis", "why vetri", "why choose", "what sets you apart")),
    ("vision_mission", ("vision", "mission", "mission and vision", "mission & vision")),
    ("ai_solutions", (
        "ai solution", "ai solutions", "agentic ai", "workflow automation",
        "ai agents", "ai assistant", "business intelligence",
    )),
    ("products", ("product", "products", "our product", "what products")),
    ("services", ("service", "services", "our service", "what services")),
    ("about", ("about us", "about vis", "about vetri", "who are you", "what is vis")),
    ("contact", ("contact", "phone", "email", "address", "call", "location", "where are you")),
    ("courses", (
        "courses", "which courses", "what courses", "courses available",
        "training courses", "training programmes", "training programs",
    )),
    ("who_can_apply", ("who can apply", "who can join", "who is eligible", "eligib")),
)


def _route_faq(message: str) -> str | None:
    text = message.strip().lower()

    if is_greeting(text):
        return REPLIES["greeting"]
    if _matches_apply_intent(text):
        return REPLIES["apply"]

    product_text = match_product(text)
    if product_text:
        return product_text

    service_text = match_service(text)
    if service_text and not _is_course_context(text):
        return service_text

    if match_course_id(text):
        if any(k in text for k in ("duration", "how long")):
            return duration_reply(match_course_name(match_course_id(text)))
        if any(k in text for k in ("fee", "fees", "tuition", "course fee")):
            return REPLIES["pricing"]
        course_text = match_course(text)
        if course_text:
            return course_text

    if any(k in text for k in ("duration", "how long")) and _is_course_context(text):
        return duration_reply(match_course_name(match_course_id(text)))

    if _matches_products_intent(text) and not _is_course_context(text):
        return REPLIES["products"]
    if _matches_services_intent(text) and not _is_course_context(text):
        return REPLIES["services"]

    if any(k in text for k in ("fee", "fees", "tuition", "course fee", "how much", "cost", "price")):
        return REPLIES["pricing"]

    for intent, keywords in INTENTS:
        if intent == "greeting":
            continue
        if any(keyword in text for keyword in keywords):
            if intent == "pricing" and _is_course_context(text):
                return REPLIES["pricing"]
            return REPLIES[intent]

    course_text = match_course(text)
    if course_text:
        return course_text

    return None


def get_structured_reply(message: str) -> str | None:
    return _route_faq(message)


def should_prefer_kb(message: str) -> bool:
    text = message.strip().lower()
    return (
        is_greeting(text)
        or any(trigger in text for trigger in STRUCTURED_TRIGGERS)
        or bool(match_course_id(text))
        or bool(match_product_id(text))
    )


def get_reply(message: str) -> str:
    reply = _route_faq(message)
    return reply if reply else UNVERIFIED
