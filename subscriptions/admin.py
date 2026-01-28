# subscriptions/admin.py

from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "duration_months",
        "price",
        "is_active",
        "sort_order",
    )
    list_filter = ("is_active", "duration_months")
    search_fields = ("title",)
    ordering = ("sort_order", "price")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("is_active", "plan")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("start_date", "created_at")
