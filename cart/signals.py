# cart/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import CartItem

@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    session_key = request.session.session_key
    if not session_key:
        return

    CartItem.objects.filter(
        session_key=session_key,
        user__isnull=True
    ).update(user=user, session_key=None)
