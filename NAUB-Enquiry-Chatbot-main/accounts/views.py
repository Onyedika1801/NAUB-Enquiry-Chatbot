from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import UserProfile


def login_page(request):
    """Landing page — shows Google Sign-In button."""
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.onboarding_complete:
            return redirect("chatbot:index")
        return redirect("accounts:onboarding")
    return render(request, "accounts/login.html")


@login_required(login_url="/accounts/login/")
def onboarding(request):
    """First-login setup: choose user type + optional matric number."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.onboarding_complete:
        return redirect("chatbot:index")

    error = None

    if request.method == "POST":
        user_type = request.POST.get("user_type", "").strip()
        matric_number = request.POST.get("matric_number", "").strip()

        if user_type not in ("existing", "aspiring"):
            error = "Please select whether you are a current student or an aspiring student."
        else:
            profile.user_type = user_type
            if user_type == "existing" and matric_number:
                profile.matric_number = matric_number.upper()
            profile.onboarding_complete = True
            profile.save()
            return redirect("chatbot:index")

    # Get Google profile picture if available
    picture_url = None
    try:
        social = request.user.socialaccount_set.filter(provider="google").first()
        if social:
            picture_url = social.extra_data.get("picture")
    except Exception:
        pass

    context = {
        "display_name": profile.display_name(),
        "picture_url": picture_url,
        "error": error,
    }
    return render(request, "accounts/onboarding.html", context)


def logout_view(request):
    """Log the user out and send them to the login page."""
    logout(request)
    return redirect("accounts:login")
