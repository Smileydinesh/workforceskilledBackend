from rest_framework import serializers
from .models import RecordedWebinar


from rest_framework import serializers
from django.utils.timezone import localtime
from .models import RecordedWebinar,RecordedWebinarDetail


class RecordedWebinarFrontendSerializer(serializers.ModelSerializer):
    webinar_id = serializers.CharField(read_only=True)
    speaker = serializers.CharField(source="instructor.name")
    image = serializers.SerializerMethodField()
    speakerImage = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()  # ✅ FIX

    class Meta:
        model = RecordedWebinar
        fields = [
            "webinar_id", 
            "title",
            "speaker",
            "duration",
            "month",
            "category",
            "price",
            "image",
            "speakerImage",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.cover_image.url)

    def get_speakerImage(self, obj):
        request = self.context.get("request")
        if obj.instructor.photo:
            return request.build_absolute_uri(obj.instructor.photo.url)
        return None

    def get_duration(self, obj):
        return f"{obj.duration_minutes} minutes"

    def get_price(self, obj):
        if hasattr(obj, "pricing") and obj.pricing:
            return f"${obj.pricing.single_price:.2f}"
        return "$0.00"

    def get_month(self, obj):
        return obj.created_at.strftime("%B")

    def get_category(self, obj):
        return "AI & Productivity"




# recorded_webinars/serializers.py



class RecordedWebinarDetailPageSerializer(serializers.ModelSerializer):
    pricing = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    why_attend = serializers.SerializerMethodField()
    who_benefit = serializers.SerializerMethodField()
    areas_covered = serializers.SerializerMethodField()

    class Meta:
        model = RecordedWebinarDetail
        fields = [
            "overview",
            "why_attend",
            "who_benefit",
            "areas_covered",
            "format",
            "refund_policy",
            "pricing",
            "instructor",
            "cover_image",
        ]

    def _split(self, text):
        return [line.strip() for line in text.split("\n") if line.strip()]

    def get_why_attend(self, obj):
        return self._split(obj.why_attend)

    def get_who_benefit(self, obj):
        return self._split(obj.who_benefit)

    def get_areas_covered(self, obj):
        return self._split(obj.areas_covered)

    def get_pricing(self, obj):
        return {
            "single": obj.webinar.pricing.single_price,
            "multi": obj.webinar.pricing.multi_user_price,
        }

    def get_cover_image(self, obj):
        request = self.context["request"]
        return request.build_absolute_uri(obj.webinar.cover_image.url)

    def get_instructor(self, obj):
        request = self.context["request"]
        i = obj.webinar.instructor
        return {
            "name": i.name,
            "designation": i.designation,
            "company": i.organization,
            "bio": i.bio,
            "photo": request.build_absolute_uri(i.photo.url),
        }

