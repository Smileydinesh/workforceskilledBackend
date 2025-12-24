from django.urls import path
from .views import RegisterAPIView, LoginAPIView,LogoutAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
    # accounts/urls.py
    path("logout/", LogoutAPIView.as_view()),

]
