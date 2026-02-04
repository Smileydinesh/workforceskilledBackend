# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from threading import Thread

from accounts.models import User
from .serializers import RegisterSerializer
from accounts.utils.email import send_welcome_email

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from subscriptions.models import UserSubscription
from accounts.serializers import (
    OrderSerializer,
    UserSubscriptionSerializer
)


def send_email_background(user):
    try:
        send_welcome_email(user)
    except Exception as e:
        print("Email error:", e)


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Send email asynchronously so Gunicorn is not blocked
        Thread(target=send_email_background, args=(user,)).start()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Account created successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED
        )



class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is None:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_200_OK)

# accounts/views.py

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        })





class UserDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # ---------------- USER INFO ----------------
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }

        # ---------------- ORDERS ----------------
        orders = (
            Order.objects
            .filter(user=user)
            .prefetch_related("items")
            .order_by("-created_at")
        )

        orders_data = OrderSerializer(orders, many=True).data

        # ---------------- SUBSCRIPTION ----------------
        subscription = (
            UserSubscription.objects
            .filter(user=user, is_active=True)
            .order_by("-end_date")
            .first()
        )

        subscription_data = (
            UserSubscriptionSerializer(subscription).data
            if subscription else None
        )

        # ---------------- FINAL RESPONSE ----------------
        return Response({
            "user": user_data,
            "subscription": subscription_data,
            "orders": orders_data,
        })
