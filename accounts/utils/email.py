from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user):
    subject = "Welcome to Workforce Webinars 🎉"

    message = f"""
Hi {user.first_name or user.email},

Welcome to WorkforceSkilled Webinars!

Your account has been created successfully.
You can now log in and access live and recorded webinars.

If you did not create this account, please ignore this email.

— WorkForceSkilled Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
