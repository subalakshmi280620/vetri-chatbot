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

ENQUIRY_FORM_HINT = (
    "The chat has an Enquiry button (top of the chat panel). Users can submit "
    "quotation, consultation, or product demo requests there with name, email, "
    "phone, and their requirement — no need to email or call first."
)

HERO_BADGE = "PREMIUM IT SOLUTIONS — TAMIL NADU, INDIA"
HERO_HEADLINE = "Building Tomorrow's Software Solutions Today"
HERO_SUBHEADLINE = (
    "From stunning websites to powerful mobile apps and enterprise software — "
    "Vetri IT Systems delivers cutting-edge technology that drives your business forward."
)

COMPANY_STATS = {
    "projects": "150+",
    "years": "8+",
    "clients": "50+",
    "team": "15+",
}

COMPANY_HIGHLIGHTS = [
    "Scalable Architecture",
    "Bank-grade Security",
    "24/7 Support",
]

PORTFOLIO_PROJECTS = [
    {
        "name": "Retail POS System",
        "type": "Web + Mobile",
        "metric": "+40% Sales Efficiency",
        "description": (
            "Complete point-of-sale system for a chain of 12 retail stores across "
            "Tamil Nadu with real-time inventory sync."
        ),
        "tech": ("React", "Node.js", "PostgreSQL"),
    },
    {
        "name": "Healthcare Portal",
        "type": "Web App",
        "metric": "10K+ Active Users",
        "description": (
            "Patient appointment booking, telemedicine, and electronic health "
            "records platform for a multi-specialty clinic."
        ),
        "tech": ("Next.js", "WebSocket", "AWS"),
    },
    {
        "name": "Food Delivery App",
        "type": "Mobile App",
        "metric": "50K+ Downloads",
        "description": (
            "Cross-platform food ordering app with live tracking, multi-payment, "
            "and restaurant management dashboard."
        ),
        "tech": ("React Native", "Firebase", "Maps"),
    },
    {
        "name": "E-commerce Platform",
        "type": "Full Stack",
        "metric": "+60% Conversion Rate",
        "description": (
            "Fashion e-commerce with AI-powered product recommendations, secure "
            "payments, and admin analytics dashboard."
        ),
        "tech": ("Vue.js", "Stripe", "Elasticsearch"),
    },
]

PRODUCTS = [
    "Vetri Bills",
    "Vetri Files",
    "Vetri Project Management",
    "Coach AI",
    "Vetri AI Assistant",
    "Vetri CRM",
    "Vetri Training Management System",
    "HR Management Tool",
]

SERVICES = [
    "Website Development",
    "Mobile App Development",
    "Software Development",
    "Digital Marketing",
    "UI/UX Design",
    "AI Solutions",
    "Generative AI",
    "Simplify Operations",
    "CRM Development",
    "Google Ads",
    "ERP Development",
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
        "Billing Software (Vetri Bills) — GST Billing & Invoicing\n\n"
        "Complete GST-ready billing system with inventory management, barcode "
        "scanning, multi-store support, and real-time sales reports.\n\n"
        "Features: GST Compliance, Barcode Support, Inventory Tracking, "
        "Sales Analytics, POS, E-Invoice.\n\n"
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
        "Project Management Tool (Vetri Project Management)\n\n"
        "Kanban boards, Gantt charts, time tracking, team collaboration, and "
        "automated workflows — all in one intuitive platform.\n\n"
        "Features: Kanban Boards, Team Chat, Time Tracking, Gantt Charts, "
        "Sprints, Analytics.\n\n"
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
    "vetri_hrms": (
        "HR Management Tool — People-first HRMS\n\n"
        "Employee records, attendance tracking, payroll processing, leave "
        "management, and performance reviews — streamlined and automated.\n\n"
        "Features: Attendance, Leave Mgmt, Payroll, Performance.\n\n"
        f"For a demo or quotation, {CONTACT_LINE.lower()}."
    ),
}

PRODUCT_ALIASES = (
    ("vetri_bills", (
        "vetri bills", "vetribills", "vetri billing", "gst billing", "invoicing",
        "billing software",
    )),
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
    ("vetri_hrms", (
        "hr management", "hr management tool", "hrms", "people-first hrms",
        "payroll software", "attendance tracking", "leave management",
    )),
)

