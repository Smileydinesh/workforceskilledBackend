# orders/urls.py ✅ CORRECT
from django.urls import path
from .views import CheckoutAPIView,OrderDetailsAPIView

urlpatterns = [
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
    path(
        "<int:order_id>/details/",
        OrderDetailsAPIView.as_view(),
        name="order-details"
    ),
]
