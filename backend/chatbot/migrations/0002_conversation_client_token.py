import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="client_token",
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
    ]
