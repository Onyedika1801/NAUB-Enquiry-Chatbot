"""
Django settings for NAUB Enquiry Chatbot project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY — change this in production!
SECRET_KEY = "django-insecure-naub-chatbot-change-this-in-production-2024"

DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ["*"]  # Restrict to your domain in production

# ── Applications ──────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",       # required by allauth

    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Our apps
    "accounts",
    "chatbot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # required by allauth
]

ROOT_URLCONF = "naub_chatbot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "naub_chatbot.wsgi.application"

# ── Database (SQLite for development) ─────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── Authentication ─────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Where to go after login / logout
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/onboarding/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"

# ── Allauth configuration ──────────────────────────────────
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True   # skip the "confirm social login" page

# ── Google OAuth credentials ───────────────────────────────
# Option A (recommended): set these as environment variables on your PC:
#   set GOOGLE_CLIENT_ID=your-id-here
#   set GOOGLE_CLIENT_SECRET=your-secret-here
#
# Option B: replace the os.environ.get() with your actual values directly.
# Get credentials at: console.cloud.google.com → APIs & Services → Credentials
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": "387449387609-ibmktf6gfbhdugopev7dcqgr85huun5v.apps.googleusercontent.com",
            "secret": "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",
            "key": "",
        },
    }
}

# ── Sessions ──────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400 * 7   # 7 days

# ── Static files ──────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Internationalization ───────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# ── Default primary key ────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
