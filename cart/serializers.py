from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    webinar_title = serializers.SerializerMethodField()  # Dynamic source
    webinar_id = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
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
            "webinar_type",  # Add this for frontend if needed (e.g., to show icons)
        ]

    def get_webinar_title(self, obj):
        return obj.webinar.title

    def get_webinar_id(self, obj):
        return obj.webinar.webinar_id

    def get_instructor(self, obj):
        return obj.webinar.instructor.name

    def get_duration(self, obj):
        return obj.webinar.duration_minutes

    def get_cover_image(self, obj):
        # Return URL; frontend will handle absolute URI
        return obj.webinar.cover_image.url if obj.webinar.cover_image else None

    def get_subtotal(self, obj):
        return obj.subtotal()