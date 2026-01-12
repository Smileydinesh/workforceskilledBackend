from rest_framework import serializers
from django.utils.timezone import localtime
from zoneinfo import ZoneInfo
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
    # time_display = serializers.SerializerMethodField()
    # date_display = serializers.SerializerMethodField()

    class Meta:
        model = LiveWebinar
        fields = [
            "webinar_id",
            "title",
            "cover_image",
            "instructor",
            "start_datetime", 
            "duration_minutes",
            "display_price",
            
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
    pst = serializers.SerializerMethodField()
    est = serializers.SerializerMethodField()

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
            "start_datetime",
            "duration_minutes",
            "date_display",
            "pst",
            "est",
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

    def get_pst(self, obj):
        return obj.start_datetime.astimezone(
            ZoneInfo("America/Los_Angeles")
        ).strftime("%I:%M %p PST")

    def get_est(self, obj):
        return obj.start_datetime.astimezone(
            ZoneInfo("America/New_York")
        ).strftime("%I:%M %p EST")

    # -------- CMS HTML FIELDS --------

    def get_overview(self, obj):
        return obj.webinaroverview.content if hasattr(obj, "webinaroverview") else ""

    def get_why_attend(self, obj):
        return obj.webinarwhyattend.content if hasattr(obj, "webinarwhyattend") else ""

    def get_who_benefits(self, obj):
        return obj.webinarbenefit.content if hasattr(obj, "webinarbenefit") else ""

    def get_areas_covered(self, obj):
        return obj.webinarareacovered.content if hasattr(obj, "webinarareacovered") else ""
