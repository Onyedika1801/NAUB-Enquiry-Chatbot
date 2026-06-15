from django.db import models
from django.conf import settings
import uuid


class ChatSession(models.Model):
    """One conversation thread per user (or anonymous browser session)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="chat_sessions",
    )
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_label = self.user.email if self.user else "anonymous"
        return f"Session [{user_label}] — {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-started_at"]


class ConversationLog(models.Model):
    """Each user query and bot response within a session."""
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="logs"
    )
    user_query = models.TextField()
    matched_intent = models.CharField(max_length=100)
    similarity_score = models.FloatField(default=0.0)
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.matched_intent}] {self.user_query[:50]}..."

    class Meta:
        ordering = ["timestamp"]


class KnowledgeEntry(models.Model):
    """
    Mirror of the JSON knowledge base — lets admins view and
    manage intents via the Django admin / knowledge base dashboard.
    """
    intent = models.CharField(max_length=100, unique=True)
    patterns = models.TextField(help_text="One pattern per line")
    response = models.TextField()
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.intent

    class Meta:
        ordering = ["intent"]
        verbose_name = "Knowledge Base Entry"
        verbose_name_plural = "Knowledge Base Entries"
