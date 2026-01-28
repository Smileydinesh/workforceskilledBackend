from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "title",
            "cover_image",
            "instructor",
            "purchase_type",
            "unit_price",
            "quantity",
            "subtotal",
        ]

    def get_title(self, obj):
        if obj.webinar:
            return obj.webinar.title
        if obj.subscription_plan:
            return obj.subscription_plan.title
        return ""

    def get_cover_image(self, obj):
        request = self.context.get("request")
        if obj.webinar and obj.webinar.cover_image and request:
            return request.build_absolute_uri(obj.webinar.cover_image.url)
        return None

    def get_instructor(self, obj):
        if obj.webinar:
            return obj.webinar.instructor.name
        return "Subscription"

    def get_subtotal(self, obj):
        return obj.unit_price * obj.quantity

