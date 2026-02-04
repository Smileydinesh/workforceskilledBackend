from rest_framework import serializers
from django.contrib.auth import get_user_model

from rest_framework import serializers
from orders.models import Order, OrderItem
from subscriptions.models import UserSubscription

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "company",
            "country",
            "phone",
            "password",
            "confirm_password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "company": {"required": False, "allow_blank": True},
            "country": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
        }

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        validated_data.setdefault("company", "")
        validated_data.setdefault("country", "")
        validated_data.setdefault("phone", "")

        user = User.objects.create_user(**validated_data)
        return user



class OrderItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "item_type",
            "title",
            "purchase_type",
            "unit_price",
            "quantity",
        ]

    def get_item_type(self, obj):
        if obj.live_webinar:
            return "LIVE"
        if obj.recorded_webinar:
            return "RECORDED"
        if obj.subscription_plan:
            return "SUBSCRIPTION"
        return "UNKNOWN"

    def get_title(self, obj):
        if obj.live_webinar:
            return obj.live_webinar.title
        if obj.recorded_webinar:
            return obj.recorded_webinar.title
        if obj.subscription_plan:
            return obj.subscription_plan.name
        return ""


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.DecimalField(
        source="total_amount",
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "payment_provider",
            "total",
            "created_at",
            "items",
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name")

    class Meta:
        model = UserSubscription
        fields = [
            "plan_name",
            "start_date",
            "end_date",
            "is_active",
        ]