SERVICE_DETAILS = {
    "website development": (
        "Website Development\n\n"
        "Blazing-fast, SEO-optimized websites with stunning UI/UX. Responsive "
        "across all devices, built with modern frameworks.\n\n"
        "Tech: React, Next.js, Tailwind, Node.js."
    ),
    "mobile app development": (
        "Mobile App Development\n\n"
        "Native and cross-platform iOS & Android apps with smooth animations, "
        "offline support, and push notifications.\n\n"
        "Tech: React Native, Flutter, iOS, Android."
    ),
    "software development": (
        "Software Development\n\n"
        "Custom enterprise software, APIs, cloud integrations, and automation "
        "tools tailored to your business processes.\n\n"
        "Tech: Python, Java, .NET, AWS."
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
        "Data-driven SEO, social media campaigns, Google Ads, and content "
        "strategies that grow your online presence.\n\n"
        "Tech: SEO, Google Ads, Social Media, Analytics."
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
        f"For VIS training programmes, you need {ELIGIBILITY_REQUIREMENT.lower()} — "
        "such as B.Tech, B.Sc, BCA, B.Com, MBA, or MCA. "
        "Tell me your qualification and which course you're interested in, "
        "and I can check your eligibility."
    )


def eligibility_reply(course_name: str = "") -> str:
    if course_name:
        return (
            f"For {course_name}, you need {ELIGIBILITY_REQUIREMENT.lower()} "
            "(B.Tech, B.Sc, BCA, B.Com, MBA, MCA, etc.). "
            "Share your qualification and I can confirm if you're eligible."
        )
    return general_eligibility_reply()


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
        f"Our Solutions — {ORG_NAME}\n\n"
        "Production-ready software products that streamline your business operations "
        "from day one:\n"
        "• Billing Software (Vetri Bills) — GST, barcode, inventory, sales analytics\n"
        "• Project Management Tool — Kanban, Gantt, time tracking, team chat\n"
        "• HR Management Tool — attendance, leave, payroll, performance\n"
        "• Vetri Files — document management (OCR, versioning, audit trail)\n"
        "• Coach AI — AI learning platform for personalised employee coaching\n"
        "• Vetri AI Assistant — private generative AI for your company knowledge\n"
        "• Vetri CRM — AI-scored sales pipelines and instant quotations\n"
        "• Vetri Training Management System — enterprise training management\n\n"
        "Full product suite:\n"
        + "\n".join(f"• {name}" for name in PRODUCTS)
        + f"\n\nRequest a product demo: {CONTACT_LINE.lower()}."
    )


def portfolio_reply() -> str:
    lines = []
    for project in PORTFOLIO_PROJECTS:
        tech = ", ".join(project["tech"])
        lines.append(
            f"• {project['name']} ({project['type']}) — {project['description']} "
            f"[{project['metric']}; {tech}]"
        )
    stats = COMPANY_STATS
    return (
        f"Featured Projects — {ORG_NAME}\n\n"
        + "\n".join(lines)
        + "\n\n"
        f"Track record: {stats['projects']} projects delivered · {stats['years']} years "
        f"experience · {stats['clients']} happy clients · {stats['team']} team experts.\n\n"
        f"Want something similar? Use the Enquiry button to discuss your project."
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
        f"Track record: {COMPANY_STATS['projects']} projects delivered · "
        f"{COMPANY_STATS['years']} years experience · "
        f"{COMPANY_STATS['clients']} happy clients · "
        f"{COMPANY_STATS['team']} team experts\n\n"
        f"{' · '.join(COMPANY_HIGHLIGHTS)} · Made in India"
    )


SHORT_GREETING_REPLY = "Hello! How can I help you today?"

