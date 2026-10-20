import logging
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, require_role
from services.software_service import SoftwareService
from models.schemas import SoftwareRequestCreate, SoftwareRequestApprove, SoftwareRequestEvaluate

logger = logging.getLogger(__name__)
software_bp = Blueprint("software", __name__)


@software_bp.route("/api/software/catalog", methods=["GET"])
@require_auth
def get_catalog():
    """Lists approved enterprise software products."""
    items = SoftwareService.list_catalog(enabled_only=True)
    return jsonify({
        "success": True,
        "catalog": items,
    })


@software_bp.route("/api/software/evaluate", methods=["POST"])
@require_auth
def evaluate_request():
    """Pre-evaluates a software request based on employee designation."""
    data = request.get_json() or {}
    try:
        req = SoftwareRequestEvaluate(**data)
        eval_result = SoftwareService.evaluate_request(
            software_id=req.software_id,
            user=g.current_user,
            justification=req.business_justification or "",
            designation=req.designation or request.headers.get("X-Employee-Designation") or g.current_user.get("designation")
        )
        return jsonify({
            "success": True,
            "evaluation": eval_result,
        })
    except Exception as e:
        logger.error(f"Error evaluating software request: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@software_bp.route("/api/software/requests", methods=["POST"])
@require_auth
def create_request():
    """Submits a software provisioning request with AI designation governance."""
    data = request.get_json() or {}
    try:
        req = SoftwareRequestCreate(**data)
        eff_designation = req.designation or request.headers.get("X-Employee-Designation") or g.current_user.get("designation")
        saved = SoftwareService.create_request(
            software_id=req.software_id,
            justification=req.business_justification,
            user=g.current_user,
            designation=eff_designation,
        )
        return jsonify({
            "success": True,
            "request": saved,
        }), 201
    except Exception as e:
        logger.error(f"Error submitting software request: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@software_bp.route("/api/software/requests", methods=["GET"])
@require_auth
def list_requests():
    """Returns requests for current employee or all requests for staff."""
    requests_list = SoftwareService.list_requests(user=g.current_user)
    return jsonify({
        "success": True,
        "requests": requests_list,
    })


@software_bp.route("/api/software/requests/<request_id>", methods=["GET"])
@require_auth
def get_request(request_id: str):
    try:
        req = SoftwareService.get_request(request_id, user=g.current_user)
        return jsonify({
            "success": True,
            "request": req,
        })
    except PermissionError as pe:
        return jsonify({"success": False, "error": str(pe)}), 403
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404


@software_bp.route("/api/software/requests/<request_id>/approve", methods=["POST"])
@require_role(["it_agent", "admin"])
def approve_request(request_id: str):
    data = request.get_json() or {}
    comment = data.get("comment")
    try:
        updated = SoftwareService.approve_request(request_id, comment=comment, user=g.current_user)
        return jsonify({
            "success": True,
            "request": updated,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@software_bp.route("/api/software/requests/<request_id>/reject", methods=["POST"])
@require_role(["it_agent", "admin"])
def reject_request(request_id: str):
    data = request.get_json() or {}
    comment = data.get("comment")
    try:
        updated = SoftwareService.reject_request(request_id, comment=comment, user=g.current_user)
        return jsonify({
            "success": True,
            "request": updated,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@software_bp.route("/api/software/requests/<request_id>/execute", methods=["POST"])
@require_role(["it_agent", "admin"])
def execute_provisioning(request_id: str):
    try:
        updated = SoftwareService.execute_provisioning(request_id, user=g.current_user)
        return jsonify({
            "success": True,
            "request": updated,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
