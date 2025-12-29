# cart/models.py
from django.db import models
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

    session_key = models.CharField(max_length=40)
    webinar_type = models.CharField(max_length=10, choices=WEBINAR_TYPE_CHOICES, default='LIVE')
    live_webinar = models.ForeignKey(LiveWebinar, on_delete=models.CASCADE, null=True, blank=True)  # Existing, now nullable
    recorded_webinar = models.ForeignKey(RecordedWebinar, on_delete=models.CASCADE, null=True, blank=True)  # New FK
    purchase_type = models.CharField(max_length=20, choices=PURCHASE_CHOICES)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session_key", "webinar_type", "live_webinar", "recorded_webinar", "purchase_type")  # Updated

    @property
    def webinar(self):  # Helper to get the active webinar (for backward compat)
        if self.webinar_type == "LIVE":
            return self.live_webinar
        return self.recorded_webinar

    def subtotal(self):
        return self.unit_price * self.quantity