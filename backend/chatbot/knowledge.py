"""Answers grounded in public content from https://vetrifresh.com/"""

import re

SITE_URL = "https://vetrifresh.com/"

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


def course_reply(name: str, extra: str = "") -> str:
    body = (
        f"{name} is one of the courses on Vetri AI Coach.\n\n"
        "You can prepare for role-specific interviews with:\n"
        "- Interview preparation roadmap and topics\n"
        "- AI mock interviews (technical, HR, and behavioral)\n"
        "- Instant AI feedback after each answer\n"
        "- Performance reports and a learning roadmap\n"
        "- Questions grounded in what the institute actually teaches\n\n"
    )
    if extra:
        body += extra.strip() + "\n\n"
    body += (
        f"Open {name} → Explore roles & modules on {SITE_URL}\n"
        "The public homepage does not list the full module syllabus. "
        "Use the site for roles and modules."
    )
    return body


COURSE_DETAILS = {
    "java": course_reply(
        "Java Fullstack",
        "The homepage demo is a Java Backend live mock interview. "
        'Example prompt: "Tell me about a time you handled a production bug under pressure."',
    ),
    "python": course_reply("Python Fullstack"),
    "prompt": course_reply("Prompt Engineering"),
    "uiux": course_reply("UI/UX"),
    "testing": course_reply("Software Testing"),
    "analytics": course_reply("Data Analytics"),
    "mobile": course_reply("Mobile App Development"),
    "aws": course_reply(
        "AWS & DevOps",
        "On the website this course is listed as AWS & Deveops.",
    ),
    "datascience": course_reply("Data Science"),
    "marketing": course_reply("Digital Marketing"),
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
    ("marketing", ("digital marketing", "digitalmarketing")),
)

REPLIES = {
    "greeting": (
        "Hi! I am Vetri AI Coach for Vetri IT Systems. "
        "I can help with every course on vetrifresh.com, plus mock interviews, "
        f"pricing, login, and contact details. Site: {SITE_URL}"
    ),
    "about": (
        "Vetri AI Coach helps you crack interviews with AI: Prepare, Practice, "
        "and Perform. Coaching is matched to every course the institute trains you on: "
        + ", ".join(COURSES)
        + f". Learn more at {SITE_URL}"
    ),
    "courses": (
        "Courses covered on Vetri AI Coach:\n"
        + "\n".join(f"- {name}" for name in COURSES)
        + "\n\nEach course has role-specific mock interview preparation. "
        "Ask about any course by name, for example: Tell me about Python Fullstack."
    ),
    "mock": (
        "AI Mock Interview is a ChatGPT-style live session with technical, HR, "
        "and behavioral questions. It is available for every course on the site. "
        "Questions are grounded in the institute's course material and question bank "
        "wherever available, so you are asked what was actually taught."
    ),
    "feedback": (
        "After every answer you get instant AI feedback: strengths, gaps, and "
        "ideal answers. You can also track growth with performance reports. "
        "This applies across all courses."
    ),
    "features": (
        "Vetri AI Coach includes:\n"
        "- Interview Preparation (role-specific roadmaps)\n"
        "- AI Mock Interview\n"
        "- AI Feedback\n"
        "- Performance Reports\n"
        "- Learning Roadmap\n"
        "- Role Based Practice\n\n"
        "These features are for every course listed on vetrifresh.com."
    ),
    "how": (
        "How it works for every course: Choose Job → Prepare → Practice → "
        "AI Evaluation → Improve."
    ),
    "free": (
        "Yes. You can register for free on Vetri AI and start preparing and "
        "practicing mock interviews immediately. Open Get Started on "
        f"{SITE_URL}"
    ),
    "pricing": (
        "You can register free and start practicing right away. For paid plans, "
        f"open the Pricing page on {SITE_URL}pricing"
    ),
    "contact": (
        "Contact Vetri AI Coach:\n"
        "- Phone: +91-8438164827\n"
        "- Phone: +91-8438781327\n"
        f"- Website: {SITE_URL}\n"
        "Pages: Home, About, Contact, Pricing, Login, Get Started. "
        "Policies: Terms and Conditions, Privacy Policy, Refund Policy."
    ),
    "login": (
        f"Use Login or Get Started on {SITE_URL} to create a free account and "
        "begin mock interviews for your course."
    ),
}

