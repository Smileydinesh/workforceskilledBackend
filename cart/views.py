# cart/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CartItem
from webinars.models import LiveWebinar
from recorded_webinars.models import RecordedWebinar  # Add this import


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

class CartAPIView(APIView):

    
    def get_session_key(self, request):
        if not request.session.session_key:
            request.session.save()   # THIS creates the session safely
        return request.session.session_key


    def get_price(self, webinar, purchase_type, webinar_type):  # Add webinar_type param
        if webinar_type == "LIVE":
            pricing = webinar.pricing
            price_map = {
                "LIVE_SINGLE": pricing.live_single_price,
                "LIVE_MULTI": pricing.live_multi_price,
                "RECORDED_SINGLE": pricing.recorded_single_price,  # Fallback, but won't be used for LIVE
                "RECORDED_MULTI": pricing.recorded_multi_price,
                "COMBO_SINGLE": pricing.combo_single_price,
                "COMBO_MULTI": pricing.combo_multi_price,
            }
        else:  # RECORDED
            pricing = webinar.pricing
            price_map = {
                "RECORDED_SINGLE": pricing.single_price,
                "RECORDED_MULTI": pricing.multi_user_price or pricing.single_price,  # Fallback if multi is null
            }
            # For recorded, map LIVE/COMBO to single_price as fallback (or raise error if invalid)
            if purchase_type not in price_map:
                price_map[purchase_type] = pricing.single_price  # Or validate strictly

        price = price_map.get(purchase_type)

        if price is None:
            raise ValueError("Invalid purchase type price mapping")

        return price


    # ---------------- GET CART ----------------
    def get(self, request):
        print("GET SESSION:", request.session.session_key)


        session_key = self.get_session_key(request)
        items = CartItem.objects.filter(session_key=session_key)

        data = []
        total = 0

        for item in items:
            webinar = item.webinar  # uses @property

            if webinar is None:
                continue  # SAFETY: skip corrupted rows

            subtotal = item.subtotal()
            total += subtotal

            data.append({
                "id": item.id,
                "webinar_id": webinar.webinar_id,
                "title": webinar.title,
                "cover_image": (
                    request.build_absolute_uri(webinar.cover_image.url)
                    if webinar.cover_image else None
                ),
                "instructor": webinar.instructor.name if hasattr(webinar, "instructor") else None,
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

    # ---------------- ADD TO CART ----------------
    # ---------------- ADD TO CART ----------------
    # ---------------- ADD TO CART ----------------
    def post(self, request):
        session_key = self.get_session_key(request)
        webinar_id = request.data.get("webinar_id")
        purchase_type = request.data.get("purchase_type", "LIVE_SINGLE")
        webinar_type = request.data.get("webinar_type", "LIVE")

        if webinar_type == "LIVE":
            webinar = get_object_or_404(LiveWebinar, webinar_id=webinar_id)
            live_webinar = webinar
            recorded_webinar = None
        else:
            webinar = get_object_or_404(RecordedWebinar, webinar_id=webinar_id)
            live_webinar = None
            recorded_webinar = webinar

        # Validate purchase type
        if webinar_type == "LIVE" and purchase_type not in LIVE_ALLOWED_PURCHASES:
            return Response({"error": "Invalid purchase type"}, status=400)

        if webinar_type == "RECORDED" and purchase_type not in RECORDED_ALLOWED_PURCHASES:
            return Response({"error": "Invalid purchase type"}, status=400)

        unit_price = self.get_price(webinar, purchase_type, webinar_type)

        item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            webinar_type=webinar_type,
            live_webinar=live_webinar,
            recorded_webinar=recorded_webinar,
            purchase_type=purchase_type,
            defaults={
                "unit_price": unit_price,
                "quantity": 1,
            }
        )

        if not created:
            item.quantity += 1
            item.save()

        return Response({"message": "Added to cart"}, status=201)


    # ---------------- REMOVE ITEM ----------------
    def delete(self, request):
        session_key = self.get_session_key(request)
        item_id = request.data.get("item_id")

        CartItem.objects.filter(
            id=item_id,
            session_key=session_key
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

    