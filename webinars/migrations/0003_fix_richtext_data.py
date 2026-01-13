from django.db import migrations, connection

def table_has_column(table, column):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, [table, column])
        return cursor.fetchone() is not None


def convert_text_to_html(apps, schema_editor):
    def safe_fix(app_label, model_name, field_name):
        Model = apps.get_model("webinars", model_name)
        table = Model._meta.db_table

        if not table_has_column(table, field_name):
            return

        for obj in Model.objects.all():
            value = getattr(obj, field_name, None)
            if value:
                text = value.strip()
                if text and not text.startswith("<"):
                    setattr(obj, field_name, f"<p>{text}</p>")
                    obj.save(update_fields=[field_name])

    safe_fix("webinars", "LiveWebinar", "description")
    safe_fix("webinars", "WebinarOverview", "content")
    safe_fix("webinars", "WebinarBenefit", "content")
    safe_fix("webinars", "WebinarAreaCovered", "content")
    safe_fix("webinars", "WebinarWhyAttend", "content")


class Migration(migrations.Migration):

    dependencies = [
        ("webinars", "0002_alter_webinarareacovered_content_and_more"),
    ]

    operations = [
        migrations.RunPython(convert_text_to_html),
    ]