SYSTEM_PROMPT = f"""You are Vetri AI Coach, the assistant for Vetri IT Systems.
Answer only about Vetri AI Coach at {SITE_URL}.
Be concise and helpful.
Treat every listed course equally. If the user names one course, answer that course only.
Do not dump the full course list unless they ask what courses exist.
If the user says hi, hello, hii, hey, or similar, greet them warmly and invite them to ask about courses, mock interviews, pricing, or contact.
If the question is not a greeting and is not about Vetri AI Coach, or the fact is not in the list below
or in retrieved documents, reply: this information is not available on Vetri AI Coach.
Do not invent fees, batch dates, certificates, or a full syllabus for any course.

Facts:
- Product: AI interview coaching — Prepare, Practice, Perform.
- Tagline: Crack Your Dream Interview with AI.
- Features: Interview Preparation, AI Mock Interview, AI Feedback, Performance Reports, Learning Roadmap, Role Based Practice.
- Mock interviews: ChatGPT-style live sessions with technical, HR, and behavioral questions, grounded in institute course material, for every course.
- How it works: Choose Job → Prepare → Practice → AI Evaluation → Improve.
- Free to register and start mock interviews immediately.
- Pages: Home, About, Contact, Pricing, Login, Get Started.
- Courses: {", ".join(COURSES)}.
- Java Fullstack homepage demo is Java Backend; example prompt about handling a production bug under pressure.
- AWS & DevOps is spelled AWS & Deveops on the site.
- Phone: +91-8438164827, +91-8438781327.
- Developer: Vetri IT Systems Pvt.
"""

INTENTS = (
    ("greeting", ("hi", "hello", "hey", "good morning", "good evening")),
    ("mock", ("mock", "interview question", "live interview", "practice interview")),
    ("feedback", ("feedback", "report", "score", "evaluation")),
    ("how", ("how it works", "how does", "roadmap", "process")),
    ("free", ("free", "cost nothing", "without paying")),
    ("pricing", ("price", "pricing", "paid", "plan", "subscription")),
    ("contact", ("contact", "phone", "call", "mobile number", "refund", "privacy", "terms")),
    ("login", ("login", "register", "sign up", "get started", "account")),
    ("features", ("feature", "what can you", "everything you need")),
    ("courses", ("course", "courses", "what do you offer", "modules")),
    ("about", ("about vetri", "what is vetri", "who are you")),
)


def _compact(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


def match_course(message: str) -> str | None:
    compact = _compact(message)
    lowered = message.lower()
    for course_id, aliases in COURSE_ALIASES:
        for alias in aliases:
            if alias.replace(" ", "") in compact or alias in lowered:
                return COURSE_DETAILS[course_id]
    return None


def is_greeting(message: str) -> bool:
    compact = _compact(message)
    if re.fullmatch(r"(h+i+|hey+|hello+|hai+|helo+|hlo+|yo+|hai+)", compact):
        return True
    words = "".join(ch.lower() if ch.isalnum() else " " for ch in message).split()
    if not words or len(words) > 5:
        return False
    greet_words = {"hi", "hii", "hiii", "hello", "hey", "hai", "helo", "hlo", "yo"}
    return words[0] in greet_words


def get_reply(message: str) -> str:
    text = message.strip().lower()
    if is_greeting(text):
        return REPLIES["greeting"]

    course_reply_text = match_course(text)
    if course_reply_text:
        return course_reply_text

    for intent, keywords in INTENTS:
        if intent == "greeting":
            continue
        if any(keyword in text for keyword in keywords):
            return REPLIES[intent]

    return (
        "This information is not available on Vetri AI Coach. "
        "I can help with every course on vetrifresh.com, mock interviews, "
        "pricing, login, and contact numbers. "
        "Try: What courses do you offer? or Tell me about Python Fullstack."
    )
