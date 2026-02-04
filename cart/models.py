# cart/models.py
from django.db import models
from django.conf import settings   
from webinars.models import LiveWebinar
from recorded_webinars.models import RecordedWebinar  # Add this import

class CartItem(models.Model):
    WEBINAR_TYPE_CHOICES = (
        ("LIVE", "Live"),
        ("RECORDED", "Recorded"),
    )

    PURCHASE_CHOICES = (
        ("LIVE_SINGLE", "Live Single"),
        ("LIVE_MULTI", "Live Multi"),
        ("RECORDED_SINGLE", "Recorded Single"),
        ("RECORDED_MULTI", "Recorded Multi"),
        ("COMBO_SINGLE", "Combo Single"),
        ("COMBO_MULTI", "Combo Multi"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )

    webinar_type = models.CharField(max_length=10, choices=WEBINAR_TYPE_CHOICES)
    live_webinar = models.ForeignKey(LiveWebinar, null=True, blank=True, on_delete=models.CASCADE)
    recorded_webinar = models.ForeignKey(RecordedWebinar, null=True, blank=True, on_delete=models.CASCADE)

    purchase_type = models.CharField(max_length=20, choices=PURCHASE_CHOICES)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["session_key", "webinar_type"]),
        ]

    @property
    def webinar(self):  # Helper to get the active webinar (for backward compat)
        if self.webinar_type == "LIVE":
            return self.live_webinar
        return self.recorded_webinar

    def subtotal(self):
        return self.unit_price * self.quantity