from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from orders.serializers import OrderItemSerializer

from cart.models import CartItem
from .models import Order, OrderItem
from orders.models import Checkout


class CheckoutAPIView(APIView):
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
                webinar=item.webinar,
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
