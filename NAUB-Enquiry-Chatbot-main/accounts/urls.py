from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("logout/", views.logout_view, name="logout"),
]
