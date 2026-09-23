from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0002_conversation_client_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="feedback",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.AddField(
            model_name="message",
            name="source",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
