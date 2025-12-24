from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    webinar_title = serializers.CharField(source="webinar.title")
    webinar_id = serializers.CharField(source="webinar.webinar_id")
    instructor = serializers.CharField(source="webinar.instructor.name")
    duration = serializers.IntegerField(source="webinar.duration_minutes")
    cover_image = serializers.ImageField(source="webinar.cover_image")
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "webinar_id",
            "webinar_title",
            "instructor",
            "duration",
            "purchase_type",
            "unit_price",
            "quantity",
            "subtotal",
            "cover_image",
        ]

    def get_subtotal(self, obj):
        return obj.subtotal()
