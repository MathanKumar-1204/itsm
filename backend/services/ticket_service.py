import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from repositories.db_repository import db
from integrations.servicenow import servicenow_client
from utils.priority_matrix import calculate_priority
from ai.ticket_classifier import TicketClassifier

logger = logging.getLogger(__name__)


class TicketService:
    @classmethod
    def classify_problem(cls, user_query: str) -> Dict[str, Any]:
        return TicketClassifier.classify_issue(user_query)

    @classmethod
    def create_ticket(cls, data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        requester_id = user["id"]
        impact = data.get("impact", "medium")
        urgency = data.get("urgency", "medium")
        priority = calculate_priority(impact, urgency)

        record_data = {
            "requester_id": requester_id,
            "title": data["title"],
            "description": data["description"],
            "category": data["category"],
            "ticket_type": data.get("ticket_type", "incident"),
            "impact": impact,
            "urgency": urgency,
            "priority": priority,
            "status": "new",
            "source": data.get("source", "portal"),
            "ai_summary": data.get("ai_summary"),
            "ai_confidence": data.get("ai_confidence"),
        }

        # 1. Save ticket in database
        ticket = db.create_ticket(record_data)
        ticket_id = ticket["id"]

        # 2. Attempt ServiceNow incident creation
        try:
            sn_res = servicenow_client.create_incident(ticket)
            if sn_res.get("success"):
                updates = {
                    "external_system": sn_res.get("external_system"),
                    "external_record_id": sn_res.get("external_record_id"),
                    "external_record_url": sn_res.get("external_record_url"),
                    "last_synced_at": datetime.now(timezone.utc).isoformat(),
                }
                ticket = db.update_ticket(ticket_id, updates)
            else:
                ticket = db.update_ticket(ticket_id, {
                    "external_system": "ServiceNow (Sync Failed)",
                    "external_record_id": None,
                })
        except Exception as e:
            logger.error(f"ServiceNow sync error during ticket creation: {e}")
            # Internal ticket is preserved!

        # 3. Audit log
        db.log_audit(
            actor_id=requester_id,
            action="create_ticket",
            entity_type="ticket",
            entity_id=ticket_id,
            metadata={"ticket_number": ticket.get("ticket_number"), "priority": priority},
        )

        return ticket

    @classmethod
    def list_tickets(cls, user: Dict[str, Any], **filters) -> List[Dict[str, Any]]:
        user_role = user.get("role", "employee")
        user_id = user.get("id")

        if user_role == "employee":
            filters["requester_id"] = user_id

        return db.list_tickets(**filters)

    @classmethod
    def get_ticket(cls, ticket_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found.")

        user_role = user.get("role", "employee")
        user_id = user.get("id")
        if user_role == "employee" and ticket.get("requester_id") != user_id:
            raise PermissionError("Access denied to this ticket.")

        comments = db.list_ticket_comments(ticket_id, include_internal=(user_role in ["it_agent", "admin"]))
        return {**ticket, "comments": comments}

    @classmethod
    def update_ticket(cls, ticket_id: str, updates: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found.")

        user_role = user.get("role", "employee")
        user_id = user.get("id")

        # Employees may only update their own ticket's description/title if still in 'new' status
        if user_role == "employee":
            if ticket.get("requester_id") != user_id:
                raise PermissionError("Access denied.")
            allowed_updates = {}
            if "title" in updates:
                allowed_updates["title"] = updates["title"]
            if "description" in updates:
                allowed_updates["description"] = updates["description"]
            updates = allowed_updates

        # If impact or urgency updated by staff, recalculate priority
        if "impact" in updates or "urgency" in updates:
            new_impact = updates.get("impact", ticket.get("impact"))
            new_urgency = updates.get("urgency", ticket.get("urgency"))
            updates["priority"] = calculate_priority(new_impact, new_urgency)

        updated_ticket = db.update_ticket(ticket_id, updates)

        db.log_audit(
            actor_id=user_id,
            action="update_ticket",
            entity_type="ticket",
            entity_id=ticket_id,
            metadata={"updated_fields": list(updates.keys())},
        )
        return updated_ticket

    @classmethod
    def add_comment(cls, ticket_id: str, comment_text: str, visibility: str, user: Dict[str, Any]) -> Dict[str, Any]:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found.")

        user_role = user.get("role", "employee")
        user_id = user.get("id")

        if user_role == "employee":
            if ticket.get("requester_id") != user_id:
                raise PermissionError("Access denied.")
            visibility = "public" # Employees cannot make internal IT comments

        comment_data = {
            "ticket_id": ticket_id,
            "author_id": user_id,
            "comment": comment_text,
            "visibility": visibility,
        }
        record = db.add_ticket_comment(comment_data)
        return record

    @classmethod
    def resolve_ticket(cls, ticket_id: str, resolution: str, user: Dict[str, Any]) -> Dict[str, Any]:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found.")

        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff can mark a ticket resolved.")

        now = datetime.now(timezone.utc).isoformat()
        updates = {
            "status": "resolved",
            "resolution": resolution,
            "resolved_at": now,
        }
        updated = db.update_ticket(ticket_id, updates)

        db.log_audit(
            actor_id=user.get("id"),
            action="resolve_ticket",
            entity_type="ticket",
            entity_id=ticket_id,
            metadata={"resolution": resolution},
        )
        return updated

    @classmethod
    def sync_servicenow(cls, ticket_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found.")

        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Staff role required for external synchronization.")

        ext_id = ticket.get("external_record_id")
        if not ext_id:
            # Attempt creating if missing
            res = servicenow_client.create_incident(ticket)
            if res.get("success"):
                db.update_ticket(ticket_id, {
                    "external_system": res.get("external_system"),
                    "external_record_id": res.get("external_record_id"),
                    "external_record_url": res.get("external_record_url"),
                    "last_synced_at": datetime.now(timezone.utc).isoformat(),
                })
            return res

        sync_res = servicenow_client.sync_incident_status(ext_id)
        if sync_res.get("success") and "mapped_internal_status" in sync_res:
            db.update_ticket(ticket_id, {
                "status": sync_res["mapped_internal_status"],
                "last_synced_at": datetime.now(timezone.utc).isoformat(),
            })
        return sync_res
