from rest_framework import serializers
from .models import SubscriptionPlan


# subscriptions/serializers.py
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "title",
            "duration_months",
            "price",
            "description",
            "features",
        ]

