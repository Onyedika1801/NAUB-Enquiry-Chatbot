from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ("existing", "Existing NAUB Student"),
        ("aspiring", "Aspiring Student"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, blank=True, default=""
    )
    matric_number = models.CharField(max_length=30, blank=True, default="")
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.user.get_full_name() or self.user.email
        return f"{name} — {self.get_user_type_display()}"

    def display_name(self):
        return self.user.get_full_name() or self.user.email.split("@")[0]

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class ChatMessage(models.Model):
    # Links the message to the Google-logged-in user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_messages")
    # Identifies which conversation session this belongs to
    chat_id = models.CharField(max_length=100, default="default_session")
    # Tracks who said it: 'user' or 'bot'
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    # Stores the text contents
    message = models.TextField()
    # Saves the date and time automatically
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp'] # Keeps messages in order from oldest to newest

    def __str__(self):
        return f"{self.user.username} - {self.sender}: {self.message[:20]}"
