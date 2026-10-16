from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot", "0007_enquiry_notes_assigned_staff"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enquiry",
            name="enquiry_type",
            field=models.CharField(
                choices=[
                    ("quotation", "Request a quotation"),
                    ("consultation", "Book a consultation"),
                    ("demo", "Request a product demo"),
                    ("sales", "Contact sales team"),
                    ("enroll", "Enroll / connect with team"),
                    ("general", "General enquiry"),
                ],
                default="general",
                max_length=20,
            ),
        ),
    ]
