from django.contrib import admin
from .models import (
    RecordedWebinar,
    RecordedWebinarPricing,
    RecordedWebinarDetail,
)

# ----------------------------
# INLINE: PRICING
# ----------------------------

class RecordedWebinarPricingInline(admin.StackedInline):
    model = RecordedWebinarPricing
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name_plural = "Pricing (Recorded Webinar)"


# ----------------------------
# INLINE: DETAILS
# ----------------------------

class RecordedWebinarDetailInline(admin.StackedInline):
    model = RecordedWebinarDetail
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name_plural = "Recorded Webinar Details"

    fieldsets = (
        ("Overview", {
            "fields": ("overview",)
        }),
        ("Why You Should Attend", {
            "fields": ("why_attend",)
        }),
        ("Who Will Benefit", {
            "fields": ("who_benefit",)
        }),
        ("Areas Covered in the Session", {
            "fields": ("areas_covered",)
        }),
        ("Additional Information", {
            "fields": ("format", "refund_policy")
        }),
    )


# ----------------------------
# RECORDED WEBINAR ADMIN
# ----------------------------

@admin.register(RecordedWebinar)
class RecordedWebinarAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "duration_minutes",
        "access_type",
        "is_published",
    )

    list_filter = ("is_published", "access_type")
    search_fields = ("title", "instructor__name")
    readonly_fields = ("webinar_id",)

    inlines = [
        RecordedWebinarPricingInline,
        RecordedWebinarDetailInline,
    ]

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "title",
                "instructor",
                "cover_image",
                "preview_video",
            )
        }),
        ("Access & Duration", {
            "fields": (
                "duration_minutes",
                "access_type",
                "is_published",
            )
        }),
        ("System", {
            "fields": ("webinar_id",),
        }),
    )
