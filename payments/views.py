from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from webinars.models import LiveWebinar
from recorded_webinars.models import RecordedWebinar
from subscriptions.models import SubscriptionPlan, UserSubscription
from orders.models import Order, OrderItem

from subscriptions.utils import user_has_active_live_subscription
from payments.paypal import PayPalClient
from django.utils import timezone

from webinars.utils import user_has_purchased_live_webinar
from recorded_webinars.utils import user_has_purchased_recorded_webinar



class CreatePayPalOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response(
                {"detail": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
            status="PENDING"
        )

        # 🆓 FREE ORDER
        if order.total_amount <= 0:
            order.status = "PAID"
            order.save()
            return Response({"free": True})

        paypal = PayPalClient()
        paypal_order = paypal.create_order(order.total_amount)

        order.payment_id = paypal_order["id"]
        order.save()

        return Response({
            "paypal_order_id": paypal_order["id"]
        })



class CapturePayPalOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        paypal_order_id = request.data.get("paypal_order_id")

        if not paypal_order_id:
            return Response(
                {"detail": "Missing PayPal order ID"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(
            Order,
            payment_id=paypal_order_id,
            user=request.user
        )

        # 🔒 Prevent double processing
        if order.status == "PAID":
            return Response(
                {
                    "success": True,
                    "order_id": order.id,
                    "message": "Order already processed"
                }
            )

        paypal = PayPalClient()
        result = paypal.capture_order(paypal_order_id)

        if result.get("status") != "COMPLETED":
            return Response(
                {"detail": "Payment not completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Mark order paid
        order.status = "PAID"
        order.save()

        # 🔥 Activate subscription if present
        item = order.items.first()
        if item and item.subscription_plan:
            start = timezone.now()
            end = start + timezone.timedelta(
                days=30 * item.subscription_plan.duration_months
            )

            UserSubscription.objects.create(
                user=order.user,
                plan=item.subscription_plan,
                order=order,
                start_date=start,
                end_date=end,
                is_active=True
            )

        return Response({
            "success": True,
            "order_id": order.id
        })

