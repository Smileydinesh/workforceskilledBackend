# webinars/urls.py

from django.urls import path
from .views import (
    LiveWebinarListAPIView,
    LiveWebinarDetailAPIView,
    LiveWebinarFilterAPIView,JoinLiveWebinarAPIView,GlobalSearchAPIView,InstructorListAPIView
)

urlpatterns = [
    path("live-webinars/", LiveWebinarListAPIView.as_view(), name="live-webinars"),
    path("live-webinars/filters/", LiveWebinarFilterAPIView.as_view(), name="live-webinar-filters"),
    path("live-webinars/<str:webinar_id>/", LiveWebinarDetailAPIView.as_view(), name="live-webinar-detail"),
    path("live-webinars/<str:webinar_id>/join/",JoinLiveWebinarAPIView.as_view(),name="join-live-webinar",),
    path("search/", GlobalSearchAPIView.as_view(), name="global-search"),
    path("instructors/", InstructorListAPIView.as_view(), name="instructors"),

]
