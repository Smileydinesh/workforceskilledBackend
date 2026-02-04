from django.urls import path
from .views import (
    CreatePayPalOrderAPIView,
    CapturePayPalOrderAPIView,
)

urlpatterns = [
    path("paypal/create/", CreatePayPalOrderAPIView.as_view()),
    path("paypal/capture/", CapturePayPalOrderAPIView.as_view()),
]
