import logging
import json
import re
from typing import Dict, Any, List, Optional
from ai.groq_client import groq_client
from ai.rag_pipeline import rag_pipeline
from ai.ticket_classifier import TicketClassifier
from repositories.db_repository import db
from services.ticket_service import TicketService
from services.software_service import SoftwareService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Multi-Intent Enterprise IT Helpdesk Chat Orchestrator.
    Routes queries to:
    - Ticket status lookups (internal numbers like INC-1005 & ServiceNow numbers like INC0010009)
    - In-chat IT Incident creation with ServiceNow synchronization
    - In-chat Software Request flow with AI Designation Governance evaluation
    - Grounded Knowledge Base RAG via Pinecone & GPT-OSS
    - Conversational general assistance & greetings
    - Self-healing diagnostics
    """

    INTENT_SYSTEM_PROMPT = """You are an Enterprise ITSM Intent Classifier.
Classify the user's message into EXACTLY ONE of these intents:
- "ticket_status": inquiring about existing tickets, ticket numbers (e.g. INC-1005, INC0010009), or tracking ticket progress
- "new_incident": wanting to report, create, or log an IT ticket or reporting a technical problem that needs a ticket
- "software_request": requesting access to or installation of software (e.g. VS Code, Docker, Python, Teams, Figma)
- "knowledge_question": asking how to do something, company policies, guides, procedures, VPN setup, password instructions
- "troubleshooting_request": reporting that something is broken, failing, disconnected, or crashing, and asking for diagnostic steps
- "general_assistance": greetings (hi, hello), general help, asking what the assistant can do, or casual conversation

