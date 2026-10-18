import logging
from typing import Dict, Any, List
from ai.groq_client import groq_client
from utils.priority_matrix import calculate_priority, VALID_LEVELS
from models.schemas import TicketClassificationResponse

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {
    "Hardware",
    "Network",
    "Software",
    "Account and Access",
    "Email",
    "Security",
    "General IT",
}


class TicketClassifier:
    """
    Intelligent Ticket Intake Classifier using Groq GPT-OSS with strict schema validation
    and deterministic backend priority matrix enforcement.
    """

    SYSTEM_PROMPT = """You are an Enterprise ITSM Incident Intake & Triage Specialist.
Analyze the user's issue description and extract structured technical metadata for ticket creation.

You must respond ONLY with a JSON object adhering to this exact schema:
{
  "title": "A concise, professional ticket summary (under 80 characters)",
  "description": "Clear technical breakdown of the reported problem",
  "category": "Hardware | Network | Software | Account and Access | Email | Security | General IT",
  "ticket_type": "incident | service_request",
  "impact": "low | medium | high | critical",
  "urgency": "low | medium | high | critical",
  "suggested_priority": "low | medium | high | critical",
  "symptoms": ["list of explicit technical symptoms observed"],
  "affected_service": "name of software, protocol, or hardware affected or null",
  "suggested_troubleshooting_workflow": "Network Troubleshooting | Disk Space and Performance Guidance | Application Troubleshooting | Manual",
  "missing_information": ["any critical troubleshooting details not provided by user"],
  "suggested_resolution": "immediate recommendation or self-heal action if applicable",
  "ai_confidence": 0.85
}

Guidelines for Impact & Urgency:
- Impact: 'critical' if whole department or production down; 'high' if single user blocked on critical deadline; 'medium' if work impaired with workaround; 'low' for cosmetic/inconvenience.
- Urgency: 'critical' if immediate meeting/deadline in minutes; 'high' if needed within hours; 'medium' if today; 'low' if general inquiry.
"""

    @classmethod
    def classify_issue(cls, user_query: str) -> Dict[str, Any]:
        """
        Classifies user query into structured ticket metadata.
        Falls back to safe rule-based heuristic if Groq is unconfigured or fails.
        """
        clean_query = (user_query or "").strip()
        if len(clean_query) < 3:
            raise ValueError("Issue description too short.")

        if groq_client.is_configured():
            try:
                messages = [
                    {"role": "system", "content": cls.SYSTEM_PROMPT},
                    {"role": "user", "content": f"User Problem Description:\n{clean_query}"},
                ]
                raw_data = groq_client.chat_json(messages=messages, temperature=0.1)
                return cls._validate_and_normalize(raw_data, clean_query)
            except Exception as e:
                logger.warning(f"Groq classification failed, falling back to heuristic engine: {e}")

        # Deterministic heuristic fallback
        return cls._heuristic_classification(clean_query)

    @classmethod
    def _validate_and_normalize(cls, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validates AI extracted fields and applies deterministic priority matrix."""
        # Category validation
        category = data.get("category", "General IT")
        if category not in VALID_CATEGORIES:
            category = "General IT"

        # Type validation
        ticket_type = data.get("ticket_type", "incident")
        if ticket_type not in ["incident", "service_request"]:
            ticket_type = "incident"

        # Impact & Urgency validation
        impact = str(data.get("impact", "medium")).lower()
        if impact not in VALID_LEVELS:
            impact = "medium"

        urgency = str(data.get("urgency", "medium")).lower()
        if urgency not in VALID_LEVELS:
            urgency = "medium"

        # Deterministic Priority calculation
        calculated_priority = calculate_priority(impact, urgency)
        suggested_priority = str(data.get("suggested_priority", calculated_priority)).lower()
        if suggested_priority not in VALID_LEVELS:
            suggested_priority = calculated_priority

        title = str(data.get("title", "")).strip()
        if not title:
            title = query[:60] + "..." if len(query) > 60 else query

        description = str(data.get("description", "")).strip()
        if not description:
            description = query

        symptoms = data.get("symptoms", [])
        if not isinstance(symptoms, list):
            symptoms = [str(symptoms)]

        missing_info = data.get("missing_information", [])
        if not isinstance(missing_info, list):
            missing_info = []

        confidence = data.get("ai_confidence", 0.85)
        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.80

        workflow = data.get("suggested_troubleshooting_workflow")
        if workflow not in ["Network Troubleshooting", "Disk Space and Performance Guidance", "Application Troubleshooting", "Manual"]:
            workflow = "Manual"

        return {
            "title": title,
            "description": description,
            "category": category,
            "ticket_type": ticket_type,
            "impact": impact,
            "urgency": urgency,
            "suggested_priority": suggested_priority,
            "calculated_priority": calculated_priority,
            "symptoms": symptoms,
            "affected_service": data.get("affected_service"),
            "suggested_troubleshooting_workflow": workflow,
            "missing_information": missing_info,
            "suggested_resolution": data.get("suggested_resolution"),
            "ai_confidence": confidence,
        }

    @classmethod
    def _heuristic_classification(cls, query: str) -> Dict[str, Any]:
        """Reliable rule-based fallback when Groq is unavailable."""
        q_lower = query.lower()

        category = "General IT"
        workflow = "Manual"
        impact = "medium"
        urgency = "medium"

        if any(w in q_lower for w in ["wifi", "wi-fi", "internet", "vpn", "dns", "gateway", "connect", "network"]):
            category = "Network"
            workflow = "Network Troubleshooting"
        elif any(w in q_lower for w in ["laptop", "monitor", "keyboard", "battery", "mouse", "printer", "hardware"]):
            category = "Hardware"
        elif any(w in q_lower for w in ["disk", "space", "storage", "slow", "freeze", "cpu", "ram", "memory"]):
            category = "Hardware"
            workflow = "Disk Space and Performance Guidance"
        elif any(w in q_lower for w in ["crash", "app", "install", "teams", "excel", "software", "update"]):
            category = "Software"
            workflow = "Application Troubleshooting"
        elif any(w in q_lower for w in ["password", "login", "sso", "locked", "mfa", "2fa", "access", "account"]):
            category = "Account and Access"
        elif any(w in q_lower for w in ["outlook", "email", "mailbox", "sync", "mail"]):
            category = "Email"
        elif any(w in q_lower for w in ["phishing", "virus", "malware", "security", "compromised", "breach"]):
            category = "Security"
            impact = "high"
            urgency = "high"

        # Check for urgent signals
        if any(w in q_lower for w in ["urgent", "asap", "meeting", "immediately", "deadline", "production"]):
            urgency = "high"

        calculated_priority = calculate_priority(impact, urgency)

        return {
            "title": query[:60] + "..." if len(query) > 60 else query,
            "description": query,
            "category": category,
            "ticket_type": "incident",
            "impact": impact,
            "urgency": urgency,
            "suggested_priority": calculated_priority,
            "calculated_priority": calculated_priority,
            "symptoms": ["Reported issue by employee: " + query[:80]],
            "affected_service": category,
            "suggested_troubleshooting_workflow": workflow,
            "missing_information": [],
            "suggested_resolution": f"Run automated {workflow} workflow or review knowledge base.",
            "ai_confidence": 0.75,
        }
