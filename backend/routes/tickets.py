import logging
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, require_role
from services.ticket_service import TicketService
from models.schemas import (
    TicketClassifyRequest,
    TicketCreateRequest,
    TicketUpdateRequest,
    TicketCommentCreateRequest,
    TicketResolveRequest,
)

logger = logging.getLogger(__name__)
tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/api/tickets/classify", methods=["POST"])
@require_auth
def classify_ticket():
    """Classifies user issue text into structured ITSM metadata."""
    data = request.get_json() or {}
    try:
        req = TicketClassifyRequest(**data)
        classification = TicketService.classify_problem(req.user_query)
        return jsonify({
            "success": True,
            "classification": classification,
        })
    except Exception as e:
        logger.error(f"Error classifying ticket: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@tickets_bp.route("/api/tickets", methods=["POST"])
@require_auth
def create_ticket():
    """Creates a new ticket in MongoDB Atlas and attempts ServiceNow incident sync."""
    data = request.get_json() or {}
    try:
        req = TicketCreateRequest(**data)
        ticket = TicketService.create_ticket(req.model_dump(), user=g.current_user)
        return jsonify({
            "success": True,
            "ticket": ticket,
        }), 201
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@tickets_bp.route("/api/tickets", methods=["GET"])
@require_auth
def list_tickets():
    """Lists tickets with filtering by status, category, priority, and search."""
    status = request.args.get("status")
    category = request.args.get("category")
    priority = request.args.get("priority")
    search = request.args.get("search")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    try:
        tickets = TicketService.list_tickets(
            user=g.current_user,
            status=status,
            category=category,
            priority=priority,
            search=search,
            limit=limit,
            offset=offset,
        )
        return jsonify({
            "success": True,
            "tickets": tickets,
            "count": len(tickets),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tickets_bp.route("/api/tickets/<ticket_id>", methods=["GET"])
@require_auth
def get_ticket(ticket_id: str):
    """Retrieves single ticket with authorization enforcement."""
    try:
        ticket = TicketService.get_ticket(ticket_id, user=g.current_user)
        return jsonify({
            "success": True,
            "ticket": ticket,
        })
    except PermissionError as pe:
        return jsonify({"success": False, "error": str(pe)}), 403
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tickets_bp.route("/api/tickets/<ticket_id>", methods=["PATCH"])
@require_auth
def update_ticket(ticket_id: str):
    """Updates ticket details with role enforcement."""
    data = request.get_json() or {}
    try:
        req = TicketUpdateRequest(**data)
        updates = req.model_dump(exclude_unset=True)
        updated = TicketService.update_ticket(ticket_id, updates, user=g.current_user)
        return jsonify({
            "success": True,
            "ticket": updated,
        })
    except PermissionError as pe:
        return jsonify({"success": False, "error": str(pe)}), 403
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@tickets_bp.route("/api/tickets/<ticket_id>/comments", methods=["POST"])
@require_auth
def add_ticket_comment(ticket_id: str):
    """Adds public or internal note to ticket."""
    data = request.get_json() or {}
    try:
        req = TicketCommentCreateRequest(**data)
        comment = TicketService.add_comment(
            ticket_id=ticket_id,
            comment_text=req.comment,
            visibility=req.visibility,
            user=g.current_user,
        )
        return jsonify({
            "success": True,
            "comment": comment,
        }), 201
    except PermissionError as pe:
        return jsonify({"success": False, "error": str(pe)}), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@tickets_bp.route("/api/tickets/<ticket_id>/resolve", methods=["POST"])
@require_role(["it_agent", "admin"])
def resolve_ticket(ticket_id: str):
    """Marks ticket resolved with confirmed resolution notes."""
    data = request.get_json() or {}
    try:
        req = TicketResolveRequest(**data)
        updated = TicketService.resolve_ticket(ticket_id, req.resolution, user=g.current_user)
        return jsonify({
            "success": True,
            "ticket": updated,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@tickets_bp.route("/api/tickets/<ticket_id>/sync-servicenow", methods=["POST"])
@require_role(["it_agent", "admin"])
def sync_servicenow(ticket_id: str):
    """Synchronizes ticket with ServiceNow incident record."""
    try:
        res = TicketService.sync_servicenow(ticket_id, user=g.current_user)
        return jsonify({
            "success": True,
            "result": res,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@tickets_bp.route("/api/tickets/sync-all", methods=["POST", "GET"])
@require_auth
def sync_all_tickets():
    """Forces synchronization of all tickets with ServiceNow."""
    try:
        tickets = TicketService.sync_all_tickets(user=g.current_user)
        return jsonify({
            "success": True,
            "tickets": tickets,
            "count": len(tickets),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
