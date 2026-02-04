from django.db import models
from django.conf import settings
from webinars.models import LiveWebinar
from recorded_webinars.models import RecordedWebinar
from django.core.exceptions import ValidationError

# from subscriptions.models import SubscriptionPlan

User = settings.AUTH_USER_MODEL

# orders/models.py
class Checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True,   
        blank=True        
    ) 

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=150, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)



class Order(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CANCELLED", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    payment_provider = models.CharField(max_length=30, default="PAYPAL")
    payment_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"


# orders/models.py




class OrderItem(models.Model):
    order = models.ForeignKey("orders.Order", related_name="items", on_delete=models.CASCADE)

    live_webinar = models.ForeignKey(
        "webinars.LiveWebinar",
        null=True, blank=True,
        on_delete=models.CASCADE
    )

    recorded_webinar = models.ForeignKey(
        RecordedWebinar,
        null=True, blank=True,
        on_delete=models.CASCADE
    )

    subscription_plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        null=True, blank=True,
        on_delete=models.CASCADE
    )

    purchase_type = models.CharField(max_length=30)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)


    def subtotal(self):
        return self.unit_price * self.quantity
    
    def clean(self):
        targets = [
            self.live_webinar,
            self.recorded_webinar,
            self.subscription_plan
        ]
        if sum(x is not None for x in targets) != 1:
            raise ValidationError(
                "OrderItem must have exactly one purchase target"
            )
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

