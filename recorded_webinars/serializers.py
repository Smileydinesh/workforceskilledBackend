from rest_framework import serializers
from .models import RecordedWebinar
from rest_framework import serializers
from .models import (
    RecordedWebinar,
    RecordedWebinarPricing,
    RecordedWebinarOverview,
    RecordedWebinarWhyAttend,
    RecordedWebinarBenefit,
    RecordedWebinarAreaCovered,
)
from webinars.serializers import InstructorSerializer



from rest_framework import serializers
from django.utils.timezone import localtime
from .models import RecordedWebinar


from rest_framework import serializers
from .models import RecordedWebinar
from webinars.serializers import InstructorSerializer


class RecordedWebinarFrontendSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()
    cover_image = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = RecordedWebinar
        fields = [
            "webinar_id",
            "title",
            "cover_image",
            "duration_minutes",
            "instructor",
            "month",
            "category",
            "display_price",
        ]

    def get_cover_image(self, obj):
        request = self.context.get("request")
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_display_price(self, obj):
        if hasattr(obj, "pricing") and obj.pricing:
            return obj.pricing.single_price
        return 0

    def get_month(self, obj):
        return obj.created_at.strftime("%Y-%m")

    def get_category(self, obj):
        return obj.category.name if hasattr(obj, "category") and obj.category else None



class RecordedWebinarPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordedWebinarPricing
        fields = [
            "single_price",
            "multi_user_price",
        ]



class RecordedWebinarDetailPageSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()
    pricing = RecordedWebinarPricingSerializer(allow_null=True)

    cover_image = serializers.SerializerMethodField()

    overview = serializers.SerializerMethodField()
    why_attend = serializers.SerializerMethodField()
    who_benefits = serializers.SerializerMethodField()
    areas_covered = serializers.SerializerMethodField()

    format = serializers.CharField(source="details.format")
    refund_policy = serializers.CharField(source="details.refund_policy")

    class Meta:
        model = RecordedWebinar
        fields = [
            "webinar_id",
            "title",
            "description",
            "cover_image",
            "duration_minutes",
            "instructor",
            "pricing",
            "overview",
            "why_attend",
            "who_benefits",
            "areas_covered",
            "format",
            "refund_policy",
        ]

    def get_cover_image(self, obj):
        request = self.context.get("request")
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None
    
    def get_overview(self, obj):
        return obj.recordedwebinaroverview.content if hasattr(obj, "recordedwebinaroverview") else ""

    def get_why_attend(self, obj):
        return obj.recordedwebinarwhyattend.content if hasattr(obj, "recordedwebinarwhyattend") else ""

    def get_who_benefits(self, obj):
        return obj.recordedwebinarbenefit.content if hasattr(obj, "recordedwebinarbenefit") else ""

    def get_areas_covered(self, obj):
        return obj.recordedwebinarareacovered.content if hasattr(obj, "recordedwebinarareacovered") else ""


