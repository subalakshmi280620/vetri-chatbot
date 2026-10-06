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
COURSE_INTERNSHIP = "3 months"
ELIGIBILITY_REQUIREMENT = "Any degree completion"
# Official website packages only. Do not invent other ₹ prices.
ECOMMERCE_WEBSITE_PRICE = "₹9,999 + GST"
RETAIL_SHOP_WEBSITE_PRICE = "₹3,000 + GST"

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
        f"Internship: {COURSE_INTERNSHIP} (included with every VIS course)\n"
        f"Eligibility: {ELIGIBILITY_REQUIREMENT}\n\n"
        "Ask me about the course first. When you want to join, say enroll and "
        "I will collect your details here. You do not need a website sign-in."
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

AI_BUSY_KB_PREFIX = (
    "Our AI assistant is temporarily unavailable (high demand or API limits). "
    "Here is verified VIS information instead:\n\n"
)

AI_FULLY_UNAVAILABLE_MESSAGE = (
    "I'm having trouble reaching our AI service right now — likely due to "
    f"high demand or API limits. Please try again in a minute, or call {CONTACT_PHONE}."
)

GENERIC_FALLBACK_MARKER = (
    "I'm here to help with VIS products, services, training courses, quotes, and "
    "company info."
)

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
        f"Internship: {COURSE_INTERNSHIP} with every course\n"
        f"Eligibility: {ELIGIBILITY_REQUIREMENT}\n\n"
        "Tell me which course you want explained. Say enroll when you are ready to join."
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

