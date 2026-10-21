
from chatbot import knowledge as kb
from chatbot.models import CompanyInformation, Product, Service, Course, FAQ

# Company details from the existing verified knowledge.
CompanyInformation.objects.update_or_create(
    company_name=kb.ORG_NAME,
    defaults={
        "legal_name": kb.ORG_LEGAL,
        "tagline": kb.TAGLINE,
        "description": kb.HERO_SUBHEADLINE,
        "phone": kb.CONTACT_PHONE,
        "email": kb.CONTACT_EMAIL,
        "address": kb.CONTACT_ADDRESS,
        "website": kb.CONTACT_WEBSITE,
        "is_active": True,
    },
)

# Map each existing product to its verified description.
product_details = {
    "Vetri Bills": "vetri_bills",
    "Vetri Files": "vetri_files",
    "Vetri Project Management": "vetri_pm",
    "Coach AI": "coach_ai",
    "Vetri AI Assistant": "vetri_ai_assistant",
    "Vetri CRM": "vetri_crm",
    "Vetri Training Management System": "vetri_tms",
    "HR Management Tool": "vetri_hrms",
}

for position, name in enumerate(kb.PRODUCTS):
    detail_key = product_details.get(name)
    description = (
        kb.PRODUCT_DETAILS.get(detail_key, name)
        if detail_key else name
    )
    Product.objects.update_or_create(
        name=name,
        defaults={
            "description": description,
            "is_active": True,
            "sort_order": position,
        },
    )

# Import services, using existing details where available.
for position, name in enumerate(kb.SERVICES):
    description = kb.SERVICE_DETAILS.get(name.lower(), name)
    Service.objects.update_or_create(
        name=name,
        defaults={
            "description": description,
            "is_active": True,
            "sort_order": position,
        },
    )

# Import courses and their existing course information.
course_keys = {
    name: key for key, name in kb.COURSE_NAMES.items()
}

for position, name in enumerate(kb.COURSES):
    key = course_keys.get(name)
    details = kb.COURSE_DETAILS.get(key, "") if key else ""

    Course.objects.update_or_create(
        name=name,
        defaults={
            "description": details or f"{name} training programme.",
            "duration": kb.COURSE_DURATION,
            "eligibility": kb.ELIGIBILITY_REQUIREMENT,
            "internship": kb.COURSE_INTERNSHIP,
            "is_active": True,
            "sort_order": position,
        },
    )

# No FAQ records are created because no separate verified FAQ list
# has been defined in the existing knowledge file.

print("Admin content import completed.")
print("Company records:", CompanyInformation.objects.count())
print("Products:", Product.objects.count())
print("Services:", Service.objects.count())
print("Courses:", Course.objects.count())
print("FAQs:", FAQ.objects.count())
