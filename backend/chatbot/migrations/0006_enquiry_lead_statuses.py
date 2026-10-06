from django.db import migrations, models


def migrate_reviewed_to_contacted(apps, schema_editor):
    Enquiry = apps.get_model("chatbot", "Enquiry")
    Enquiry.objects.filter(status="reviewed").update(status="contacted")


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0005_knowledge_vector_rag"),
    ]

    operations = [
        migrations.RunPython(migrate_reviewed_to_contacted, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="enquiry",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("contacted", "Contacted"),
                    ("closed", "Closed"),
                ],
                default="new",
                max_length=20,
            ),
        ),
    ]
