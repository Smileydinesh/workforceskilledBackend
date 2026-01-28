from django.utils import timezone
from subscriptions.models import UserSubscription


def user_has_active_live_subscription(user):
    if not user or not user.is_authenticated:
        return False

    return UserSubscription.objects.filter(
        user=user,
        is_active=True,
        end_date__gte=timezone.now()
    ).exists()
