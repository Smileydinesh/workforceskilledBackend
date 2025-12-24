# cart/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CartItem
from webinars.models import LiveWebinar


class CartAPIView(APIView):

    def get_session_key(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def get_price(self, webinar, purchase_type):
        pricing = webinar.pricing

        price_map = {
            "LIVE_SINGLE": pricing.live_single_price,
            "LIVE_MULTI": pricing.live_multi_price,
            "RECORDED_SINGLE": pricing.recorded_single_price,
            "RECORDED_MULTI": pricing.recorded_multi_price,
            "COMBO_SINGLE": pricing.combo_single_price,
            "COMBO_MULTI": pricing.combo_multi_price,
        }

        return price_map[purchase_type]

    # ---------------- GET CART ----------------
    def get(self, request):
        session_key = self.get_session_key(request)
        items = CartItem.objects.filter(session_key=session_key)

        data = []
        total = 0

        for item in items:
            subtotal = item.subtotal()
            total += subtotal

            data.append({
                "id": item.id,
                "webinar_id": item.webinar.webinar_id,
                "title": item.webinar.title,
                "cover_image": request.build_absolute_uri(item.webinar.cover_image.url),
                "instructor": item.webinar.instructor.name,
                "purchase_type": item.purchase_type,
                "price": item.unit_price,
                "quantity": item.quantity,
                "subtotal": subtotal,
            })

        return Response({"items": data, "total": total,"count": len(items) })

    # ---------------- ADD TO CART ----------------
    def post(self, request):
        session_key = self.get_session_key(request)
        webinar_id = request.data.get("webinar_id")
        purchase_type = request.data.get("purchase_type", "LIVE_SINGLE")

        webinar = get_object_or_404(LiveWebinar, webinar_id=webinar_id)

        unit_price = self.get_price(webinar, purchase_type)

        CartItem.objects.create(
            session_key=session_key,
            webinar=webinar,
            purchase_type=purchase_type,
            unit_price=unit_price,
        )

        return Response(
            {"message": "Added to cart"},
            status=status.HTTP_201_CREATED
        )

    # ---------------- REMOVE ITEM ----------------
    def delete(self, request):
        session_key = self.get_session_key(request)
        item_id = request.data.get("item_id")

        CartItem.objects.filter(
            id=item_id,
            session_key=session_key
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
