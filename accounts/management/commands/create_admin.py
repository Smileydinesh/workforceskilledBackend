from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = os.environ.get("Admin@gmail.com")
        password = os.environ.get("Admin@123")

        if not email or not password:
            print("ADMIN_EMAIL or ADMIN_PASSWORD not set")
            return

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password
            )
            print("Admin created")
        else:
            print("Admin already exists")