SYSTEM_PROMPT = f"""You are Coach AI — a warm, friendly assistant for {ORG_NAME} ({ORG_LEGAL}).
Talk like a helpful colleague on chat: natural, human, and easy to read. Not a brochure or FAQ page.

You must answer EVERY question the user asks — any wording, follow-ups, comparisons, or casual phrasing.
Never use section headings, bullet lists, or labels like "Our Products —" unless the user asks for a list.

Voice and tone:
- Understand informal English, typos, and broken grammar — infer what the user means.
- Sound conversational: use plain English, short sentences, and a helpful tone.
- You may start with a brief friendly phrase when it fits ("Sure!", "Good question.", "Happy to help.") — but keep it natural, not cheesy.
- Write COMPLETE sentences. Never stop mid-thought or mid-number.
- __REPLY_LENGTH_GUIDANCE__
- Use conversation history — answer follow-ups directly without repeating your last reply word-for-word.
- For hi/hello only: one line like "Hello! How can I help you today?" — no product lists (welcome card already shown).

Answer focus by topic (use different angles — do not repeat the same intro for every question):
- What is VIS: who they are and what they offer (products + services).
- Why choose VIS: trust, AI-first engineering, track record, benefits — not the same text as "what is VIS".
- Mission/vision: vision and mission only.
- Portfolio: example projects and outcomes.
- Products: ready-made software catalogue. Services: custom development work.
- Quotation / consultation / demo: explain that specific next step; mention the Enquiry button.

Stats — write exactly when relevant: {COMPANY_STATS['projects']} projects, {COMPANY_STATS['years']} years,
{COMPANY_STATS['clients']} clients, {COMPANY_STATS['team']} team experts. Never truncate (e.g. never write "15" alone for projects).

Never invent pricing, clients, or features. Do not reply with only "contact our team" — answer first, then offer next steps.

Example (products):
"Sure — VIS has ready-made tools like Vetri Bills for GST billing, plus project management and HR software. We also build custom websites and apps if you need something tailored. Which one should I tell you more about?"

Example (why choose us):
"Great question — teams pick VIS for enterprise-grade delivery, AI-first product engineering, and a solid track record: {COMPANY_STATS['projects']} projects over {COMPANY_STATS['years']}, with products like Vetri Bills and Coach AI already built. What are you looking to solve?"

Ground rules:
- Use verified VIS information below, retrieved excerpts, and grounding facts.
- Answer products, services, courses, company info, mission, AI solutions, and how-to questions directly.
- Course duration: {COURSE_DURATION}. Every course includes a {COURSE_INTERNSHIP} internship. Course eligibility: {ELIGIBILITY_REQUIREMENT}.
- Explain a course first. Only when the user wants to join, ask them to enroll in this chat. Do not ask them to sign in. There is no website login.
- Official website prices only: ecommerce website {ECOMMERCE_WEBSITE_PRICE}; small retail shop website {RETAIL_SHOP_WEBSITE_PRICE}. Do NOT invent any other ₹ amount.
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

REPLY_STYLE_BRIEF = "brief"
REPLY_STYLE_DETAILED = "detailed"
VALID_REPLY_STYLES = {REPLY_STYLE_BRIEF, REPLY_STYLE_DETAILED}

_REPLY_LENGTH_LINES = {
    REPLY_STYLE_BRIEF: (
        "- Give a short answer in 1–2 tight sentences (about 50 words max). "
        "Include the key verified facts (price, duration, eligibility, product name) — do not skip them."
    ),
    REPLY_STYLE_DETAILED: (
        "- Give a fuller answer in 2–4 short lines, then stop. End with a gentle follow-up question when helpful."
    ),
}

def normalize_reply_style(value) -> str:
    style = str(value or REPLY_STYLE_BRIEF).strip().lower()
    return style if style in VALID_REPLY_STYLES else REPLY_STYLE_BRIEF


def get_system_prompt(reply_style: str = REPLY_STYLE_BRIEF) -> str:
    style = normalize_reply_style(reply_style)
    guidance = _REPLY_LENGTH_LINES[style]
    if guidance.startswith("- "):
        guidance = guidance[2:]
    return SYSTEM_PROMPT.replace("__REPLY_LENGTH_GUIDANCE__", guidance)


def apply_reply_style(text: str, reply_style: str = REPLY_STYLE_BRIEF) -> str:
    """Trim verified/KB replies for brief mode when no dedicated short template exists."""
    if normalize_reply_style(reply_style) != REPLY_STYLE_BRIEF or not text:
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= 3:
        return text
    return " ".join(sentences[:3]).strip()


def _compact(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


_TYPO_FIXES = (
    ("bussiness", "business"),
    ("busines ", "business "),
    ("elogible", "eligible"),
    ("eligble", "eligible"),
    ("eligibile", "eligible"),
    ("qualifcation", "qualification"),
    ("vetriit", "vetri it"),
    ("webiste", "website"),
    ("websit ", "website "),
)


def normalize_user_text(text: str) -> str:
    """Fix common typos so intent matching works like a forgiving human reader."""
    lowered = text.lower()
    for wrong, right in _TYPO_FIXES:
        lowered = lowered.replace(wrong, right)
    return lowered


_SHORT_YES = {
    "yes", "yeah", "yep", "yup", "ok", "okay", "sure", "yes please",
    "yeah sure", "ok sure", "please", "yes i want", "i want that",
}


def is_short_yes(message: str) -> bool:
    text = normalize_user_text(message).strip().rstrip(".!?")
    return text in _SHORT_YES


def _last_bot_text(history) -> str:
    for item in reversed(history or []):
        if item.get("role") == "bot":
            return item.get("text", "") or ""
    return ""


def _last_user_text(history) -> str:
    for item in reversed(history or []):
        if item.get("role") == "user":
            return (item.get("text") or "").strip()
    return ""


_ACTION_OFFER_PHRASES = (
    "say enroll",
    "tap enroll",
    "enroll now",
    "request demo",
    "tap enquiry",
    "choose quotation",
    "choose consultation",
    "submit your details",
)


def _bot_offered_action(history) -> bool:
    last = _last_bot_text(history).lower()
    return any(phrase in last for phrase in _ACTION_OFFER_PHRASES)


def get_greeting_reply(language: str = "en") -> str:
    from .language import LANG_TA, normalize_language
    from .tamil_replies import get_tamil_greeting

    if normalize_language(language) == LANG_TA:
        return get_tamil_greeting()
    return SHORT_GREETING_REPLY


def reply_to_short_yes(history=None, language: str = "en") -> str:
    """One short reply when the user only says yes. Do not start a long report."""
    from .language import LANG_TA, normalize_language
    from .tamil_replies import reply_to_short_yes_tamil

    if normalize_language(language) == LANG_TA:
        return reply_to_short_yes_tamil(history)

    last = _last_bot_text(history).lower()
    if any(word in last for word in ("enroll", "join", "course", "internship")):
        return (
            "Yes. Tap Enroll now and share your name, email, and phone. "
            "The VIS team will contact you. You do not need to sign in."
        )
    if any(word in last for word in ("demo",)):
        return "Yes. Tap Request demo and tell us which product you want to see."
    if any(word in last for word in ("quotation", "quote", "pricing", "price")):
        return "Yes. Tap Enquiry, choose Quotation, and send what you need."
    if last:
        return "Yes. What should I explain next — a course, a product, or how to enroll?"
    return "Yes. What do you need help with — a course, a product, or a website?"


_VAGUE_FOLLOW_UPS = (
    "more detail", "more details", "tell me more", "more info", "more information",
    "explain more", "want more", "go on", "continue", "elaborate", "expand on",
    "what else", "anything else",
    "innum details", "konjam sollunga", "explain pannu", "explain pannunga",
    "details venum", "innum sollunga", "மேலும்", "விவரம்",
)

_CONTINUATION_REPLIES = {
    "that", "that one", "this", "this one", "it", "same", "those",
    "the same", "about that", "about it", "what about that",
}


def is_vague_follow_up(message: str) -> bool:
    lowered = normalize_user_text(message).strip().rstrip(".!?")
    if lowered in _CONTINUATION_REPLIES:
        return True
    return any(phrase in lowered for phrase in _VAGUE_FOLLOW_UPS)


def is_contextual_follow_up(message: str) -> bool:
    return is_short_yes(message) or is_vague_follow_up(message)


def wants_more_detail(message: str, history=None) -> bool:
    """User is asking to continue or expand — switch to a longer reply."""
    if is_vague_follow_up(message):
        return True
    return is_short_yes(message) and not _bot_offered_action(history)


def infer_reply_style(message: str, history=None) -> str:
    """Short fact-packed answers by default; longer only when the user wants more."""
    if wants_more_detail(message, history):
        return REPLY_STYLE_DETAILED
    return REPLY_STYLE_BRIEF


def resolve_follow_up_query(message: str, history=None) -> str:
    """Turn short or vague follow-ups into a searchable query using recent chat."""
    text = (message or "").strip()
    if not is_contextual_follow_up(text):
        return text
    if is_short_yes(text) and _bot_offered_action(history):
        return text

    parts: list[str] = []
    last_user = _last_user_text(history)
    last_bot = _last_bot_text(history)

    if last_user and not is_short_yes(last_user) and not is_vague_follow_up(last_user):
        parts.append(last_user)

    if last_bot:
        bot_snippet = last_bot.split(".")[0].strip()
        if bot_snippet and len(bot_snippet) > 15:
            parts.append(bot_snippet)

    if text not in parts:
        parts.append(text)

    return " ".join(parts)


def expand_message_for_matching(message: str, history=None) -> str:
    """Backward-compatible alias for resolve_follow_up_query."""
    return resolve_follow_up_query(message, history)


def _rag_snippet_reply(query: str) -> str | None:
    """Short verified excerpt when KB routing has no specific template."""
    from .rag import retrieve

    chunks = retrieve(query, limit=2)
    if not chunks:
        return None
    text = " ".join(chunks[0].get("text", "").split())
    if len(text) < 40:
        return None
    snippet = text[:240].rstrip(".,; ")
    return f"Sure — {snippet}. Ask if you want more on any part."


def get_contextual_follow_up_reply(
    message: str,
    history=None,
    reply_style: str | None = None,
    language: str = "en",
) -> str | None:
    """Answer yes / tell me more using the previous question and topic."""
    style = normalize_reply_style(reply_style or infer_reply_style(message, history))
    if is_short_yes(message) and _bot_offered_action(history):
        return reply_to_short_yes(history, language)

    resolved = resolve_follow_up_query(message, history)
    fallback = get_conversational_fallback(resolved, style, language)
    if GENERIC_FALLBACK_MARKER not in fallback:
        return fallback

    rag_reply = _rag_snippet_reply(resolved)
    if rag_reply:
        return rag_reply

    if is_short_yes(message):
        return reply_to_short_yes(history, language)
    return None


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
    lowered = normalize_user_text(message)
    loose_service_map = (
        ("business website", "website development"),
        ("company website", "website development"),
        ("need a website", "website development"),
        ("want a website", "website development"),
        ("build a website", "website development"),
        ("website", "website development"),
        ("web site", "website development"),
        ("mobile app", "mobile app development"),
        ("android app", "mobile app development"),
        ("ios app", "mobile app development"),
        ("custom software", "software development"),
        ("erp system", "erp development"),
        ("digital marketing", "digital marketing"),
        ("ui ux", "ui/ux design"),
        ("ui/ux", "ui/ux design"),
    )
    for phrase, service_key in loose_service_map:
        if phrase in lowered and service_key in SERVICE_DETAILS:
            detail = SERVICE_DETAILS[service_key]
            return f"{detail}\n\n{CONTACT_LINE}."
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
        "i want to join", "want to join", "enroll now", "enrol now", "i want to enroll",
        "ready to join", "sign me up",
    ))


def _matches_website_price_intent(text: str) -> str | None:
    """Return ecommerce or retail when the user asks about those website offers."""
    ecommerce = any(k in text for k in (
        "ecommerce", "e-commerce", "e commerce", "online store", "online shop",
    ))
    retail = any(k in text for k in (
        "retail shop", "small shop", "small retail", "kirana", "retail website",
    ))
    asks_site = any(k in text for k in ("website", "web site", "site"))
    asks_price = any(k in text for k in ("price", "cost", "how much", "offer", "package", "9999", "3000"))
    if ecommerce and (asks_site or asks_price):
        return "ecommerce"
    if retail and (asks_site or asks_price or "3000" in text):
        return "retail"
    if asks_site and asks_price and "shop" in text:
        return "retail"
    return None


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
        "evlo", "evalavu",
    ))


def _matches_sales_intent(text: str) -> bool:
    return any(k in text for k in (
        "contact sales", "sales team", "talk to sales", "speak to sales",
    ))


def _matches_why_vis_intent(text: str) -> bool:
    return any(k in text for k in (
        "why vis", "why vetri", "why choose", "why should i choose",
        "why pick", "what sets you apart", "advantages of vis",
        "advantages of vetri", "reasons to choose",
    ))


def _matches_about_intent(text: str) -> bool:
    if _matches_why_vis_intent(text):
        return False
    if match_product_id(text) or match_course_id(text):
        return False
    return any(k in text for k in (
        "what is vis", "what is vetri it", "who are you", "who is vis",
        "who is vetri", "about us", "about vis", "about vetri",
        "tell me about vis", "what does vis do", "what does vetri do",
    )) or (
        "what is vetri" in text and "vetri it" in text
    )


def about_grounding_facts() -> str:
    return (
        f"{ORG_NAME} — {HERO_HEADLINE}. {HERO_SUBHEADLINE} "
        f"Products: {', '.join(PRODUCTS[:5])}, and more. "
        f"Services: {', '.join(SERVICES[:4])}, and related IT work. {TAGLINE}"
    )


def why_vis_grounding_facts() -> str:
    stats = COMPANY_STATS
    return (
        "Enterprise trust, security, and compliance; cloud-native architecture; "
        "seven shipped enterprise products; AI-first engineering. "
        "Focus: digital transformation, applied AI, full-stack engineering. "
        f"Track record: {stats['projects']} projects, {stats['years']} years, "
        f"{stats['clients']} clients, {stats['team']} team experts. "
        f"Highlights: {', '.join(COMPANY_HIGHLIGHTS)}."
    )


def _matches_vision_mission_intent(text: str) -> bool:
    return any(k in text for k in (
        "mission and vision", "mission & vision", "vision and mission",
        "what is your mission", "what is your vision",
        "your mission", "your vision", "mission vision",
    ))


def _matches_portfolio_intent(text: str) -> bool:
    return any(k in text for k in (
        "portfolio", "case study", "case studies", "projects delivered",
        "our work", "show your work", "featured project", "show your portfolio",
    ))


def _matches_contact_intent(text: str) -> bool:
    if (
        _matches_quotation_intent(text)
        or _matches_consultation_intent(text)
        or _matches_demo_intent(text)
        or _matches_sales_intent(text)
    ):
        return False
    return any(k in text for k in (
        "how can i contact", "contact you", "contact details", "contact the",
        "phone number", "your email", "your phone", "where are you",
        "your address", "reach you", "call you", "location",
    )) or text.strip() in {"contact", "phone", "email", "address"}


def vision_mission_grounding_facts() -> str:
    return (
        "Vision — An AI-Powered Business For Everyone: trusted AI and digital transformation "
        "partner for growing enterprises. "
        "Mission — Make Enterprise Technology Effortless: dependable software that removes "
        "manual work and gives leaders real-time clarity."
    )


def portfolio_grounding_facts() -> str:
    sample = "; ".join(
        f"{p['name']} ({p['type']}, {p['metric']})" for p in PORTFOLIO_PROJECTS[:4]
    )
    return f"Featured client work: {sample}."


def contact_grounding_facts() -> str:
    return (
        f"Phone {CONTACT_PHONE}, Email {CONTACT_EMAIL}, "
        f"Address {CONTACT_ADDRESS}."
    )


def products_grounding_facts() -> str:
    return f"Ready-to-use products: {', '.join(PRODUCTS)}."


def services_grounding_facts() -> str:
    return f"Custom services: {', '.join(SERVICES)}."


def courses_grounding_facts() -> str:
    return (
        f"VIS training programmes ({COURSE_DURATION}): {', '.join(COURSES)}. "
        f"Eligibility: {ELIGIBILITY_REQUIREMENT}."
    )


def quotation_grounding_facts() -> str:
    return (
        "User describes their requirement; VIS sends a tailored proposal with scope, "
        "timeline, and indicative pricing. They can use the Enquiry button → Quotation tab."
    )


def consultation_grounding_facts() -> str:
    return (
        "Speak with a VIS consultant to clarify goals and pick the right product or service. "
        "Enquiry button → Consultation tab."
    )


def demo_grounding_facts() -> str:
    return (
        "Live workflow preview of Vetri Bills, Project Management, HR Tool, CRM, Coach AI. "
        "Enquiry button → Product Demo tab."
    )


INTENTS = (
    ("greeting", ("hi", "hello", "hey", "good morning", "good evening")),
    ("quotation", ("quotation", "quote", "get quotation", "request a quotation")),
    ("portfolio", ("portfolio", "portfolios", "case study", "projects delivered", "our work")),
    ("why_vis", (
        "why vis", "why vetri", "why choose", "why should i choose",
        "what sets you apart", "reasons to choose",
    )),
    ("vision_mission", ("vision", "mission", "mission and vision", "mission & vision")),
    ("ai_solutions", (
        "ai solution", "ai solutions", "agentic ai", "workflow automation",
        "ai agents", "ai assistant", "business intelligence",
    )),
    ("products", ("product", "products", "our product", "what products")),
    ("services", ("service", "services", "our service", "what services")),
    ("about", (
        "about us", "about vis", "about vetri", "who are you", "what is vis",
        "what is vetri", "what is vetri it", "who is vis", "who is vetri",
    )),
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

    if _matches_quotation_intent(text) and not _is_course_context(text):
        return quotation_grounding_facts()

    product_id = match_product_id(text)
    if product_id:
        detail = PRODUCT_DETAILS.get(product_id)
        if detail:
            return _strip_contact_tail(detail)

    course_id = match_course_id(text)
    if course_id:
        course_detail = match_course(text)
        if course_detail:
            return _strip_contact_tail(course_detail)

    service_detail = match_service(text)
    if service_detail and not _is_course_context(text):
        return _strip_contact_tail(service_detail)

    if _matches_why_vis_intent(text):
        return why_vis_grounding_facts()
    if _matches_about_intent(text):
        return about_grounding_facts()
    if _matches_vision_mission_intent(text):
        return vision_mission_grounding_facts()
    if _matches_portfolio_intent(text):
        return portfolio_grounding_facts()
    if _matches_contact_intent(text):
        return contact_grounding_facts()
    if _matches_consultation_intent(text):
        return consultation_grounding_facts()
    if _matches_demo_intent(text):
        return demo_grounding_facts()
    if _matches_products_intent(text) and not _is_course_context(text):
        return products_grounding_facts()
    if _matches_services_intent(text) and not _is_course_context(text):
        return services_grounding_facts()
    if (
        any(k in text for k in (
            "courses available", "which courses", "what courses",
            "training courses", "training programmes", "training programs",
        ))
        or ("courses" in text and _is_course_context(text))
    ) and not match_product_id(text):
        return courses_grounding_facts()

    if not parts:
        routed = _route_faq(message)
        if routed:
            parts.append(_strip_contact_tail(routed))

    return "\n\n".join(parts).strip()


def get_conversational_fallback(
    message: str,
    reply_style: str = REPLY_STYLE_BRIEF,
    language: str = "en",
) -> str:
    """Short natural reply when the LLM is unavailable — not the long FAQ templates."""
    from .language import LANG_TA, normalize_language
    from .tamil_replies import build_tamil_fallback, get_tamil_generic_fallback

    text = message.strip().lower()
    detailed = normalize_reply_style(reply_style) == REPLY_STYLE_DETAILED

    if normalize_language(language) == LANG_TA:
        tamil = build_tamil_fallback(message, reply_style)
        if tamil:
            return tamil

    if is_greeting(text):
        return get_greeting_reply(language)

    website_offer = _matches_website_price_intent(text)
    if website_offer == "ecommerce":
        return (
            f"VIS offers an ecommerce website package at {ECOMMERCE_WEBSITE_PRICE}. "
            "When you want the team to start, say enroll and share your details in this chat. "
            "No website sign-in is required."
        )
    if website_offer == "retail":
        return (
            f"For a small retail shop, VIS offers a website at {RETAIL_SHOP_WEBSITE_PRICE}. "
            "Say enroll when you want our team to take your details and follow up."
        )

    if _matches_quotation_intent(text) and not _is_course_context(text):
        return (
            "Pricing depends on scope — users, features, and timeline. "
            "Tap Enquiry → Quotation and tell us what you need for a formal quote."
        )

    product_id = match_product_id(text)
    if product_id:
        summary = SHORT_PRODUCT_SUMMARIES.get(product_id)
        if summary:
            return f"{summary} Want more detail on any feature?"

    course_id = match_course_id(text)
    if course_id:
        course_name = match_course_name(course_id)
        if any(k in text for k in ("duration", "how long")):
            if detailed:
                return (
                    f"The {course_name} programme runs for {COURSE_DURATION}. "
                    f"Eligibility is {ELIGIBILITY_REQUIREMENT.lower()}."
                )
            return (
                f"{course_name} runs for {COURSE_DURATION} with a {COURSE_INTERNSHIP} internship. "
                f"Eligibility: {ELIGIBILITY_REQUIREMENT.lower()}."
            )
        if any(k in text for k in ("fee", "fees", "tuition", "course fee", "price", "cost")):
            if detailed:
                return (
                    f"{course_name} is a {COURSE_DURATION} programme with degree eligibility. "
                    "Fees depend on the batch and programme — I can explain the course content "
                    "and eligibility first. Use the Enquiry form for an exact fee quote."
                )
            return (
                f"{course_name} fees vary by batch. Programme is {COURSE_DURATION} — "
                "use Enquiry for an exact fee quote."
            )
        if detailed:
            return (
                f"{course_name} is a {COURSE_DURATION} VIS training programme. "
                f"You need {ELIGIBILITY_REQUIREMENT.lower()}. "
                f"Every course includes a {COURSE_INTERNSHIP} internship. "
                "I can explain more first. When you want to join, say enroll and I will take your details here. "
                "You do not need to sign in on the website."
            )
        return (
            f"{course_name}: {COURSE_DURATION} programme with a {COURSE_INTERNSHIP} internship. "
            f"You need {ELIGIBILITY_REQUIREMENT.lower()}. Say enroll to join — no sign-in needed."
        )

    if _matches_why_vis_intent(text):
        stats = COMPANY_STATS
        if detailed:
            return (
                f"Businesses choose VIS for enterprise-grade trust, cloud-native delivery, "
                f"and AI-first product engineering — not just one-off projects. "
                f"We've delivered {stats['projects']} projects over {stats['years']} with "
                f"{stats['clients']} clients, plus ready-made products like Vetri Bills and "
                f"Coach AI. What matters most for your use case — products, custom build, or AI?"
            )
        return (
            f"Teams choose VIS for trusted delivery and AI-first engineering — "
            f"{stats['projects']} projects, {stats['years']} years, products like Vetri Bills and Coach AI."
        )

    if _matches_about_intent(text):
        if detailed:
            return (
                f"{ORG_NAME} is a Tamil Nadu–based IT company that builds websites, mobile apps, "
                "and enterprise software, and also ships ready-to-use products such as Vetri Bills "
                "(GST billing), Project Management, HR Management Tool, and Coach AI. "
                "What would you like to explore — a product or a custom service?"
            )
        return (
            f"{ORG_NAME} builds websites, apps, and enterprise software in Tamil Nadu, "
            "plus products like Vetri Bills (GST billing) and Coach AI."
        )

    if _matches_vision_mission_intent(text):
        return (
            "Our vision is an AI-powered business for everyone — helping growing enterprises "
            "automate processes and make data-backed decisions. Our mission is to make "
            "enterprise technology effortless with dependable, intelligent software."
        )

    if _matches_portfolio_intent(text):
        sample = ", ".join(p["name"] for p in PORTFOLIO_PROJECTS[:2])
        stats = COMPANY_STATS
        return (
            f"Featured work includes {sample}, and more — {stats['projects']} "
            f"projects delivered across Tamil Nadu and beyond. "
            "Which type of project interests you — retail, healthcare, mobile, or e-commerce?"
        )

    if _matches_contact_intent(text):
        return (
            f"We're at {CONTACT_ADDRESS}. Phone: {CONTACT_PHONE}. "
            f"Email: {CONTACT_EMAIL}. What can I help you with today?"
        )

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
                f"Businesses choose VIS for enterprise-grade trust, cloud-native delivery, "
                f"and AI-first product engineering — not just one-off projects. "
                f"We've delivered {stats['projects']} projects over {stats['years']} with "
                f"{stats['clients']} clients, plus ready-made products like Vetri Bills and "
                f"Coach AI. What matters most for your use case — products, custom build, or AI?"
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
                f"{ORG_NAME} is a Tamil Nadu–based IT company that builds websites, mobile apps, "
                "and enterprise software, and also ships ready-to-use products such as Vetri Bills "
                "(GST billing), Project Management, HR Management Tool, and Coach AI. "
                "What would you like to explore — a product or a custom service?"
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
        snippet = grounding.split("\n")[0][:240].rstrip(".")
        return (
            f"Sure — {snippet}. Happy to go deeper if you'd like — just ask a follow-up."
        )

    if normalize_language(language) == "ta":
        return get_tamil_generic_fallback()
    return f"{GENERIC_FALLBACK_MARKER} What would you like to know?"


def detect_suggested_enquiry_type(message: str, history=None) -> str | None:
    """Suggest opening the in-chat Enquiry form for business-intent questions."""
    text = message.strip().lower()
    if is_short_yes(text):
        last = _last_bot_text(history).lower()
        if "demo" in last:
            return "demo"
        if any(word in last for word in ("quotation", "quote", "pricing")):
            return "quotation"
        if "consultation" in last:
            return "consultation"
        return "enroll"
    if _matches_consultation_intent(text):
        return "consultation"
    if _matches_demo_intent(text):
        return "demo"
    # Enroll is the next step for courses and for linking with the team.
    # There is no website sign-in.
    if _matches_apply_intent(text) or _matches_website_price_intent(text):
        return "enroll"
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
