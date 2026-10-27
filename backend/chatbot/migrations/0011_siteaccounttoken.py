import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("chatbot", "0010_visitorevent"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="SiteAccountToken", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("token", models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("last_used_at", models.DateTimeField(auto_now=True)),
        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="site_tokens", to=settings.AUTH_USER_MODEL)),
    ])]
