"""Answers grounded in verified VIS / Vetri IT Systems course information."""

import re

SITE_URL = "https://vetrifresh.com/"
ORG_NAME = "Vetri IT Systems (VIS)"

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

CONTACT_LINE = (
    "Please contact the VIS team for confirmation: "
    f"+91-8438164827 / +91-8438781327"
)

COURSE_DURATION = "180 days"
ELIGIBILITY_REQUIREMENT = "Any degree completion"

DEGREE_INDICATORS = (
    "degree", "graduate", "graduation", "graduated", "bachelor", "master",
    "btech", "b.tech", "b.e", "bsc", "b.sc", "bca", "b.com", "bcom",
    "mba", "mca", "m.tech", "mtech", "engineering", "ug", "pg",
    "post graduate", "postgraduate", "completed degree", "degree holder",
    "ba ", "b.a", "ma ", "m.a", "phd", "doctorate",
)

UNVERIFIED = (
    "Thank you for your question.\n\n"
    "I could not find verified information about that in the available VIS course "
    f"information.\n\n{CONTACT_LINE}."
)


def qualification_meets_degree_requirement(qualification: str) -> bool:
    lowered = qualification.lower()
    return any(indicator in lowered for indicator in DEGREE_INDICATORS)


def duration_reply(course_name: str = "") -> str:
    topic = f" — {course_name}" if course_name else ""
    return (
        f"Course Duration{topic}\n\n"
        f"The verified course duration is {COURSE_DURATION}.\n\n"
        "This duration applies to all listed VIS training programmes unless stated "
        f"otherwise.\n\n{CONTACT_LINE}."
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
        "About the programme:\n"
        f"{name} is offered by {ORG_NAME} with structured training and "
        "role-specific interview preparation support.\n"
        f"{extra_block}\n"
        f"Duration:\n{COURSE_DURATION}\n\n"
        f"Eligibility:\n{ELIGIBILITY_REQUIREMENT}\n\n"
        "Key skills and practice areas:\n"
        "• Role-specific interview roadmap\n"
        "• AI mock interviews (technical, HR, and behavioural)\n"
        "• Instant AI feedback and performance reports\n"
        "• Learning roadmap aligned with institute course material\n\n"
        "How to apply:\n"
        "• Confirm you meet the eligibility requirement (any degree completion)\n"
        "• Contact the VIS admissions team to register for your chosen programme\n"
        "• Share your qualification and preferred course for enrollment confirmation\n\n"
        f"For fee details or admission confirmation, {CONTACT_LINE.lower()}."
    )


def course_reply(name: str, extra: str = "") -> str:
    return course_card(name, extra)


