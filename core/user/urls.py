from django.urls import path
from .views import login_user, register_user, logout_user

urlpatterns = [
    path("", login_user, name="user-login"),
    path('register/', register_user, name="register-page"),
    path("logout/", logout_user, name="logout-page")
]