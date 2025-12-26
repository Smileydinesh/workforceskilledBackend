from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="webinar.title")
    cover_image = serializers.SerializerMethodField()
    instructor = serializers.CharField(source="webinar.instructor.name")
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

    def get_cover_image(self, obj):
        request = self.context.get("request")
        if obj.webinar.cover_image and request:
            return request.build_absolute_uri(obj.webinar.cover_image.url)
        return None

    def get_subtotal(self, obj):
        return obj.unit_price * obj.quantity
