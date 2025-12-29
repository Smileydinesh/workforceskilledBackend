from django.contrib import admin
from .models import (
    LiveWebinar,
    Instructor,
    WebinarPricing,
    WebinarOverview,
    WebinarWhyAttend,
    WebinarBenefit,
    WebinarAreaCovered,
    WebinarCategory,
)


# ----------------------------
# INLINE SECTIONS
# ----------------------------

class WebinarPricingInline(admin.StackedInline):
    model = WebinarPricing
    can_delete = False
    extra = 0
    max_num = 1
    verbose_name_plural = "Pricing (Live / Recorded / Combo)"


class WebinarOverviewInline(admin.TabularInline):
    model = WebinarOverview
    extra = 1
    verbose_name_plural = "Webinar Overview (Paragraphs)"


class WebinarWhyAttendInline(admin.TabularInline):
    model = WebinarWhyAttend
    extra = 1
    verbose_name_plural = "Why You Should Attend (Points)"


class WebinarBenefitInline(admin.TabularInline):
    model = WebinarBenefit
    extra = 1
    verbose_name_plural = "Who Will Benefit (Points)"


class WebinarAreaCoveredInline(admin.TabularInline):
    model = WebinarAreaCovered
    extra = 1
    verbose_name_plural = "Areas Covered in the Session"


# ----------------------------
# INSTRUCTOR ADMIN
# ----------------------------

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "organization")
    search_fields = ("name", "designation", "organization")


@admin.register(WebinarCategory)
class WebinarCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}



# ----------------------------
# LIVE WEBINAR ADMIN
# ----------------------------
@admin.register(LiveWebinar)
class LiveWebinarAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "webinar_id",
        "category",
        "instructor",
        "start_datetime",
        "duration_minutes",
        "status",
    )

    list_filter = ("status", "category", "start_datetime")
    search_fields = ("title", "webinar_id")
    readonly_fields = ("webinar_id",)

    inlines = [
        WebinarPricingInline,
        WebinarOverviewInline,
        WebinarWhyAttendInline,
        WebinarBenefitInline,
        WebinarAreaCoveredInline,
    ]

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "title",
                "category",
                "instructor",
                "cover_image",
                "status",
            )
        }),
        ("Schedule", {
            "fields": (
                "start_datetime",
                "time_display",
                "duration_minutes",
            )
        }),
    )