Respond ONLY with JSON:
{
  "intent": "ticket_status | new_incident | software_request | knowledge_question | troubleshooting_request | general_assistance",
  "entities": {
    "ticket_number": "string or null",
    "software_name": "string or null",
    "issue_category": "string or null"
  }
}
"""

    @classmethod
    def classify_intent(cls, message: str) -> Dict[str, Any]:
        """Classifies intent using deterministic heuristics and Groq AI classifier."""
        clean_msg = message.strip().lower()

        # 1. Regex check for Ticket Number (matches internal e.g. INC-1005, SR-5001 OR ServiceNow e.g. INC0010009)
        m_ticket = re.search(r"(inc-?\d+|sr-?\d+)", clean_msg, re.IGNORECASE)
        t_num = m_ticket.group(1).upper() if m_ticket else None

        if t_num or any(w in clean_msg for w in ["status of", "my ticket", "check ticket", "track ticket", "ticket status", "how is my incident"]):
            return {"intent": "ticket_status", "entities": {"ticket_number": t_num}}

        # 2. Check for Greetings / General Conversational Help
        if clean_msg in ["hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup"] or \
           any(clean_msg.startswith(w) for w in ["hi ", "hello ", "hey "]):
            return {"intent": "general_assistance", "entities": {}}
        if any(phrase in clean_msg for phrase in ["who are you", "what can you do", "help me", "what is this", "thank you", "thanks"]):
            return {"intent": "general_assistance", "entities": {}}

        # 3. Check if query is an Informational / Policy / Guide / How-to question
        is_informational_question = any(
            clean_msg.startswith(w) for w in ["what", "how", "why", "where", "can you explain", "tell me", "explain", "describe", "is there", "which"]
        ) or any(
            w in clean_msg for w in ["procedure", "policy", "policies", "guide", "documentation", "steps", "instructions", "manual", "handbook", "overview"]
        )

        # 4. Check for explicit Ticket Creation Intent
        is_ticket_creation = any(
            phrase in clean_msg for phrase in [
                "create a ticket", "create ticket", "submit ticket", "submit a ticket",
                "log a ticket", "log an incident", "open a ticket", "file a ticket",
                "raise a ticket", "report an issue", "report issue", "confirm ticket",
                "log ticket", "make a ticket"
            ]
        )
        if is_ticket_creation:
            return {"intent": "new_incident", "entities": {}}

        # 5. Check for Software Provisioning Intent (ONLY if NOT an informational inquiry)
        sw_catalog = db.list_software_catalog(enabled_only=True)
        detected_sw = None
        for item in sw_catalog:
            item_name = item.get("name", "").lower()
            if item_name in clean_msg or (item_name == "visual studio code" and any(k in clean_msg for k in ["vs code", "vscode"])):
                detected_sw = item.get("name")
                break

        if not is_informational_question:
            if detected_sw or any(
                w in clean_msg for w in [
                    "request access to", "request software", "request license",
                    "need software", "install software", "software request",
                    "i need vs code", "i need python", "i need docker",
                    "can i have access to", "order software", "provision software"
                ]
            ):
                return {"intent": "software_request", "entities": {"software_name": detected_sw}}

        # 6. Groq AI Intent Classification
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
                if intent in ["ticket_status", "new_incident", "software_request", "knowledge_question", "troubleshooting_request", "general_assistance"]:
                    return res
            except Exception as e:
                logger.warning(f"Groq intent classification failed: {e}")

        # 7. Fallback Heuristics
        if is_informational_question or any(w in clean_msg for w in ["how to", "how do i", "policy", "where can i", "guide", "documentation"]):
            return {"intent": "knowledge_question", "entities": {}}
        if any(w in clean_msg for w in ["slow", "down", "not working", "crash", "error", "disconnected", "cannot", "broken", "failing"]):
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
        user_name = user.get("full_name") or user.get("email", "Employee")
        user_dept = user.get("department", "General")
        user_desig = user.get("designation") or ("Software Engineer" if "engin" in user_dept.lower() else "Employee")

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

        # ==================== ROUTE 1: TICKET STATUS REQUEST ====================
        if intent == "ticket_status":
            m = re.search(r"(inc-?\d+|sr-?\d+)", message, re.IGNORECASE)
            ticket_number = entities.get("ticket_number") or (m.group(1).upper() if m else None)

            if ticket_number:
                # Query ticket matching either internal number OR external ServiceNow reference
                all_tickets = db.list_tickets(limit=100)
                matched = [
                    t for t in all_tickets
                    if t.get("ticket_number", "").upper() == ticket_number.upper()
                    or (t.get("external_record_id") and t.get("external_record_id", "").upper() == ticket_number.upper())
                ]

                if matched:
                    ticket = matched[0]
                    # Attempt live ServiceNow status sync for up-to-the-second accuracy
                    if ticket.get("external_record_id"):
                        try:
                            # Use system context for read-only sync
                            sync_res = TicketService.sync_servicenow(ticket["id"], user={"id": user_id, "role": "admin"})
                            refreshed = db.get_ticket(ticket["id"])
                            if refreshed:
                                ticket = refreshed
                        except Exception as e:
                            logger.warning(f"Chat status sync error: {e}")

                        state_display = ticket.get("state") or (ticket.get("status", "New").replace("_", " ").title())
                        ext_ref = ticket.get("external_record_id") or "Local Only"
                        ext_url = ticket.get("external_record_url")

                        ref_link = f"[{ext_ref}]({ext_url})" if ext_url else ext_ref

                        response_text = (
                            f"### 📋 Ticket Status: {ticket.get('ticket_number')}\n\n"
                            f"- **State**: `{state_display.upper()}`\n"
                            f"- **Title**: **{ticket.get('title')}**\n"
                            f"- **Category**: {ticket.get('category')}\n"
                            f"- **Priority**: `{ticket.get('priority', 'medium').upper()}`\n"
                            f"- **ServiceNow Ref**: {ref_link}\n"
                            f"- **Requester**: {ticket.get('requester_name', user_name)}\n"
                        )
                        if ticket.get("resolution"):
                            response_text += f"\n- **Resolution Notes**: {ticket.get('resolution')}\n"

                        if state_display.lower() == "resolved":
                            response_text += "\n*This incident has been marked Resolved in ServiceNow.*"

                        action_payload = {"type": "ticket_view", "ticket": ticket}
                        suggested_prompts = ["Check other tickets", "Report a new issue", "Search Knowledge Base"]
                else:
                    response_text = (
                        f"I could not locate an active incident record matching **{ticket_number}**.\n\n"
                        "Please verify the ticket number (e.g. `INC-1005` or ServiceNow reference `INC0010009`), "
                        "or check your ticket list below."
                    )
                    user_tickets = db.list_tickets(requester_id=user_id if user_role == "employee" else None, limit=5)
                    if user_tickets:
                        action_payload = {"type": "ticket_list", "tickets": user_tickets}
                    suggested_prompts = ["Show all my tickets", "Report a new issue"]
            else:
                # Show user's active tickets with live states
                user_tickets = TicketService.list_tickets(user=user, limit=5)
                if user_tickets:
                    lines = [
                        f"- **{t['ticket_number']}**: {t['title']} (State: `{t.get('state', t.get('status', 'New')).upper()}`, SN: `{t.get('external_record_id') or 'Local'}`)"
                        for t in user_tickets
                    ]
                    response_text = "### 📂 Your Recent IT Support Tickets:\n\n" + "\n".join(lines) + "\n\nAsk about any ticket number (e.g. *\"Status of INC-1005\"*) for full details."
                    action_payload = {"type": "ticket_list", "tickets": user_tickets}
                else:
                    response_text = "You do not have any open tickets currently on file. Would you like to create one?"
                suggested_prompts = ["Report a new issue", "Request software", "How do I troubleshoot VPN?"]

        # ==================== ROUTE 2: SOFTWARE REQUEST ====================
        elif intent == "software_request":
            catalog = db.list_software_catalog(enabled_only=True)
            requested_sw_name = entities.get("software_name")

            # Try to match specific software from catalog
            matched_sw = None
            if requested_sw_name:
                matched_sw = next((s for s in catalog if s["name"].lower() == requested_sw_name.lower()), None)

            if not matched_sw:
                clean_msg = message.lower()
                for item in catalog:
                    n = item["name"].lower()
                    if n in clean_msg or (n == "visual studio code" and any(k in clean_msg for k in ["vs code", "vscode"])):
                        matched_sw = item
                        break

            if matched_sw:
                # Submit real Software Request in the workflow with AI designation evaluation
                try:
                    justification = f"Requested via AI Helpdesk Chat: '{message}'"
                    req = SoftwareService.create_request(
                        software_id=matched_sw["id"],
                        justification=justification,
                        user=user,
                        designation=user_desig,
                    )

                    is_auto = req.get("status") == "approved" or req.get("ai_recommendation") == "auto_approved"
                    eval_msg = req.get("ai_evaluation", "Evaluated by AI Governance System.")
                    badge = "⚡ AUTO-APPROVED" if is_auto else "⏳ PENDING MANAGER REVIEW"

                    response_text = (
                        f"### ✓ Software Request Submitted: **{matched_sw['name']}**\n\n"
                        f"- **Request Number**: `{req.get('request_number', 'SR-5000')}`\n"
                        f"- **Category**: {matched_sw.get('category', 'Productivity')}\n"
                        f"- **Requester Designation**: **{req.get('designation', user_desig)}** ({user_dept})\n"
                        f"- **AI Governance Decision**: **{badge}**\n"
                        f"- **AI Rationale**: *\"{eval_msg}\"*\n"
                        f"- **Current State**: `{req.get('status', 'submitted').upper()}` (Deployment: `{req.get('provisioning_status', 'pending').upper()}`)\n\n"
                        "This request has been registered in the system. You can view its progress under the **Software Requests** tab."
                    )
                    action_payload = {
                        "type": "software_request_confirmed",
                        "request": req,
                        "software": matched_sw,
                    }
                    suggested_prompts = ["View all software requests", "Request another tool", "Check ticket status"]
                except Exception as e:
                    logger.error(f"Error creating software request via chat: {e}")
                    response_text = f"I identified **{matched_sw['name']}**, but encountered an error submitting the request: {str(e)}."
            else:
                # Software not specifically identified: show catalog options
                sw_list = [f"- **{s['name']}** ({s['category']})" for s in catalog[:6]]
                response_text = (
                    "### 💻 Enterprise Software Catalogue\n\n"
                    "I can submit a software provisioning request for you. Available software in our catalogue:\n\n"
                    + "\n".join(sw_list) + "\n\n"
                    f"As a **{user_desig}** in **{user_dept}**, our AI Governance engine automatically checks license entitlement and auto-approves role-aligned tools.\n\n"
                    "Tell me which software you would like to request (e.g. *\"Request Visual Studio Code\"* or *\"Install Docker\"*)."
                )
                action_payload = {"type": "software_provisioning_prompt", "catalog": catalog[:4]}
                suggested_prompts = [f"Request {s['name']}" for s in catalog[:3]]

        # ==================== ROUTE 3: NEW INCIDENT / TICKET CREATION ====================
        elif intent == "new_incident":
            ticket_info = TicketClassifier.classify_issue(message)
            clean_msg = message.lower()

            # Check if user explicitly asked to create / submit / log the ticket right now
            should_create_now = any(
                phrase in clean_msg for phrase in [
                    "create a ticket", "create ticket", "submit ticket", "submit a ticket",
                    "log a ticket", "log ticket", "open a ticket", "file a ticket",
                    "raise a ticket", "confirm ticket", "yes, create", "create it"
                ]
            )

            if should_create_now:
                try:
                    payload = {
                        "title": ticket_info.get("title"),
                        "description": ticket_info.get("description", message),
                        "category": ticket_info.get("category", "General IT"),
                        "impact": ticket_info.get("impact", "medium"),
                        "urgency": ticket_info.get("urgency", "medium"),
                        "priority": ticket_info.get("calculated_priority", "medium"),
                        "ticket_type": "incident",
                        "source": "ai_chat",
                    }
                    new_ticket = TicketService.create_ticket(payload, user=user)
                    sn_ref = new_ticket.get("external_record_id")
                    sn_text = f" (ServiceNow: `{sn_ref}`)" if sn_ref else ""

                    response_text = (
                        f"### ✓ Incident Ticket Created Successfully!\n\n"
                        f"- **Ticket Number**: `{new_ticket.get('ticket_number')}`{sn_text}\n"
                        f"- **Title**: **{new_ticket.get('title')}**\n"
                        f"- **Category**: {new_ticket.get('category')}\n"
                        f"- **Calculated Priority**: `{new_ticket.get('priority', 'medium').upper()}`\n"
                        f"- **State**: `NEW`\n"
                        f"- **Requester**: {user_name}\n\n"
                        "Our IT Operations team has been notified. You can track this ticket anytime by asking "
                        f"*\"Status of {new_ticket.get('ticket_number')}\"* or viewing **My Tickets**."
                    )
                    action_payload = {"type": "ticket_created", "ticket": new_ticket}
                    suggested_prompts = [f"Status of {new_ticket.get('ticket_number')}", "Run Self-Heal Diagnostics", "Search Knowledge Base"]
                except Exception as e:
                    logger.error(f"Error creating ticket in chat: {e}")
                    response_text = f"I prepared your incident ticket, but encountered an error saving: {e}."
            else:
                # Offer ticket intake preview with 1-click confirmation
                response_text = (
                    f"### 🎫 Proposed IT Incident Ticket:\n\n"
                    f"- **Title**: {ticket_info.get('title')}\n"
                    f"- **Category**: {ticket_info.get('category')}\n"
                    f"- **Calculated Priority**: `{ticket_info.get('calculated_priority', 'medium').upper()}` (Impact: {ticket_info.get('impact')}, Urgency: {ticket_info.get('urgency')})\n\n"
                    f"**Summary**: {ticket_info.get('description')}\n\n"
                    "Would you like me to submit this ticket now, or try troubleshooting first?"
                )
                action_payload = {
                    "type": "ticket_intake_preview",
                    "ticket_data": ticket_info,
                }
                suggested_prompts = ["Create Ticket", "Run Diagnostics First", "Edit Description"]

        # ==================== ROUTE 4: GENERAL ASSISTANCE & GREETINGS ====================
        elif intent == "general_assistance":
            response_text = (
                f"Hello {user_name.split()[0]}! 👋 I am your **ITSM AI Helpdesk Assistant**.\n\n"
                "I am integrated with your enterprise IT systems, ServiceNow, and the Internal Knowledge Base. Here is what I can help you with:\n\n"
                "- 📋 **Check Ticket Status**: Ask *\"Status of INC-1005\"* or *\"Check INC0010009\"*\n"
                "- 🎫 **Create IT Tickets**: Say *\"Create a ticket for my flickering monitor\"*\n"
                "- 💻 **Request Software**: Ask *\"I need Visual Studio Code\"* or *\"Install Docker\"* (with automated AI designation governance)\n"
                "- 📖 **Search Knowledge Base**: Ask verified procedures like *\"How do I troubleshoot VPN connection issues?\"*\n"
                "- 🛠️ **Self-Healing Diagnostics**: Test network latency and system connectivity\n\n"
                "What can I help you with today?"
            )
            suggested_prompts = ["Check my tickets", "How do I troubleshoot VPN?", "Request VS Code", "Create IT Ticket"]

        # ==================== ROUTE 5: TROUBLESHOOTING REQUEST ====================
        elif intent == "troubleshooting_request":
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
            suggested_prompts = [f"Run {wf_name}", "Create Ticket", "Search Knowledge Base"]

        # ==================== ROUTE 6: KNOWLEDGE QUESTION (RAG) ====================
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
                suggested_prompts = ["Create Ticket", "Check ticket status", "Request software"]
            else:
                suggested_prompts = ["How do I connect to VPN?", "What are software installation procedures?", "Check my tickets"]

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
