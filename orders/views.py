from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from orders.serializers import OrderItemSerializer

from cart.models import CartItem
from .models import Order, OrderItem
from orders.models import Checkout

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from orders.models import Order, OrderItem, Checkout
from rest_framework_simplejwt.authentication import JWTAuthentication


class CheckoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_session_key(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    # 🔹 STEP 1: GET checkout data
    def get(self, request):
        session_key = self.get_session_key(request)
        cart_items = CartItem.objects.filter(session_key=session_key)

        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=400)

        serializer = OrderItemSerializer(
            cart_items,
            many=True,
            context={"request": request}
        )

        total = sum(item.subtotal() for item in cart_items)

        return Response({
            "user": {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": request.user.phone,
                "company": request.user.company,
                "country": request.user.country,
            },
            "cart": {
                "items": serializer.data,   # 🔥 THIS FIXES IMAGES
                "subtotal": total,
                "total": total,
            }
        })


      

    # 🔹 STEP 2: CREATE ORDER + CHECKOUT
    def post(self, request):
        session_key = self.get_session_key(request)
        cart_items = CartItem.objects.filter(session_key=session_key)

        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=400)

        total = sum(item.subtotal() for item in cart_items)

        # 🔒 Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        # 🔒 Lock items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                live_webinar=item.live_webinar if item.webinar_type == "LIVE" else None,
                recorded_webinar=item.recorded_webinar if item.webinar_type == "RECORDED" else None,
                purchase_type=item.purchase_type,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )


        # 🔒 Save checkout address
        Checkout.objects.create(
            user=request.user,
            order=order,
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            email=request.data["email"],
            phone=request.data["phone"],
            company=request.data.get("company", ""),
            address=request.data["address"],
            city=request.data["city"],
            state=request.data["state"],
            zip_code=request.data["zip_code"],
            country=request.data["country"],
        )

        # 🧹 Clear cart
        cart_items.delete()

        return Response({
            "message": "Checkout successful",
            "order_id": order.id,
            "total": order.total_amount,
        }, status=status.HTTP_201_CREATED)



class OrderDetailsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        # 🔒 Billing address
        checkout = get_object_or_404(
            Checkout,
            order=order,
            user=request.user
        )

        items_data = []
        for item in order.items.all():
            if item.live_webinar:
                title = item.live_webinar.title
                item_type = "LIVE_WEBINAR"
            elif item.recorded_webinar:
                title = item.recorded_webinar.title
                item_type = "RECORDED_WEBINAR"
            elif item.subscription_plan:
                title = item.subscription_plan.name
                item_type = "SUBSCRIPTION"
            else:
                title = "Unknown"
                item_type = "UNKNOWN"

            items_data.append({
                "title": title,
                "type": item_type,
                "quantity": item.quantity,
                "subtotal": item.unit_price * item.quantity,
            })

        return Response({
            "id": order.id,
            "status": order.status,
            "total": order.total_amount,
            "billing": {
                "first_name": checkout.first_name,
                "last_name": checkout.last_name,
                "email": checkout.email,
                "phone": checkout.phone,
                "address": checkout.address,
                "city": checkout.city,
                "state": checkout.state,
                "zip_code": checkout.zip_code,
                "country": checkout.country,
            },
            "items": items_data
        }, status=status.HTTP_200_OK)
