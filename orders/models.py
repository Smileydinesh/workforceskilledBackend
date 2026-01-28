from django.db import models
from django.conf import settings
from webinars.models import LiveWebinar
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

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"


# orders/models.py


class OrderItem(models.Model):
    order = models.ForeignKey(
        "orders.Order",
        related_name="items",
        on_delete=models.CASCADE
    )

    webinar = models.ForeignKey(
        "webinars.LiveWebinar",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    subscription_plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    purchase_type = models.CharField(max_length=30)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.unit_price * self.quantity

