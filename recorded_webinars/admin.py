from django.contrib import admin
from .models import (
    RecordedWebinar,
    RecordedWebinarPricing,
    RecordedWebinarDetail,
    RecordedWebinarOverview,
    RecordedWebinarWhyAttend,
    RecordedWebinarBenefit,
    RecordedWebinarAreaCovered,
)




class RecordedWebinarPricingInline(admin.StackedInline):
    model = RecordedWebinarPricing
    extra = 0
    max_num = 1




class RecordedWebinarOverviewInline(admin.TabularInline):
    model = RecordedWebinarOverview
    extra = 1


class RecordedWebinarWhyAttendInline(admin.TabularInline):
    model = RecordedWebinarWhyAttend
    extra = 1


class RecordedWebinarBenefitInline(admin.TabularInline):
    model = RecordedWebinarBenefit
    extra = 1


class RecordedWebinarAreaCoveredInline(admin.TabularInline):
    model = RecordedWebinarAreaCovered
    extra = 1



@admin.register(RecordedWebinar)
class RecordedWebinarAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "webinar_id",
        "instructor",
        "duration_minutes",
        "access_type",
        "is_published",
        "created_at",
    )

    list_filter = ("is_published", "access_type", "created_at")
    search_fields = ("title", "webinar_id", "instructor__name")
    readonly_fields = ("webinar_id", "created_at")

    inlines = [
        RecordedWebinarPricingInline, 
        RecordedWebinarOverviewInline,
        RecordedWebinarWhyAttendInline,
        RecordedWebinarBenefitInline,
        RecordedWebinarAreaCoveredInline,
    ]


@admin.register(RecordedWebinarDetail)
class RecordedWebinarDetailAdmin(admin.ModelAdmin):
    list_display = ("webinar", "format", "refund_policy")
    search_fields = ("webinar__title", "webinar__webinar_id")
