import logging
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from services.chat_service import ChatService
from models.schemas import ChatMessageRequest, ChatSessionCreateRequest

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat/message", methods=["POST", "OPTIONS"])
@chat_bp.route("/api/chat", methods=["POST", "OPTIONS"])
@require_auth
def handle_chat_message():
    """Main conversational endpoint: processes queries via RAG, intent classification, and diagnostics."""
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    data = request.get_json() or {}
    try:
        req = ChatMessageRequest(**data)
        result = ChatService.send_message(
            message=req.message,
            user=g.current_user,
            session_id=req.session_id,
        )

        session_id = result.get("session_id") if isinstance(result, dict) else None
        content = result.get("content") if isinstance(result, dict) else str(result)
        metadata = result.get("metadata", {}) if isinstance(result, dict) else {}
        sources = metadata.get("sources", [])
        suggested_actions = metadata.get("suggested_prompts", [])
        ticket_draft = metadata.get("action_payload", {}).get("ticket_data") if metadata.get("action_payload") else None

        return jsonify({
            "success": True,
            "session_id": session_id,
            "response": content,
            "content": content,
            "sources": sources,
            "suggested_actions": suggested_actions,
            "ticket_draft": ticket_draft,
            "metadata": metadata,
            "data": result,
        })
    except Exception as e:
        logger.error(f"Error handling chat: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 400


@chat_bp.route("/api/chat/sessions", methods=["GET"])
@require_auth
def list_sessions():
    """Lists recent conversation sessions for the authenticated user."""
    try:
        sessions = ChatService.list_sessions(user=g.current_user)
        return jsonify({
            "success": True,
            "sessions": sessions,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@chat_bp.route("/api/chat/sessions", methods=["POST"])
@require_auth
def create_session():
    """Creates a new empty chat session."""
    data = request.get_json() or {}
    req = ChatSessionCreateRequest(**data)
    try:
        session = ChatService.create_session(user=g.current_user, title=req.title)
        return jsonify({
            "success": True,
            "session": session,
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@chat_bp.route("/api/chat/sessions/<session_id>/messages", methods=["GET"])
@require_auth
def get_session_messages(session_id: str):
    """Retrieves all message history for a given session."""
    try:
        messages = ChatService.get_session_messages(session_id, user=g.current_user)
        return jsonify({
            "success": True,
            "messages": messages,
        })
    except PermissionError as pe:
        return jsonify({"success": False, "error": str(pe)}), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
