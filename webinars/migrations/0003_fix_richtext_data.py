from django.db import migrations

def column_exists(schema_editor, table, column):
    try:
        return column in [
            c.name for c in schema_editor.connection.introspection.get_table_description(
                schema_editor.connection.cursor(), table
            )
        ]
    except Exception:
        return False


def convert_text_to_html(apps, schema_editor):
    def safe_fix(model_name, field_name):
        Model = apps.get_model("webinars", model_name)
        table = Model._meta.db_table

        if not column_exists(schema_editor, table, field_name):
            return

        for obj in Model.objects.all():
            value = getattr(obj, field_name, None)
            if value:
                text = value.strip()
                if text and not text.startswith("<"):
                    setattr(obj, field_name, f"<p>{text}</p>")
                    obj.save(update_fields=[field_name])

    safe_fix("LiveWebinar", "description")
    safe_fix("WebinarOverview", "content")
    safe_fix("WebinarBenefit", "content")
    safe_fix("WebinarAreaCovered", "content")
    safe_fix("WebinarWhyAttend", "content")


class Migration(migrations.Migration):

    dependencies = [
        ("webinars", "0002_alter_webinarareacovered_content_and_more"),
    ]

    operations = [
        migrations.RunPython(convert_text_to_html),
    ]
