from orders.models import OrderItem

def user_has_purchased_live_webinar(user, webinar):
    if not user.is_authenticated:
        return False

    return OrderItem.objects.filter(
        order__user=user,
        live_webinar=webinar,   # ✅ FIXED
        purchase_type__in=[
            "LIVE_SINGLE",
            "LIVE_MULTI",
            "COMBO_SINGLE",
            "COMBO_MULTI",
        ],
        order__status="PAID"
    ).exists()
