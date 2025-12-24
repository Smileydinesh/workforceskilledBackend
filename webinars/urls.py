from django.urls import path
from .views import LiveWebinarListAPIView, LiveWebinarDetailAPIView

urlpatterns = [
    path("live-webinars/", LiveWebinarListAPIView.as_view()),
    path("live-webinars/<str:webinar_id>/", LiveWebinarDetailAPIView.as_view()),
]
