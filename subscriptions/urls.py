from django.urls import path
from .views import SubscriptionPlanListAPIView,PurchaseSubscriptionAPIView,CreateSubscriptionOrderAPIView

urlpatterns = [
    path("plans/", SubscriptionPlanListAPIView.as_view()),
    path("purchase/", PurchaseSubscriptionAPIView.as_view()),
    path(
        "subscriptions/order/",
        CreateSubscriptionOrderAPIView.as_view(),
        name="create-subscription-order"
    ),

]
