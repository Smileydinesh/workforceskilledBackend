from django.core.management.base import BaseCommand
from webinars.models import WebinarOverview, WebinarWhyAttend, WebinarBenefit, WebinarAreaCovered
from recorded_webinars.models import (
    RecordedWebinarOverview,
    RecordedWebinarWhyAttend,
    RecordedWebinarBenefit,
    RecordedWebinarAreaCovered,
)

class Command(BaseCommand):
    help = "Normalize legacy text fields to CKEditor-compatible HTML"

    def normalize(self, qs):
        count = 0
        for obj in qs:
            if obj.content and not obj.content.strip().startswith("<"):
                obj.content = f"<p>{obj.content}</p>"
                obj.save()
                count += 1
        return count

    def handle(self, *args, **kwargs):
        total = 0

        total += self.normalize(WebinarOverview.objects.all())
        total += self.normalize(WebinarWhyAttend.objects.all())
        total += self.normalize(WebinarBenefit.objects.all())
        total += self.normalize(WebinarAreaCovered.objects.all())

        total += self.normalize(RecordedWebinarOverview.objects.all())
        total += self.normalize(RecordedWebinarWhyAttend.objects.all())
        total += self.normalize(RecordedWebinarBenefit.objects.all())
        total += self.normalize(RecordedWebinarAreaCovered.objects.all())

        self.stdout.write(self.style.SUCCESS(f"Normalized {total} legacy CKEditor fields"))