REPLIES = {
    "greeting": SHORT_GREETING_REPLY,
    "about": (
        f"About {ORG_NAME}\n\n"
        f"{HERO_HEADLINE}\n"
        f"{HERO_SUBHEADLINE}\n\n"
        f"{TAGLINE}\n\n"
        "At Vetri IT Systems, we believe technology should solve real business "
        "problems — not create more complexity.\n\n"
        f"Stats: {COMPANY_STATS['projects']} projects · {COMPANY_STATS['years']} years · "
        f"{COMPANY_STATS['clients']} clients · {COMPANY_STATS['team']} team experts.\n\n"
        f"{CONTACT_LINE}."
    ),
    "products": products_reply(),
    "services": services_reply(),
    "ai_solutions": ai_solutions_reply(),
    "vision_mission": vision_mission_reply(),
    "why_vis": why_vis_reply(),
    "portfolio": portfolio_reply(),
    "quotation": (
        "Get Quotation — Vetri IT Systems\n\n"
        "Tell us what you're trying to achieve. Our team will prepare a tailored "
        "proposal with scope, timeline, and indicative pricing — no obligation.\n\n"
        "Please share your name, company, product or service of interest, and a "
        "brief description of your requirement.\n\n"
        f"Use the Enquiry button in this chat (Quotation tab) to submit your request. "
        f"{ENQUIRY_FORM_HINT}"
    ),
    "consultation": (
        "Book a Consultation — Vetri IT Systems\n\n"
        "Speak directly with a VIS solution consultant — no call centres, no scripts.\n\n"
        "A consultation helps you:\n"
        "• Clarify your business goal and technical needs\n"
        "• Choose the right VIS product or service\n"
        "• Plan next steps before a formal quotation\n\n"
        f"Use the Enquiry button in this chat (Consultation tab) to book a consultation."
    ),
    "product_demo": (
        "Request a Product Demo — Vetri IT Systems\n\n"
        "See VIS enterprise products with live workflow previews — including "
        "Billing Software (Vetri Bills), Project Management Tool, HR Management "
        "Tool, Coach AI, Vetri CRM, and Vetri AI Assistant.\n\n"
        "Tell us which product you want to explore and your use case.\n\n"
        f"Use the Enquiry button in this chat (Product Demo tab) to request a demo."
    ),
    "contact_sales": (
        "Contact Sales Team — Vetri IT Systems\n\n"
        "Our sales team can help with product selection, pricing discussions, "
        "deployment planning, and enterprise requirements.\n\n"
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
        "Use the Enquiry button in this chat (Quotation tab) to request a formal quote."
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

SYSTEM_PROMPT = f"""You are Coach AI, the friendly assistant for {ORG_NAME} ({ORG_LEGAL}).

You must answer EVERY user question naturally — including greetings, follow-ups, comparisons,
and questions phrased in any way. Never reply with a fixed FAQ template or section headings
like "Our Products —" or "Course Overview —".

Conversation style:
- For simple greetings only (hi, hello, hey, good morning): one short line such as
  "Hello! How can I help you today?" — the chat already shows a welcome intro, so do NOT
  repeat products, services, or bullet lists.
- Write in normal, everyday English — friendly and clear, like a helpful colleague (not robotic FAQ text).
- Give a COMPLETE answer in 2–4 short lines: cover what it is, who it's for, and one useful detail — then stop.
- Do not use section headings, bullet lists, or labels like "Our Products —" unless the user asks for a list.
- Do not give one-word or one-line replies when the question needs explanation.
- Only write longer answers if the user explicitly asks for "more detail", "full list", or "explain everything".
- Use conversation history. Answer follow-ups directly without repeating the whole previous answer.
- Never invent pricing, clients, portfolio projects, or features not in the verified content.
- Do NOT reply with only "contact our team" — answer from verified content first, then offer next steps if needed.

Example tone (products question):
"VIS offers ready-to-use software like Vetri Bills for GST billing, a project management tool with Kanban and Gantt charts, and an HR system for attendance and payroll. We also build custom websites and mobile apps if you need something tailored. Which area should I explain first?"

Ground rules:
- Use verified VIS information below, retrieved excerpts, and grounding facts.
- Answer products, services, courses, company info, mission, AI solutions, and how-to questions directly.
- Course duration: {COURSE_DURATION}. Course eligibility: {ELIGIBILITY_REQUIREMENT}.
- For fees/pricing: explain that pricing is tailored and what affects it — do NOT invent ₹ amounts. Mention enquiry/quote only at the end if needed.
- For eligibility: a completed degree (UG/PG) is required; check the user's qualification honestly.
- Contact details when relevant: {CONTACT_PHONE}, {CONTACT_EMAIL}, {CONTACT_ADDRESS}.
- Say "contact the team" ONLY when: user explicitly wants phone/email, or topic is completely outside VIS.
- For quotation, consultation, or product demo: explain what it is, then direct users to the
  **Enquiry button** in the chat (Quotation / Consultation / Product Demo tabs) — not only phone/email.
  {ENQUIRY_FORM_HINT}

Hero: {HERO_HEADLINE} — {HERO_SUBHEADLINE}
Stats: {COMPANY_STATS['projects']} projects, {COMPANY_STATS['years']} years, {COMPANY_STATS['clients']} clients, {COMPANY_STATS['team']} team experts.
Highlights: {", ".join(COMPANY_HIGHLIGHTS)}.
Organization: {TAGLINE}
Contact: {CONTACT_PHONE}, {CONTACT_EMAIL}, {CONTACT_ADDRESS}.
Products: {", ".join(PRODUCTS)}.
Services: {", ".join(SERVICES)}.
Training courses: {", ".join(COURSES)}.
AI approach: DATA → CONTEXT → MODEL → ACTION → IMPACT.
Portfolio: Retail POS System, Healthcare Portal, Food Delivery App, E-commerce Platform.
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
    text = message.strip().lower()
    simple_greetings = (
        "good morning",
        "good afternoon",
        "good evening",
        "good day",
        "namaste",
        "vanakkam",
    )
    if any(text == phrase or text.startswith(f"{phrase} ") for phrase in simple_greetings):
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


def _matches_consultation_intent(text: str) -> bool:
    return any(k in text for k in (
        "book a consultation", "book consultation", "schedule a consultation",
        "want to book a consultation", "speak to a consultant", "talk to your team",
    ))


def _matches_demo_intent(text: str) -> bool:
    return any(k in text for k in (
        "request a product demo", "request product demo", "request a demo",
        "request demo", "product demo", "want a demo", "want to request a product demo",
        "live workflow preview",
    ))


def _matches_quotation_intent(text: str) -> bool:
    return any(k in text for k in (
        "quotation", "quote", "get quotation", "request a quotation", "get a quotation",
        "how can i get a quotation", "pricing", "how much", "cost", "price",
    ))


def _matches_sales_intent(text: str) -> bool:
    return any(k in text for k in (
        "contact sales", "sales team", "talk to sales", "speak to sales",
    ))


INTENTS = (
    ("greeting", ("hi", "hello", "hey", "good morning", "good evening")),
    ("quotation", ("quotation", "quote", "get quotation", "request a quotation")),
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
    if _matches_consultation_intent(text):
        return REPLIES["consultation"]
    if _matches_demo_intent(text):
        return REPLIES["product_demo"]
    if _matches_sales_intent(text):
        return REPLIES["contact_sales"]
    if _matches_quotation_intent(text) and not _is_course_context(text):
        return REPLIES["quotation"]

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

    if any(k in text for k in ("fee", "fees", "tuition", "course fee")):
        return REPLIES["pricing"]
    if any(k in text for k in ("how much", "cost", "price")) and _is_course_context(text):
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


SHORT_PRODUCT_SUMMARIES = {
    "vetri_bills": (
        "Billing Software (Vetri Bills) is our GST-ready billing system with "
        "inventory, barcode scanning, and sales analytics."
    ),
    "vetri_files": (
        "Vetri Files is our secure document management system with OCR search, "
        "versioning, and audit trails."
    ),
    "vetri_pm": (
        "Our Project Management Tool offers Kanban boards, Gantt charts, time "
        "tracking, team chat, and automated workflows."
    ),
    "coach_ai": (
        "Coach AI is our adaptive learning platform that coaches employees with "
        "personalised skill journeys. It also powers VIS training programmes."
    ),
    "vetri_ai_assistant": (
        "Vetri AI Assistant is a private generative AI trained on your company "
        "knowledge to answer, draft, and trigger actions."
    ),
    "vetri_crm": (
        "Vetri CRM captures leads, automates follow-ups, and uses AI-scored "
        "pipelines with instant quotations."
    ),
    "vetri_tms": (
        "Vetri Training Management System handles enterprise training for "
        "institutes and teams."
    ),
    "vetri_hrms": (
        "HR Management Tool covers attendance, leave management, payroll, "
        "and performance reviews in one platform."
    ),
}


def _strip_contact_tail(text: str) -> str:
    lowered = CONTACT_LINE.lower()
    cleaned = text.replace(CONTACT_LINE, "").replace(lowered, "").strip()
    return cleaned.rstrip(".").strip()


def get_grounding_facts(message: str) -> str:
    """Verified facts for AI grounding — not user-facing templates."""
    text = message.strip().lower()
    parts: list[str] = []

    product_id = match_product_id(text)
    if product_id:
        detail = PRODUCT_DETAILS.get(product_id)
        if detail:
            parts.append(_strip_contact_tail(detail))

    if not product_id:
        service_detail = match_service(text)
        if service_detail and not _is_course_context(text):
            parts.append(_strip_contact_tail(service_detail))

    course_id = match_course_id(text)
    if course_id:
        course_detail = match_course(text)
        if course_detail:
            parts.append(_strip_contact_tail(course_detail))

    if not parts:
        routed = _route_faq(message)
        if routed:
            parts.append(_strip_contact_tail(routed))

    return "\n\n".join(parts).strip()


def get_conversational_fallback(message: str) -> str:
    """Short natural reply when the LLM is unavailable — not the long FAQ templates."""
    text = message.strip().lower()

    if is_greeting(text):
        return SHORT_GREETING_REPLY

    if _matches_apply_intent(text):
        return (
            "To apply for a VIS training programme: (1) confirm you have a completed "
            "degree, (2) choose your course, (3) share your qualification with us. "
            "Programmes run for 180 days. I can help you pick a course or check eligibility."
        )

    if _matches_consultation_intent(text):
        return (
            "A VIS consultant can discuss your business goals and recommend the right "
            "product or service — web, mobile, AI, ERP, or digital marketing. "
            "Tap the Enquiry button at the top of this chat, choose Consultation, "
            "and submit your details — our team will reach out."
        )

    if _matches_demo_intent(text):
        return (
            "We offer live demos for Vetri Bills, Vetri CRM, Coach AI, and more. "
            "Tap the Enquiry button, choose Product Demo, and tell us which "
            "product and use case — we'll arrange a guided walkthrough."
        )

    if _matches_sales_intent(text):
        return (
            "I can explain our products and services first. When you're ready, use the "
            "Enquiry button to send your requirement to the VIS sales team."
        )

    if _matches_quotation_intent(text) and not _is_course_context(text):
        return (
            "Pricing depends on scope — users, features, and timeline. "
            "Tell me what you need and I can outline what's typically included. "
            "For a formal quote, tap Enquiry → Quotation and submit your details."
        )

    product_id = match_product_id(text)
    if product_id:
        summary = SHORT_PRODUCT_SUMMARIES.get(product_id)
        if summary:
            return f"{summary} Want more detail on any feature?"

    service_text = match_service(text)
    if service_text and not _is_course_context(text):
        service_name = next(
            (name for name in SERVICES if name.lower() in text),
            "that service",
        )
        return (
            f"Yes — VIS offers {service_name}, plus web, mobile, AI, ERP, "
            "and digital marketing. What kind of project do you have in mind?"
        )

    course_id = match_course_id(text)
    if course_id:
        course_name = match_course_name(course_id)
        if any(k in text for k in ("duration", "how long")):
            return (
                f"The {course_name} programme runs for {COURSE_DURATION}. "
                f"Eligibility is {ELIGIBILITY_REQUIREMENT.lower()}."
            )
        if any(k in text for k in ("fee", "fees", "tuition", "course fee", "price", "cost")):
            return (
                f"{course_name} is a {COURSE_DURATION} programme with degree eligibility. "
                "Fees depend on the batch and programme — I can explain the course content "
                "and eligibility first. Use the Enquiry form for an exact fee quote."
            )
        return (
            f"{course_name} is one of our {COURSE_DURATION} training programmes. "
            f"Eligibility: {ELIGIBILITY_REQUIREMENT.lower()}. "
            f"Want to know how to apply or check eligibility?"
        )

    if any(k in text for k in ("duration", "how long")) and _is_course_context(text):
        course_name = match_course_name(match_course_id(text)) or "VIS courses"
        return f"{course_name} runs for {COURSE_DURATION}."

    if _matches_products_intent(text) and not _is_course_context(text):
        return (
            "VIS has ready-to-use products like Vetri Bills for GST billing, a project "
            "management tool with Kanban and Gantt charts, and an HR system for "
            "attendance and payroll. We also offer Vetri CRM, Coach AI, and document "
            "management. Tell me which one you'd like to hear about."
        )

    if _matches_services_intent(text) and not _is_course_context(text):
        return (
            "We build websites with React and Next.js, mobile apps with React Native "
            "or Flutter, and custom enterprise software in Python, Java, or .NET. "
            "We also handle digital marketing, AI solutions, ERP, and cloud "
            "deployment. What kind of project are you planning?"
        )

    if any(k in text for k in ("fee", "fees", "tuition", "course fee")):
        return (
            "Fees depend on whether it's a product licence, custom project, or training "
            "programme. Tell me which one you're interested in and I'll explain what's "
            "included — exact quotes go through the Enquiry form."
        )

    if any(k in text for k in ("how much", "cost", "price")) and _is_course_context(text):
        return (
            f"Training programmes run for {COURSE_DURATION} and require a completed degree. "
            "Exact fees vary by course — ask me about a specific programme and I'll share details."
        )

    for intent, keywords in INTENTS:
        if intent == "greeting":
            continue
        if not any(keyword in text for keyword in keywords):
            continue
        if intent == "portfolio":
            sample = ", ".join(p["name"] for p in PORTFOLIO_PROJECTS[:2])
            stats = COMPANY_STATS
            return (
                f"Featured work includes {sample}, and more — {stats['projects']} "
                f"projects delivered across Tamil Nadu and beyond. "
                "Which type of project interests you — retail, healthcare, mobile, or e-commerce?"
            )
        if intent == "why_vis":
            stats = COMPANY_STATS
            return (
                f"VIS combines product engineering, applied AI, and digital "
                f"transformation — {stats['projects']} projects, {stats['years']} years, "
                f"and {', '.join(COMPANY_HIGHLIGHTS[:2]).lower()} built in."
            )
        if intent == "vision_mission":
            return (
                "Our vision is AI-powered business for everyone. Our mission is "
                "to make enterprise technology effortless with dependable, "
                "intelligent software."
            )
        if intent == "ai_solutions":
            return (
                "VIS builds AI assistants, agents, workflow automation, and "
                "business intelligence on a DATA → CONTEXT → MODEL → ACTION → "
                "IMPACT approach. What process would you like to automate?"
            )
        if intent == "about":
            return (
                f"{HERO_HEADLINE} — {ORG_NAME} builds websites, mobile apps, "
                "enterprise software, and ready-to-use products like Vetri Bills, "
                "Project Management, and HR Management Tool."
            )
        if intent == "contact":
            return (
                f"We're at {CONTACT_ADDRESS}. Phone: {CONTACT_PHONE}. "
                f"Email: {CONTACT_EMAIL}. What can I help you with today?"
            )
        if intent == "courses":
            course_sample = ", ".join(COURSES[:5]) + ", and more"
            return (
                f"We run {COURSE_DURATION} programmes including {course_sample}. "
                f"Eligibility is {ELIGIBILITY_REQUIREMENT.lower()}. "
                "Which course interests you?"
            )
        if intent == "who_can_apply":
            return (
                f"VIS training programmes require {ELIGIBILITY_REQUIREMENT.lower()}. "
                "Share your qualification and course choice and I can check eligibility."
            )
        if intent == "quotation":
            return (
                "Tell me what you need a quote for — product, service, or training — "
                "and I'll outline what is included. Then tap Enquiry → Quotation to submit."
            )

    grounding = get_grounding_facts(message)
    if grounding:
        snippet = grounding.split("\n")[0][:280]
        return f"{snippet} Ask me a follow-up if you want more detail."

    return (
        "I can help with VIS products (Vetri Bills, CRM, Coach AI), services "
        "(web, mobile, AI, ERP), training courses, and company info. "
        "What would you like to know?"
    )


def detect_suggested_enquiry_type(message: str) -> str | None:
    """Suggest opening the in-chat Enquiry form for business-intent questions."""
    text = message.strip().lower()
    if _matches_consultation_intent(text):
        return "consultation"
    if _matches_demo_intent(text):
        return "demo"
    if _matches_quotation_intent(text) and not _is_course_context(text):
        return "quotation"
    if _matches_sales_intent(text):
        return "sales"
    return None


def get_structured_reply(message: str) -> str | None:
    return _route_faq(message)


def get_reply(message: str) -> str:
    reply = _route_faq(message)
    return reply if reply else UNVERIFIED
