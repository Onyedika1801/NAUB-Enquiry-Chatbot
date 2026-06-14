from django.contrib import admin
from .models import ChatSession, ConversationLog, KnowledgeEntry


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "started_at", "message_count")
    readonly_fields = ("session_id", "started_at")

    def message_count(self, obj):
        return obj.logs.count()
    message_count.short_description = "Messages"


@admin.register(ConversationLog)
class ConversationLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user_query_short", "matched_intent", "similarity_score")
    list_filter = ("matched_intent",)
    search_fields = ("user_query", "bot_response")
    readonly_fields = ("timestamp", "session", "user_query", "matched_intent",
                       "similarity_score", "bot_response")

    def user_query_short(self, obj):
        return obj.user_query[:60] + "..." if len(obj.user_query) > 60 else obj.user_query
    user_query_short.short_description = "User Query"


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ("intent", "is_active", "last_updated")
    list_filter = ("is_active",)
    search_fields = ("intent", "patterns", "response")
