from rest_framework import serializers
from django.utils.timezone import localtime
from .models import (
    LiveWebinar,
    Instructor,
    WebinarPricing,
    WebinarOverview,
    WebinarWhyAttend,
    WebinarBenefit,
    WebinarAreaCovered,
)

# ---------------- INSTRUCTOR ----------------
class InstructorSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = [
            "name",
            "designation",
            "organization",
            "bio",
            "photo",
        ]

    def get_photo(self, obj):
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


# ---------------- LIST SERIALIZER ----------------
class LiveWebinarSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()
    cover_image = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    time_display = serializers.SerializerMethodField()
    date_display = serializers.SerializerMethodField()

    class Meta:
        model = LiveWebinar
        fields = [
            "webinar_id",
            "title",
            "cover_image",
            "instructor",
            "duration_minutes",
            "display_price",
            "time_display",
            "date_display",
            "status",
        ]

    def get_cover_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.cover_image.url)

    def get_display_price(self, obj):
        """
        Lowest price shown on listing card
        """
        if hasattr(obj, "pricing") and obj.pricing:
            return obj.pricing.live_single_price
        return None

    def get_time_display(self, obj):
        return localtime(obj.start_datetime).strftime("%I:%M %p")

    def get_date_display(self, obj):
        return obj.start_datetime.strftime("%A, %B %d, %Y")


# ---------------- PRICING ----------------
class WebinarPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarPricing
        fields = [
            "live_single_price",
            "live_multi_price",
            "recorded_single_price",
            "recorded_multi_price",
            "combo_single_price",
            "combo_multi_price",
        ]


# ---------------- DETAIL SERIALIZER ----------------
class LiveWebinarDetailSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()
    pricing = WebinarPricingSerializer(allow_null=True)

    date_display = serializers.SerializerMethodField()
    time_display = serializers.SerializerMethodField()

    overview = serializers.SerializerMethodField()
    why_attend = serializers.SerializerMethodField()
    who_benefits = serializers.SerializerMethodField()
    areas_covered = serializers.SerializerMethodField()

    class Meta:
        model = LiveWebinar
        fields = [
            "webinar_id",
            "title",
            "description",
            "status",
            "date_display",
            "time_display",
            "duration_minutes",
            "instructor",
            "pricing",
            "overview",
            "why_attend",
            "who_benefits",
            "areas_covered",
        ]

    # -------- DATE / TIME --------
    def get_date_display(self, obj):
        return obj.start_datetime.strftime("%A, %B %d, %Y")

    def get_time_display(self, obj):
        return localtime(obj.start_datetime).strftime("%I:%M %p")

    # -------- CONTENT SECTIONS --------
    def get_overview(self, obj):
        return [o.paragraph for o in obj.webinaroverview_set.all()]

    def get_why_attend(self, obj):
        return [w.point for w in obj.webinarwhyattend_set.all()]

    def get_who_benefits(self, obj):
        benefits = obj.webinarbenefit_set.all()
        return {
            "subtitle": benefits.first().subtitle if benefits.exists() else "",
            "points": [b.point for b in benefits],
        }

    def get_areas_covered(self, obj):
        return [a.point for a in obj.webinarareacovered_set.all()]