COURSE_DETAILS = {
    "java": course_reply(
        "Java Fullstack",
        "The platform demo includes a Java Backend live mock interview. "
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
        "This course is listed on the platform as AWS & Deveops.",
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

REPLIES = {
    "greeting": (
        f"Welcome to {ORG_NAME}.\n\n"
        "I am your VIS virtual assistant. I can help you with course information, "
        "duration, eligibility, mock interview support, and contact details.\n\n"
        "I provide only verified information from our official VIS course data. "
        "How may I assist you today?"
    ),
    "about": (
        f"About {ORG_NAME}\n\n"
        "We provide professional IT training with AI-powered interview coaching: "
        "Prepare, Practice, and Perform.\n\n"
        "Our programmes include: "
        + ", ".join(COURSES)
        + "."
    ),
    "courses": (
        f"Available Courses — {ORG_NAME}\n\n"
        + "\n".join(f"• {name}" for name in COURSES)
        + "\n\nEach programme includes role-specific mock interview preparation and "
        "structured learning support.\n\n"
        "To view details for a specific course, please ask by name — for example: "
        "\"Tell me about Python Fullstack.\""
    ),
    "mock": (
        "AI Mock Interview is a live session with technical, HR, and behavioral questions. "
        "It is available for every course. Questions are grounded in the institute's course "
        "material and question bank wherever available."
    ),
    "feedback": (
        "After every answer you get instant AI feedback: strengths, gaps, and ideal answers. "
        "You can also track growth with performance reports. This applies across all courses."
    ),
    "features": (
        "VIS training and coaching includes:\n"
        "- Interview Preparation (role-specific roadmaps)\n"
        "- AI Mock Interview\n"
        "- AI Feedback\n"
        "- Performance Reports\n"
        "- Learning Roadmap\n"
        "- Role Based Practice\n\n"
        "These features apply to every listed course."
    ),
    "how": (
        "How it works for every course: Choose Job → Prepare → Practice → "
        "AI Evaluation → Improve."
    ),
    "free": (
        "Yes. You can register for free and start preparing and practicing mock interviews "
        "immediately."
    ),
    "pricing": (
        "Course Fee Information\n\n"
        "You may register for free and begin mock interview practice immediately.\n\n"
        "Verified training-course fee amounts are not listed in the available VIS course "
        f"information.\n\n{CONTACT_LINE}."
    ),
    "contact": (
        f"Contact {ORG_NAME}\n\n"
        "• Phone: +91-8438164827\n"
        "• Phone: +91-8438781327\n\n"
        f"{CONTACT_LINE}."
    ),
    "login": (
        "Use Login or Get Started on the platform to create a free account and "
        "begin mock interviews for your course."
    ),
    "skills": (
        "Key skills and practice areas across VIS courses include:\n"
        "- Role-specific interview roadmaps\n"
        "- AI mock interviews (technical, HR, and behavioral)\n"
        "- Instant AI feedback and performance reports\n"
        "- Learning roadmap based on institute course material\n\n"
        "Ask about a specific course for more detail, for example: "
        "Tell me about Python Fullstack."
    ),
    "who_can_apply": (
        "Admission Eligibility\n\n"
        f"• Requirement: {ELIGIBILITY_REQUIREMENT}\n"
        "• Accepted examples: B.Tech, B.Sc, BCA, B.Com, MBA, MCA, or any other completed "
        "undergraduate or postgraduate degree."
    ),
    "apply": (
        "How to Apply — VIS Training Programmes\n\n"
        "Step 1: Review eligibility\n"
        f"• Ensure you meet the requirement: {ELIGIBILITY_REQUIREMENT}\n\n"
        "Step 2: Choose your course\n"
        "• Select from our available programmes (for example, Python Fullstack, Java Fullstack, "
        "Data Science, or UI/UX)\n\n"
        "Step 3: Contact the VIS admissions team\n"
        "• Phone: +91-8438164827\n"
        "• Phone: +91-8438781327\n"
        "• Share your qualification, preferred course, and contact details\n\n"
        "Step 4: Complete enrollment\n"
        "• The VIS team will guide you through registration and programme onboarding\n\n"
        f"{CONTACT_LINE}."
    ),
}

STRUCTURED_TRIGGERS = (
    "duration", "how long", "how many months", "how many days",
    "fee", "fees", "tuition", "course cost", "course fee", "price", "pricing",
    "skill", "learn", "what will i", "course", "courses", "contact", "phone",
    "eligib", "who can apply", "mock", "register", "login",
    "how to apply", "how do i apply", "application", "admission process", "enroll",
)

SYSTEM_PROMPT = f"""You are the official VIS assistant for {ORG_NAME}.
Be professional, friendly, clear, and concise. Use short labelled sections when describing a course.
Treat every listed course equally. If the user names one course, answer that course only.
Do not dump the full course list unless they ask what courses exist.
Greet warmly for hi, hello, hii, hey.
Never invent course fees, certificates, batches, or placement figures.
If a fact is not in the facts below or in retrieved documents, say you could not find verified VIS course information and suggest contacting VIS (+91-8438164827 / +91-8438781327).
For eligibility ("am I eligible"): use the listed rule — {ELIGIBILITY_REQUIREMENT}. Ask which course and qualification if needed, then respond with Outcome: ELIGIBLE, NOT ELIGIBLE, or CANNOT DETERMINE.

Facts:
- Organization: {ORG_NAME}.
- Product: AI interview coaching — Prepare, Practice, Perform.
- Tagline: Crack Your Dream Interview with AI.
- Features: Interview Preparation, AI Mock Interview, AI Feedback, Performance Reports, Learning Roadmap, Role Based Practice.
- Mock interviews: live sessions with technical, HR, and behavioral questions, grounded in institute course material, for every course.
- How it works: Choose Job → Prepare → Practice → AI Evaluation → Improve.
- Free to register and start mock interviews immediately. Exact classroom/course fee amounts are not in the public notes.
- Course duration: {COURSE_DURATION} for all listed training courses.
- Eligibility: {ELIGIBILITY_REQUIREMENT} for all listed training courses.
- How to apply: (1) confirm eligibility, (2) choose a course, (3) contact VIS admissions by phone, (4) complete enrollment with VIS team guidance.
- Courses: {", ".join(COURSES)}.
- Java Fullstack demo is Java Backend; example prompt about handling a production bug under pressure.
- AWS & DevOps is spelled AWS & Deveops on the platform.
- Phone: +91-8438164827, +91-8438781327.
"""

INTENTS = (
    ("greeting", ("hi", "hello", "hey", "good morning", "good evening")),
    ("mock", ("mock", "interview question", "live interview", "practice interview")),
    ("feedback", ("feedback", "report", "score", "evaluation")),
    ("how", ("how it works", "how does", "roadmap", "process")),
    ("free", ("free", "cost nothing", "without paying")),
    ("pricing", ("price", "pricing", "paid", "plan", "subscription", "course fee", "tuition")),
    ("contact", ("contact", "phone", "call", "mobile number", "refund", "privacy", "terms")),
    ("login", ("login", "register", "sign up", "get started", "account")),
    ("features", ("feature", "what can you", "everything you need")),
    ("courses", ("course", "courses", "what do you offer", "modules", "programs")),
    ("about", ("about vetri", "what is vetri", "who are you", "about vis")),
    ("who_can_apply", ("who can apply", "who can join", "who is eligible")),
    ("apply", (
        "how to apply", "how do i apply", "how can i apply", "application process",
        "admission process", "how to enroll", "how to join", "how to register for course",
        "apply for course", "apply for admission",
    )),
    ("skills", ("what skills", "skills will i learn", "key skills", "what will i learn")),
)


def _compact(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


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


def get_structured_reply(message: str) -> str | None:
    """Return a verified KB answer for clear FAQ-style questions."""
    text = message.strip().lower()
    if is_greeting(text):
        return REPLIES["greeting"]
    if match_course_id(text):
        if any(key in text for key in ("duration", "how long", "how many months", "how many days")):
            return duration_reply(match_course_name(match_course_id(text)))
        if any(key in text for key in ("fee", "fees", "tuition", "course cost", "course fee")):
            return REPLIES["pricing"]
        course_text = match_course(text)
        if course_text:
            return course_text
    if any(key in text for key in ("duration", "how long", "how many months", "how many days")):
        return duration_reply(match_course_name(match_course_id(text)))
    if any(key in text for key in ("fee", "fees", "tuition", "course cost", "course fee")):
        return REPLIES["pricing"]
    if any(key in text for key in ("skill", "learn", "what will i")):
        course_text = match_course(text)
        return course_text or REPLIES["skills"]
    course_text = match_course(text)
    if course_text:
        return course_text
    for intent, keywords in INTENTS:
        if intent == "greeting":
            continue
        if any(keyword in text for keyword in keywords):
            return REPLIES[intent]
    return None


def should_prefer_kb(message: str) -> bool:
    text = message.strip().lower()
    return is_greeting(text) or any(trigger in text for trigger in STRUCTURED_TRIGGERS) or bool(match_course_id(text))


def get_reply(message: str) -> str:
    text = message.strip().lower()
    if is_greeting(text):
        return REPLIES["greeting"]

    if any(key in text for key in ("duration", "how long", "how many months", "how many days")):
        name = match_course_name(match_course_id(text))
        return duration_reply(name)

    if any(key in text for key in ("fee", "fees", "tuition", "course cost", "course fee")):
        return REPLIES["pricing"]

    if any(key in text for key in ("skill", "learn", "what will i")):
        course_reply_text = match_course(text)
        if course_reply_text:
            return course_reply_text
        return REPLIES["skills"]

    course_reply_text = match_course(text)
    if course_reply_text:
        return course_reply_text

    for intent, keywords in INTENTS:
        if intent == "greeting":
            continue
        if any(keyword in text for keyword in keywords):
            return REPLIES[intent]

    return UNVERIFIED
