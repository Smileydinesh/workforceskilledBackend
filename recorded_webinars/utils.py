from orders.models import OrderItem

def user_has_purchased_recorded_webinar(user, webinar):
    if not user.is_authenticated:
        return False

    return OrderItem.objects.filter(
        order__user=user,
        recorded_webinar=webinar,
        purchase_type__in=[
            "RECORDED_SINGLE",
            "RECORDED_MULTI",
            "COMBO_SINGLE",
            "COMBO_MULTI",
        ],
        order__status="PAID"
    ).exists()
