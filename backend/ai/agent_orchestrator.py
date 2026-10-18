import logging
import json
from typing import Dict, Any, List, Optional
from ai.groq_client import groq_client
from ai.rag_pipeline import rag_pipeline
from ai.ticket_classifier import TicketClassifier
from repositories.db_repository import db

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Multi-Intent Enterprise IT Helpdesk Chat Orchestrator.
    Routes queries to RAG, Self-Healing, Ticket Intake, Ticket Status lookups, or Software Provisioning.
    """

    INTENT_SYSTEM_PROMPT = """You are an Enterprise ITSM Intent Classifier.
Classify the user's message into EXACTLY ONE of these intents:
- "knowledge_question": asking how to do something, company policies, guides, VPN, setup, configuration
- "troubleshooting_request": reporting that something is broken, slow, failing, disconnected, or crashing, and needing immediate diagnostic help
- "new_incident": wanting to report or create an IT ticket for a problem
- "ticket_status": inquiring about existing tickets or ticket numbers (e.g. INC-1001)
- "software_request": requesting access or installation of software (e.g. VS Code, Docker, Python)
- "general_assistance": greeting or general conversational help

Respond ONLY with JSON:
{
  "intent": "knowledge_question | troubleshooting_request | new_incident | ticket_status | software_request | general_assistance",
  "entities": {
    "ticket_number": "string or null",
    "software_name": "string or null",
    "issue_category": "string or null"
  }
}
"""

    @classmethod
    def classify_intent(cls, message: str) -> Dict[str, Any]:
        """Classifies intent using Groq or deterministic heuristics."""
        clean_msg = message.strip().lower()

        # Check if query is an informational / procedure / guide / how-to question
        is_informational_question = any(
            clean_msg.startswith(w) for w in ["what", "how", "why", "where", "can you", "tell me", "explain", "describe", "is there", "which"]
        ) or any(
            w in clean_msg for w in ["procedure", "policy", "policies", "guide", "documentation", "steps", "instructions", "manual", "handbook", "overview"]
        )

        # 1. Heuristic: Ticket Status Lookups
        if any(w in clean_msg for w in ["status of", "my ticket", "check ticket"]) or ("inc-" in clean_msg or "sr-" in clean_msg):
            import re
            m = re.search(r"(inc-\d+|sr-\d+)", clean_msg, re.IGNORECASE)
            t_num = m.group(1).upper() if m else None
            return {"intent": "ticket_status", "entities": {"ticket_number": t_num}}

        # 2. Heuristic: Software Provisioning Request (ONLY if NOT an informational inquiry)
        if not is_informational_question and any(
            w in clean_msg for w in [
                "request access to", "request software", "request license", 
                "request vs code", "request python", "request docker", 
                "need a license for", "order software", "provision software"
            ]
        ):
            return {"intent": "software_request", "entities": {}}

        # 3. AI-Powered Intent Classification via Groq
        if groq_client.is_configured():
            try:
                res = groq_client.chat_json(
                    messages=[
                        {"role": "system", "content": cls.INTENT_SYSTEM_PROMPT},
                        {"role": "user", "content": message},
                    ],
                    temperature=0.0,
                )
                intent = res.get("intent", "knowledge_question")
                if intent in ["knowledge_question", "troubleshooting_request", "new_incident", "ticket_status", "software_request", "general_assistance"]:
                    return res
            except Exception as e:
                logger.warning(f"Groq intent classification failed: {e}")

        # 4. Fallback heuristics
        if is_informational_question or any(w in clean_msg for w in ["how to", "how do i", "policy", "where can i", "guide", "documentation"]):
            return {"intent": "knowledge_question", "entities": {}}
        if any(w in clean_msg for w in ["slow", "down", "not working", "crash", "error", "disconnected", "cannot"]):
            return {"intent": "troubleshooting_request", "entities": {}}

        return {"intent": "knowledge_question", "entities": {}}

    @classmethod
    def handle_chat_message(cls, session_id: str, message: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a chat message within a session, returning assistant response, source citations,
        and actionable cards (e.g., ticket preview, diagnostics launcher, software link).
        """
        user_id = user.get("id")
        user_role = user.get("role", "employee")

        # 1. Save user message to database
        db.add_chat_message(session_id=session_id, role="user", content=message)

        # 2. Classify intent
        intent_data = cls.classify_intent(message)
        intent = intent_data.get("intent", "knowledge_question")
        entities = intent_data.get("entities", {})

        response_text = ""
        sources = []
        action_payload = None
        suggested_prompts = []

        # Route 1: Ticket Status Request
        if intent == "ticket_status":
            ticket_number = entities.get("ticket_number")
            if ticket_number:
                # Query ticket directly
                all_tickets = db.list_tickets(limit=100)
                matched = [t for t in all_tickets if t.get("ticket_number", "").upper() == ticket_number.upper()]
                if matched:
                    ticket = matched[0]
                    # Verify authorization
                    if user_role not in ["it_agent", "admin"] and ticket.get("requester_id") != user_id:
                        response_text = f"You are not authorized to view the details for ticket **{ticket_number}**."
                    else:
                        response_text = (
                            f"### Ticket Status: {ticket.get('ticket_number')}\n\n"
                            f"- **Title**: {ticket.get('title')}\n"
                            f"- **Status**: `{ticket.get('status').upper()}`\n"
                            f"- **Priority**: `{ticket.get('priority').upper()}`\n"
                            f"- **Category**: {ticket.get('category')}\n"
                            f"- **External Reference**: {ticket.get('external_record_id') or 'Local Only'}\n\n"
                            f"{'**Resolution Notes**: ' + ticket.get('resolution') if ticket.get('resolution') else ''}"
                        )
                        action_payload = {"type": "ticket_view", "ticket": ticket}
                else:
                    response_text = f"I could not find an active ticket with number **{ticket_number}** in the system."
            else:
                # Show list of user's active tickets
                user_tickets = db.list_tickets(requester_id=user_id, limit=5)
                if user_tickets:
                    lines = [f"- **{t['ticket_number']}**: {t['title']} (`{t['status']}`, Priority: `{t['priority']}`)" for t in user_tickets]
                    response_text = "Here are your recent tickets:\n\n" + "\n".join(lines)
                else:
                    response_text = "You do not have any open tickets currently on file."
            suggested_prompts = ["Report a new issue", "Request software", "Search knowledge base"]

        # Route 2: Software Request
        elif intent == "software_request":
            catalog = db.list_software_catalog(enabled_only=True)
            sw_names = [s["name"] for s in catalog]
            response_text = (
                "You can request approved enterprise software directly through our self-service portal.\n\n"
                f"**Available in Catalogue**: {', '.join(sw_names)}.\n\n"
                "Click below to browse or submit a formal software provisioning request."
            )
            action_payload = {"type": "software_provisioning_prompt", "catalog": catalog[:4]}
            suggested_prompts = ["Request Visual Studio Code", "Request Python 3.12", "Request Microsoft Teams"]

        # Route 3: Troubleshooting Request
        elif intent == "troubleshooting_request":
            # Run classification to find appropriate workflow
            ticket_info = TicketClassifier.classify_issue(message)
            wf_name = ticket_info.get("suggested_troubleshooting_workflow", "Network Troubleshooting")
            if wf_name == "Manual":
                wf_name = "Network Troubleshooting"

            response_text = (
                f"I detected an issue related to **{ticket_info.get('category')}**: *\"{ticket_info.get('title')}\"*.\n\n"
                f"I have initialized the automated **{wf_name}** workflow to diagnose this safely. "
                "Would you like to run the diagnostic checks now, or proceed straight to creating an IT support ticket?"
            )
            action_payload = {
                "type": "diagnostic_workflow",
                "workflow_name": wf_name,
                "ticket_preview": ticket_info,
            }
            suggested_prompts = [f"Run {wf_name}", "Create IT Ticket", "Search Knowledge Base"]

        # Route 4: New Incident / Ticket Intake
        elif intent == "new_incident":
            ticket_info = TicketClassifier.classify_issue(message)
            response_text = (
                f"I have prepared an IT incident ticket for you:\n\n"
                f"- **Title**: {ticket_info.get('title')}\n"
                f"- **Category**: {ticket_info.get('category')}\n"
                f"- **Calculated Priority**: `{ticket_info.get('calculated_priority').upper()}` (Impact: {ticket_info.get('impact')}, Urgency: {ticket_info.get('urgency')})\n\n"
                "Please review or edit the details in the form below before submitting."
            )
            action_payload = {
                "type": "ticket_intake_preview",
                "ticket_data": ticket_info,
            }
            suggested_prompts = ["Confirm Ticket", "Edit Description", "Run Diagnostics First"]

        # Route 5: Knowledge Question (RAG)
        else:
            rag_result = rag_pipeline.answer_with_rag(query=message, user_role=user_role)
            response_text = rag_result["answer"]
            sources = rag_result.get("sources", [])
            if not rag_result.get("has_grounded_context"):
                # Offer ticket escalation
                ticket_info = TicketClassifier.classify_issue(message)
                action_payload = {
                    "type": "ticket_intake_preview",
                    "ticket_data": ticket_info,
                }
            suggested_prompts = ["How do I connect to VPN?", "My laptop is running slowly", "Request software"]

        # 3. Save assistant message with metadata
        metadata = {
            "intent": intent,
            "sources": sources,
            "action_payload": action_payload,
            "suggested_prompts": suggested_prompts,
        }
        db.add_chat_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            metadata=metadata,
        )

        return {
            "session_id": session_id,
            "role": "assistant",
            "content": response_text,
            "metadata": metadata,
        }
