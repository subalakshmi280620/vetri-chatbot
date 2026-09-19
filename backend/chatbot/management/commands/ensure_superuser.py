import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create a Django superuser from environment variables when one does not exist. "
        "Used on Render free tier where Shell access is unavailable."
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser creation: set DJANGO_SUPERUSER_USERNAME and "
                    "DJANGO_SUPERUSER_PASSWORD in the environment."
                )
            )
            return

        if len(password) < 8:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_SUPERUSER_PASSWORD must be at least 8 characters."
                )
            )
            return

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            user = user_model.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            if email:
                user.email = email
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Updated superuser '{username}' from environment.")
            )
            return

        user_model.objects.create_superuser(
            username=username,
            email=email or f"{username}@example.com",
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
