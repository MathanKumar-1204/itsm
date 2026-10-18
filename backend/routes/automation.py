import logging
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from services.automation_service import AutomationService
from models.schemas import AutomationRunRequest, AutomationVerifyRequest

logger = logging.getLogger(__name__)
automation_bp = Blueprint("automation", __name__)


@automation_bp.route("/api/automation/workflows", methods=["GET"])
@require_auth
def list_workflows():
    """Lists available self-healing diagnostic workflows."""
    workflows = AutomationService.list_workflows()
    return jsonify({
        "success": True,
        "workflows": workflows,
    })


@automation_bp.route("/api/automation/run", methods=["POST"])
@require_auth
def run_workflow():
    """Executes a diagnostic workflow (Network, Disk Space, or Application)."""
    data = request.get_json() or {}
    try:
        req = AutomationRunRequest(**data)
        run = AutomationService.run_workflow(
            workflow_name=req.workflow_name,
            issue_description=req.issue_description,
            user=g.current_user,
            ticket_id=req.ticket_id,
            step_inputs=req.step_inputs,
        )
        return jsonify({
            "success": True,
            "run": run,
        }), 201
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@automation_bp.route("/api/automation/runs", methods=["GET"])
@require_auth
def list_runs():
    """Returns past automation runs for user or IT staff."""
    limit = int(request.args.get("limit", 50))
    runs = AutomationService.list_runs(user=g.current_user, limit=limit)
    return jsonify({
        "success": True,
        "runs": runs,
    })


@automation_bp.route("/api/automation/runs/<run_id>", methods=["GET"])
@require_auth
def get_run(run_id: str):
    try:
        run = AutomationService.get_run(run_id, user=g.current_user)
        return jsonify({
            "success": True,
            "run": run,
        })
    except PermissionError as pe:
        return jsonify({"success": False, "error": str(pe)}), 403
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404


@automation_bp.route("/api/automation/runs/<run_id>/verify-resolution", methods=["POST"])
@require_auth
def verify_resolution(run_id: str):
    """Employee feedback on whether diagnostic resolved the issue."""
    data = request.get_json() or {}
    try:
        req = AutomationVerifyRequest(**data)
        res = AutomationService.verify_resolution(
            run_id=run_id,
            resolved=req.resolved,
            user=g.current_user,
            feedback=req.feedback,
        )
        return jsonify({
            "success": True,
            "result": res,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
