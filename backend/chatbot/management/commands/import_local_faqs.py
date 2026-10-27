import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from chatbot.models import FAQ


class Command(BaseCommand):
    help = "Import missing FAQs without overwriting existing records."

    def handle(self, *args, **options):
        fixture = Path(__file__).resolve().parents[3] / "local_faqs.json"

        if not fixture.is_file():
            raise CommandError(f"FAQ file not found: {fixture}")

        try:
            records = json.loads(fixture.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Cannot read FAQ file: {exc}") from exc

        created_count = 0
        existing_count = 0

        for record in records:
            if record.get("model") != "chatbot.faq":
                continue

            fields = record.get("fields", {})
            question = fields.get("question", "").strip()
            answer = fields.get("answer", "").strip()

            if not question or not answer:
                raise CommandError("FAQ entry has a missing question or answer.")

            _, created = FAQ.objects.get_or_create(
                question=question,
                defaults={
                    "category": fields.get("category", ""),
                    "answer": answer,
                    "is_active": fields.get("is_active", True),
                    "sort_order": fields.get("sort_order", 0),
                },
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"FAQ import complete. Created: {created_count}; "
                f"already existing: {existing_count}; "
                f"total FAQs: {FAQ.objects.count()}."
            )
        )
