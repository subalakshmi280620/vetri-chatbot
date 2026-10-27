import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("chatbot", "0009_companyinformation_course_faq_product_service")]
    operations = [
        migrations.CreateModel(
            name="VisitorEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("visitor_id", models.UUIDField(db_index=True)),
                ("path", models.CharField(db_index=True, default="/", max_length=255)),
                ("visited_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"ordering": ["-visited_at"]},
        ),
        migrations.AddIndex(model_name="visitorevent", index=models.Index(fields=["visited_at", "path"], name="chat_vis_date_path_idx")),
    ]
