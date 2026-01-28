import uuid
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from datetime import timedelta



# webinars/models.py

class WebinarCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class LiveWebinar(models.Model):
    WEBINAR_STATUS = (
        ("UPCOMING", "Upcoming"),
        ("LIVE", "Live"),
        ("ENDED", "Ended"),
    )

    webinar_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    category = models.ForeignKey(
    WebinarCategory,
    on_delete=models.PROTECT,
    related_name="webinars"
)
  

    title = models.CharField(max_length=255)

    is_test = models.BooleanField(
        default=False,
        help_text="Mark this webinar as Test / Demo only"
    )

    description = models.TextField(blank=True) 
    cover_image = models.ImageField(upload_to="webinars/covers/",null=True,blank=True,help_text="Optional – upload only if needed")

    instructor = models.ForeignKey("webinars.Instructor",on_delete=models.CASCADE)

    start_datetime = models.DateTimeField()
    time_display = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField()

    # price_usd = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(
        max_length=10,
        choices=WEBINAR_STATUS,
        default="UPCOMING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_datetime"]

    def save(self, *args, **kwargs):
        if not self.webinar_id:
            self.webinar_id = (
                f"WEB{timezone.now().strftime('%y%m%d')}"
                f"{uuid.uuid4().hex[:4].upper()}"
            )

        # ✅ JUST CALCULATE STATUS (NO EXTRA SAVE)
        self.status = self.calculate_status()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    
    @property
    def end_datetime(self):
        return self.start_datetime + timedelta(minutes=self.duration_minutes)
    
    def calculate_status(self):
        now = timezone.now()
        end_time = self.start_datetime + timedelta(minutes=self.duration_minutes)

        if now < self.start_datetime:
            return "UPCOMING"
        elif self.start_datetime <= now <= end_time:
            return "LIVE"
        return "ENDED"




class WebinarPricing(models.Model):
    webinar = models.OneToOneField(
        LiveWebinar,
        on_delete=models.CASCADE,
        related_name="pricing"
    )

    # Live
    live_single_price = models.DecimalField(max_digits=8, decimal_places=2)
    live_multi_price = models.DecimalField(max_digits=8, decimal_places=2)

    # Recorded
    recorded_single_price = models.DecimalField(max_digits=8, decimal_places=2)
    recorded_multi_price = models.DecimalField(max_digits=8, decimal_places=2)

    # Combo
    combo_single_price = models.DecimalField(max_digits=8, decimal_places=2)
    combo_multi_price = models.DecimalField(max_digits=8, decimal_places=2)



class WebinarOverview(models.Model):
    webinar = models.OneToOneField(LiveWebinar, on_delete=models.CASCADE)
    content = RichTextField()

class WebinarWhyAttend(models.Model):
    webinar = models.OneToOneField(LiveWebinar, on_delete=models.CASCADE)
    content = RichTextField()

class WebinarBenefit(models.Model):
    webinar = models.OneToOneField(LiveWebinar, on_delete=models.CASCADE)
    content = RichTextField()

class WebinarAreaCovered(models.Model):
    webinar = models.OneToOneField(LiveWebinar, on_delete=models.CASCADE)
    content = RichTextField()



class Instructor(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=150)
    organization = models.CharField(max_length=150, blank=True)
    bio = models.TextField()
    photo = models.ImageField(upload_to="webinars/instructors/")

    def __str__(self):
        return f"{self.name} – {self.designation}"
