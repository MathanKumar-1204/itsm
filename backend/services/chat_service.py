import logging
from typing import Dict, Any, List
from repositories.db_repository import db
from ai.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


class ChatService:
    @classmethod
    def create_session(cls, user: Dict[str, Any], title: str = "New Conversation") -> Dict[str, Any]:
        return db.create_chat_session(user_id=user["id"], title=title)

    @classmethod
    def list_sessions(cls, user: Dict[str, Any]) -> List[Dict[str, Any]]:
        return db.list_chat_sessions(user_id=user["id"])

    @classmethod
    def get_session_messages(cls, session_id: str, user: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Enforce that user owns session unless staff
        sessions = db.list_chat_sessions(user_id=user["id"])
        owned_ids = {s["id"] for s in sessions}
        if session_id not in owned_ids and user.get("role") not in ["it_agent", "admin"]:
            raise PermissionError("Access denied to this chat session.")

        return db.get_session_messages(session_id)

    @classmethod
    def send_message(cls, message: str, user: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        if not session_id:
            # Auto-create session if not provided
            preview = message[:30] + "..." if len(message) > 30 else message
            session = db.create_chat_session(user_id=user["id"], title=preview)
            session_id = session["id"]

        return AgentOrchestrator.handle_chat_message(
            session_id=session_id,
            message=message,
            user=user,
        )
