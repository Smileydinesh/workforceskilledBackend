from django.db import migrations

def convert_text_to_html(apps, schema_editor):
    LiveWebinar = apps.get_model("webinars", "LiveWebinar")
    WebinarOverview = apps.get_model("webinars", "WebinarOverview")
    WebinarBenefit = apps.get_model("webinars", "WebinarBenefit")
    WebinarAreaCovered = apps.get_model("webinars", "WebinarAreaCovered")
    WebinarWhyAttend = apps.get_model("webinars", "WebinarWhyAttend")

    def fix(qs, field):
        for obj in qs.all():
            value = getattr(obj, field, None)
            if value:
                text = value.strip()
                if text and not text.startswith("<"):
                    setattr(obj, field, f"<p>{text}</p>")
                    obj.save(update_fields=[field])

    fix(LiveWebinar.objects, "description")
    fix(WebinarOverview.objects, "content")
    fix(WebinarBenefit.objects, "content")
    fix(WebinarAreaCovered.objects, "content")
    fix(WebinarWhyAttend.objects, "content")


class Migration(migrations.Migration):

    dependencies = [
        ("webinars", "0002_alter_webinarareacovered_content_and_more"),
    ]

    operations = [
        migrations.RunPython(convert_text_to_html),
    ]
