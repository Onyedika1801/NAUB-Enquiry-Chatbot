import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .engine import ChatbotEngine
from .models import ChatSession, ConversationLog

# Initialize the chatbot engine once at module load (not per request)
chatbot_engine = ChatbotEngine()


def index(request):
    """Render the main chat interface page."""
    # Create or retrieve a session for this user
    session_id = request.session.get("chat_session_id")
    if not session_id:
        chat_session = ChatSession.objects.create()
        request.session["chat_session_id"] = str(chat_session.session_id)
    else:
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            chat_session = ChatSession.objects.create()
            request.session["chat_session_id"] = str(chat_session.session_id)

    # Load prior conversation history for this session
    history = chat_session.logs.all().values(
        "user_query", "bot_response", "timestamp"
    )
    context = {
        "history": list(history),
        "session_id": str(chat_session.session_id),
    }
    return render(request, "chatbot/index.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    API endpoint that receives a user query and returns a bot response.
    Expects JSON body: {"message": "user query here", "session_id": "uuid"}
    Returns JSON:      {"response": "...", "intent": "...", "score": 0.95}
    """
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id", "")

        if not user_message:
            return JsonResponse({"error": "Empty message received."}, status=400)

        # Get chatbot response
        bot_response, matched_intent, similarity_score = chatbot_engine.get_response(
            user_message
        )

        # Retrieve or create session
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            chat_session = ChatSession.objects.create()

        # Log the conversation (anonymized — no PII stored)
        ConversationLog.objects.create(
            session=chat_session,
            user_query=user_message,
            matched_intent=matched_intent,
            similarity_score=similarity_score,
            bot_response=bot_response,
        )

        return JsonResponse({
            "response": bot_response,
            "intent": matched_intent,
            "score": similarity_score,
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)


def clear_session(request):
    """Clear the current chat session and start a new one."""
    if "chat_session_id" in request.session:
        del request.session["chat_session_id"]
    return JsonResponse({"status": "Session cleared."})
