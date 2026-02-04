from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import CartItem
from webinars.models import LiveWebinar
from recorded_webinars.models import RecordedWebinar
from subscriptions.utils import user_has_active_live_subscription


LIVE_ALLOWED_PURCHASES = {
    "LIVE_SINGLE",
    "LIVE_MULTI",
    "RECORDED_SINGLE",
    "RECORDED_MULTI",
    "COMBO_SINGLE",
    "COMBO_MULTI",
}

RECORDED_ALLOWED_PURCHASES = {
    "RECORDED_SINGLE",
    "RECORDED_MULTI",
}

SUBSCRIPTION_BLOCKED_PURCHASES = {
    "LIVE_SINGLE",
    "LIVE_MULTI",
    "COMBO_SINGLE",
    "COMBO_MULTI",
}


class CartAPIView(APIView):

    # ---------------- SESSION KEY ----------------
    def get_session_key(self, request):
        if not request.session.session_key:
            request.session.save()
        return request.session.session_key

    # ---------------- CART QUERYSET ----------------
    def get_cart_queryset(self, request):
        if request.user.is_authenticated:
            return CartItem.objects.filter(user=request.user)
        else:
            session_key = self.get_session_key(request)
            return CartItem.objects.filter(session_key=session_key)

    # ---------------- PRICE ----------------
    def get_price(self, webinar, purchase_type, webinar_type):
        pricing = webinar.pricing

        if webinar_type == "LIVE":
            price_map = {
                "LIVE_SINGLE": pricing.live_single_price,
                "LIVE_MULTI": pricing.live_multi_price,
                "RECORDED_SINGLE": pricing.recorded_single_price,
                "RECORDED_MULTI": pricing.recorded_multi_price,
                "COMBO_SINGLE": pricing.combo_single_price,
                "COMBO_MULTI": pricing.combo_multi_price,
            }
        else:
            price_map = {
                "RECORDED_SINGLE": pricing.single_price,
                "RECORDED_MULTI": pricing.multi_user_price or pricing.single_price,
            }

        price = price_map.get(purchase_type)
        if price is None:
            raise ValueError("Invalid purchase type")

        return price

    # ================= GET CART =================
    def get(self, request):
        items = self.get_cart_queryset(request)

        data = []
        total = 0

        for item in items:
            webinar = item.webinar
            if not webinar:
                continue

            subtotal = item.subtotal()
            total += subtotal

            data.append({
                "id": item.id,
                "webinar_id": webinar.webinar_id,
                "title": webinar.title,
                "cover_image": request.build_absolute_uri(webinar.cover_image.url)
                if webinar.cover_image else None,
                "instructor": getattr(webinar.instructor, "name", None),
                "purchase_type": item.purchase_type,
                "price": float(item.unit_price),
                "quantity": item.quantity,
                "subtotal": float(subtotal),
                "webinar_type": item.webinar_type,
            })

        return Response({
            "items": data,
            "total": float(total),
            "count": len(data),
        })

    # ================= ADD TO CART =================
    def post(self, request):
        webinar_id = request.data.get("webinar_id")
        purchase_type = request.data.get("purchase_type")
        webinar_type = request.data.get("webinar_type")

        if webinar_type == "LIVE":
            webinar = get_object_or_404(LiveWebinar, webinar_id=webinar_id)
            live_webinar = webinar
            recorded_webinar = None
        else:
            webinar = get_object_or_404(RecordedWebinar, webinar_id=webinar_id)
            live_webinar = None
            recorded_webinar = webinar

        # 🔒 Subscription block (CLEAN)
        if (
            request.user.is_authenticated
            and user_has_active_live_subscription(request.user)
            and purchase_type in SUBSCRIPTION_BLOCKED_PURCHASES
        ):
            return Response(
                {"detail": "You already have an active subscription."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if webinar_type == "LIVE" and purchase_type not in LIVE_ALLOWED_PURCHASES:
            return Response({"error": "Invalid purchase type"}, status=400)

        if webinar_type == "RECORDED" and purchase_type not in RECORDED_ALLOWED_PURCHASES:
            return Response({"error": "Invalid purchase type"}, status=400)

        unit_price = self.get_price(webinar, purchase_type, webinar_type)

        if request.user.is_authenticated:
            item, created = CartItem.objects.get_or_create(
                user=request.user,
                webinar_type=webinar_type,
                live_webinar=live_webinar,
                recorded_webinar=recorded_webinar,
                purchase_type=purchase_type,
                defaults={"unit_price": unit_price, "quantity": 1},
            )
        else:
            session_key = self.get_session_key(request)
            item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                webinar_type=webinar_type,
                live_webinar=live_webinar,
                recorded_webinar=recorded_webinar,
                purchase_type=purchase_type,
                defaults={"unit_price": unit_price, "quantity": 1},
            )

        if not created:
            item.quantity += 1
            item.save()

        return Response({"message": "Added to cart"}, status=201)

    # ================= REMOVE ITEM =================
    def delete(self, request):
        item_id = request.data.get("item_id")

        if request.user.is_authenticated:
            CartItem.objects.filter(id=item_id, user=request.user).delete()
        else:
            session_key = self.get_session_key(request)
            CartItem.objects.filter(id=item_id, session_key=session_key).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
