from django.db import models
import uuid


class ChatSession(models.Model):
    """Tracks a single browser session for multi-turn conversation."""
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id} — {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-started_at"]


class ConversationLog(models.Model):
    """Stores each user query and the chatbot response for review and improvement."""
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
    Optional: mirror of the JSON knowledge base in the database.
    Allows admins to view knowledge base entries via the Django admin panel.
    """
    intent = models.CharField(max_length=100, unique=True)
    patterns = models.TextField(help_text="Comma-separated list of patterns")
    response = models.TextField()
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.intent

    class Meta:
        ordering = ["intent"]
        verbose_name = "Knowledge Base Entry"
        verbose_name_plural = "Knowledge Base Entries"
