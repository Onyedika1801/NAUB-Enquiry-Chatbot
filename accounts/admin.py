from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_type", "matric_number", "onboarding_complete", "created_at")
    list_filter = ("user_type", "onboarding_complete")
    search_fields = ("user__email", "user__first_name", "matric_number")
    readonly_fields = ("created_at",)
