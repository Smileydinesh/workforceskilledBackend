from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer
from orders.models import Order, OrderItem, Checkout
from django.shortcuts import get_object_or_404


from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from subscriptions.models import SubscriptionPlan, UserSubscription
from orders.models import Order
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscription
from orders.models import Order, OrderItem


class SubscriptionPlanListAPIView(APIView):
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)




# subscriptions/views.py
from orders.models import Order, OrderItem, Checkout

class PurchaseSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")

        plan = get_object_or_404(
            SubscriptionPlan,
            id=plan_id,
            is_active=True
        )

        # 🔒 Block duplicate active subscription
        if UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gte=timezone.now()
        ).exists():
            return Response(
                {"detail": "You already have an active subscription"},
                status=400
            )

        # 🔹 Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=plan.price,
            status="PENDING"# later → PAYMENT_PENDING
        )

        # 🔹 Create OrderItem (subscription)
        OrderItem.objects.create(
            order=order,
            subscription_plan=plan,
            purchase_type="SUBSCRIPTION",
            unit_price=plan.price,
            quantity=1
        )

        # 🔹 Create Checkout snapshot
        Checkout.objects.create(
            user=request.user,
            order=order,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            phone=request.user.phone,
            company=request.user.company,
            address="N/A",
            city="N/A",
            state="N/A",
            zip_code="N/A",
            country=request.user.country,
        )

        # 🔹 Activate subscription
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=30 * plan.duration_months)

        UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        return Response(
            {
                "message": "Subscription activated",
                "plan": plan.title,
                "valid_till": end_date,
            },
            status=status.HTTP_201_CREATED
        )



class CreateSubscriptionOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")

        if not plan_id:
            return Response(
                {"detail": "Subscription plan is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1️⃣ Validate plan
        try:
            plan = SubscriptionPlan.objects.get(
                id=plan_id,
                is_active=True
            )
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Invalid subscription plan"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2️⃣ Prevent duplicate active subscription
        if UserSubscription.objects.filter(
            user=user,
            is_active=True,
            end_date__gte=timezone.now()
        ).exists():
            return Response(
                {"detail": "You already have an active subscription"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ Create Order
        order = Order.objects.create(
            user=user,
            total_amount=plan.price,
            status="PAID"  # 🔥 Later: set after payment success
        )

        # 4️⃣ Create OrderItem (Subscription)
        OrderItem.objects.create(
            order=order,
            subscription_plan=plan,
            purchase_type="SUBSCRIPTION",
            unit_price=plan.price,
            quantity=1
        )

        # 5️⃣ Create UserSubscription
        start_date = timezone.now()
        end_date = start_date + timedelta(days=30 * plan.duration_months)

        UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            order=order,
            is_active=True
        )

        return Response(
            {
                "success": True,
                "message": "Subscription activated successfully",
                "plan": plan.title,
                "valid_until": end_date,
            },
            status=status.HTTP_201_CREATED
        )
