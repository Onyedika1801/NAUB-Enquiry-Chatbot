from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Our custom accounts views (login page, onboarding, logout)
    # Must come BEFORE allauth so our /accounts/login/ and /accounts/logout/ take precedence
    path("accounts/", include("accounts.urls", namespace="accounts")),

    # Allauth handles Google OAuth callbacks (/accounts/google/login/, etc.)
    path("accounts/", include("allauth.urls")),

    # Chatbot (protected by login_required inside views)
    path("", include("chatbot.urls", namespace="chatbot")),
]
