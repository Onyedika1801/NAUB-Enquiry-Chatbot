import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .engine import ChatbotEngine
from .models import ChatSession, ConversationLog

# Initialise the engine once at module load (not per request)
chatbot_engine = ChatbotEngine()


def _get_or_create_session(request):
    """Return the current ChatSession for this user, creating one if needed."""
    user = request.user
    session_key = "chat_session_id"
    session_id = request.session.get(session_key)

    if session_id:
        try:
            return ChatSession.objects.get(session_id=session_id, user=user)
        except ChatSession.DoesNotExist:
            pass  # stale session ID — create a fresh one below

    chat_session = ChatSession.objects.create(user=user)
    request.session[session_key] = str(chat_session.session_id)
    return chat_session


@login_required(login_url="/accounts/login/")
def index(request):
    """Main chat interface — requires login."""
    # Redirect to onboarding if not completed yet
    try:
        if not request.user.profile.onboarding_complete:
            return redirect("accounts:onboarding")
    except Exception:
        return redirect("accounts:onboarding")

    chat_session = _get_or_create_session(request)

    history = chat_session.logs.all().values(
        "user_query", "bot_response", "timestamp"
    )

    # Build context for the template
    profile = request.user.profile
    picture_url = None
    try:
        social = request.user.socialaccount_set.filter(provider="google").first()
        if social:
            picture_url = social.extra_data.get("picture")
    except Exception:
        pass

    context = {
        "history": list(history),
        "session_id": str(chat_session.session_id),
        "display_name": profile.display_name(),
        "user_type": profile.user_type,
        "matric_number": profile.matric_number,
        "picture_url": picture_url,
    }
    return render(request, "chatbot/index.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    API endpoint that receives a user query and returns a bot response.
    Expects JSON body: {"message": "...", "session_id": "uuid"}
    Returns JSON:      {"response": "...", "intent": "...", "score": 0.95}
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id", "")

        if not user_message:
            return JsonResponse({"error": "Empty message received."}, status=400)

        bot_response, matched_intent, similarity_score = chatbot_engine.get_response(
            user_message
        )

        try:
            chat_session = ChatSession.objects.get(
                session_id=session_id, user=request.user
            )
        except ChatSession.DoesNotExist:
            chat_session = ChatSession.objects.create(user=request.user)

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


@login_required(login_url="/accounts/login/")
def clear_session(request):
    """Clear the current chat session and start a fresh one."""
    if "chat_session_id" in request.session:
        del request.session["chat_session_id"]
    return JsonResponse({"status": "Session cleared."})
