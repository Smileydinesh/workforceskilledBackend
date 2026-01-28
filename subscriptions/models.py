from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# from orders.models import Order

User = settings.AUTH_USER_MODEL


class SubscriptionPlan(models.Model):
    title = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField()  # 6 or 12
    price = models.DecimalField(max_digits=8, decimal_places=2)

    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.duration_months} months)"


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        on_delete=models.PROTECT
    )

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(
                days=30 * self.plan.duration_months
            )
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.is_active and timezone.now() <= self.end_date

    def __str__(self):
        return f"{self.user} - {self.plan.title}"
