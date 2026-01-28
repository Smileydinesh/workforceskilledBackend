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
from subscriptions.utils import user_has_active_live_subscription




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
            "is_test",          
            "cover_image",
            "instructor",
            "start_datetime", 
            "duration_minutes",
            "display_price",
            
            "status",
        ]

    def get_cover_image(self, obj):
        request = self.context.get("request")

        if obj.cover_image and hasattr(obj.cover_image, "url"):
            return request.build_absolute_uri(obj.cover_image.url)

        return None


    def get_display_price(self, obj):
        request = self.context.get("request")

        if not hasattr(obj, "pricing") or not obj.pricing:
            return None

        if request and request.user.is_authenticated:
            if user_has_active_live_subscription(request.user):
                return 0

        return obj.pricing.live_single_price


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
    pricing = serializers.SerializerMethodField()


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
            "is_test",
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

    def get_pricing(self, obj):
        pricing = obj.pricing
        if not pricing:
            return None

        request = self.context.get("request")

        data = {
            "live_single_price": pricing.live_single_price,
            "live_multi_price": pricing.live_multi_price,
            "recorded_single_price": pricing.recorded_single_price,
            "recorded_multi_price": pricing.recorded_multi_price,
            "combo_single_price": pricing.combo_single_price,
            "combo_multi_price": pricing.combo_multi_price,
        }

        # 🔒 SUBSCRIPTION OVERRIDE
        if request and request.user.is_authenticated:
            if user_has_active_live_subscription(request.user):
                data["live_single_price"] = 0
                data["live_multi_price"] = 0

                # Combo = recorded only
                data["combo_single_price"] = pricing.recorded_single_price
                data["combo_multi_price"] = pricing.recorded_multi_price

        return data


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
