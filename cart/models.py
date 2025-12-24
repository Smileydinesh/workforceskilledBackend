# cart/models.py
from django.db import models
from webinars.models import LiveWebinar

class CartItem(models.Model):
    PURCHASE_CHOICES = (
        ("LIVE_SINGLE", "Live Single"),
        ("LIVE_MULTI", "Live Multi"),
        ("RECORDED_SINGLE", "Recorded Single"),
        ("RECORDED_MULTI", "Recorded Multi"),
        ("COMBO_SINGLE", "Combo Single"),
        ("COMBO_MULTI", "Combo Multi"),
    )

    session_key = models.CharField(max_length=40)
    webinar = models.ForeignKey(LiveWebinar, on_delete=models.CASCADE)
    purchase_type = models.CharField(max_length=20, choices=PURCHASE_CHOICES)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session_key", "webinar", "purchase_type")

    def subtotal(self):
        return self.unit_price * self.quantity
