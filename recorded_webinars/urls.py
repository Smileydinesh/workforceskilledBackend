from django.urls import path
from .views import (
    RecordedWebinarListAPIView,
    RecordedWebinarDetailAPIView,
    RecordedWebinarFilterAPIView,
)

urlpatterns = [
    # LIST (with query params filtering)
    path(
        "recorded-webinars/",
        RecordedWebinarListAPIView.as_view(),
    ),

    # FILTER METADATA (months, instructors, categories)
    path(
        "recorded-webinars/filters/",
        RecordedWebinarFilterAPIView.as_view(),
    ),

    # DETAIL PAGE
    path(
        "recorded-webinars/<str:webinar_id>/",
        RecordedWebinarDetailAPIView.as_view(),
        name="recorded-webinar-detail",
    ),
]
