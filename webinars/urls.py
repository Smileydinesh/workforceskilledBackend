# webinars/urls.py

from django.urls import path
from .views import (
    LiveWebinarListAPIView,
    LiveWebinarDetailAPIView,
    LiveWebinarFilterAPIView,
)

urlpatterns = [
    path("live-webinars/", LiveWebinarListAPIView.as_view(), name="live-webinars"),
    path("live-webinars/filters/", LiveWebinarFilterAPIView.as_view(), name="live-webinar-filters"),
    path("live-webinars/<str:webinar_id>/", LiveWebinarDetailAPIView.as_view(), name="live-webinar-detail"),
]
