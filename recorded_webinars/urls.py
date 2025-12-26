from django.urls import path
from .views import (
    RecordedWebinarListAPIView,
    RecordedWebinarDetailPageAPIView,
)

urlpatterns = [
    path(
        "recorded-webinars/",
        RecordedWebinarListAPIView.as_view(),
    ),
    path(
        "recorded-webinars/<str:webinar_id>/",
        RecordedWebinarDetailPageAPIView.as_view(),
    ),
]
