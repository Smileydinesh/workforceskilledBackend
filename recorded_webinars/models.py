# recorded_webinars/models.py
import uuid
from django.db import models
from django.utils import timezone
from webinars.models import Instructor


import uuid
from django.utils import timezone
from django.db import models
from webinars.models import Instructor


class RecordedWebinar(models.Model):
    webinar_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    cover_image = models.ImageField(upload_to="recorded/covers/")
    preview_video = models.FileField(
        upload_to="recorded/previews/",
        blank=True,
        null=True
    )

    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    duration_minutes = models.PositiveIntegerField()

    access_type = models.CharField(
        max_length=20,
        choices=(
            ("LIFETIME", "Lifetime"),
            ("LIMITED", "Limited Time"),
        ),
        default="LIFETIME"
    )

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.webinar_id:
            self.webinar_id = f"WEB{timezone.now().strftime('%y%m%d')}{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class RecordedWebinarPricing(models.Model):
    webinar = models.OneToOneField(
        RecordedWebinar,
        related_name="pricing",
        on_delete=models.CASCADE
    )

    single_price = models.DecimalField(max_digits=8, decimal_places=2)
    multi_user_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)


class RecordedWebinarDetail(models.Model):
    webinar = models.OneToOneField(
        RecordedWebinar,
        related_name="details",
        on_delete=models.CASCADE
    )

    overview = models.TextField(help_text="Paragraphs separated by new lines")
    why_attend = models.TextField(help_text="One point per line")
    who_benefit = models.TextField(help_text="One point per line")
    areas_covered = models.TextField(help_text="One point per line")

    format = models.CharField(max_length=100, default="High-quality streaming")
    refund_policy = models.CharField(
        max_length=255,
        default="100% Money Back Guarantee"
    )
