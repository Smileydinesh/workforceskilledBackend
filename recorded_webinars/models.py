# recorded_webinars/models.py
import uuid
from django.db import models
from django.utils import timezone
from webinars.models import Instructor


import uuid
from django.utils import timezone
from django.db import models
from webinars.models import Instructor, WebinarCategory


class RecordedWebinar(models.Model):
    webinar_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    category = models.ForeignKey(
        WebinarCategory,
        on_delete=models.PROTECT,
        related_name="recorded_webinars"
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

    format = models.CharField(
        max_length=100,
        default="High-quality streaming"
    )
    refund_policy = models.CharField(
        max_length=255,
        default="100% Money Back Guarantee"
    )

    def __str__(self):
        return f"Details for {self.webinar.title}"


class RecordedWebinarOverview(models.Model):
    webinar = models.ForeignKey(
        RecordedWebinar,
        on_delete=models.CASCADE
    )
    paragraph = models.TextField()

    def __str__(self):
        return self.paragraph[:50]


class RecordedWebinarWhyAttend(models.Model):
    webinar = models.ForeignKey(
        RecordedWebinar,
        on_delete=models.CASCADE
    )
    point = models.CharField(max_length=255)

    def __str__(self):
        return self.point


class RecordedWebinarBenefit(models.Model):
    webinar = models.ForeignKey(
        RecordedWebinar,
        on_delete=models.CASCADE
    )
    subtitle = models.CharField(max_length=255, blank=True)
    point = models.CharField(max_length=255)

    def __str__(self):
        return self.point


class RecordedWebinarAreaCovered(models.Model):
    webinar = models.ForeignKey(
        RecordedWebinar,
        on_delete=models.CASCADE
    )
    point = models.CharField(max_length=255)

    def __str__(self):
        return self.point
