
from django.core.management.base import BaseCommand
from django.db import transaction

from chatbot import knowledge as kb
from chatbot.models import CompanyInformation, Product, Service, Course, FAQ


class Command(BaseCommand):
    help = "Add missing verified VIS content without overwriting existing records."

    @transaction.atomic
    def handle(self, *args, **options):
        company_defaults = {
            "legal_name": kb.ORG_LEGAL,
            "tagline": kb.TAGLINE,
            "description": kb.HERO_SUBHEADLINE,
            "phone": kb.CONTACT_PHONE,
            "email": kb.CONTACT_EMAIL,
            "address": kb.CONTACT_ADDRESS,
            "website": kb.CONTACT_WEBSITE,
            "is_active": True,
        }

        company, created = CompanyInformation.objects.get_or_create(
            company_name=kb.ORG_NAME,
            defaults=company_defaults,
        )
        self.stdout.write(
            f"Company information: {'created' if created else 'already exists'}"
        )

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
            _, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "is_active": True,
                    "sort_order": position,
                },
            )
            if created:
                self.stdout.write(f"Created product: {name}")

        for position, name in enumerate(kb.SERVICES):
            description = kb.SERVICE_DETAILS.get(name.lower(), name)
            _, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "is_active": True,
                    "sort_order": position,
                },
            )
            if created:
                self.stdout.write(f"Created service: {name}")

        course_keys = {
            name: key for key, name in kb.COURSE_NAMES.items()
        }

        for position, name in enumerate(kb.COURSES):
            key = course_keys.get(name)
            details = kb.COURSE_DETAILS.get(key, "") if key else ""
            _, created = Course.objects.get_or_create(
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
            if created:
                self.stdout.write(f"Created course: {name}")

        self.stdout.write(
            self.style.SUCCESS(
                "Import complete. "
                f"Companies: {CompanyInformation.objects.count()}, "
                f"Products: {Product.objects.count()}, "
                f"Services: {Service.objects.count()}, "
                f"Courses: {Course.objects.count()}, "
                f"FAQs: {FAQ.objects.count()}. "
                "Existing records were not overwritten."
            )
        )
