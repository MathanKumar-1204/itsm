from flask import Blueprint, jsonify, g, request
from utils.auth_middleware import require_auth, require_role
from repositories.db_repository import db
from config import Config

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/metrics", methods=["GET"])
@require_auth
def get_metrics():
    """Returns live aggregated counts and breakdowns computed from real DB records."""
    metrics = db.get_dashboard_metrics()
    return jsonify({
        "success": True,
        "metrics": metrics,
    })


@dashboard_bp.route("/api/audit-logs", methods=["GET"])
@require_role(["admin"])
def get_audit_logs():
    """Returns immutable security and action audit log."""
    limit = int(request.args.get("limit", 100))
    logs = db.list_audit_logs(limit=limit)
    return jsonify({
        "success": True,
        "logs": logs,
    })


@dashboard_bp.route("/api/config/status", methods=["GET"])
def get_config_status():
    """Returns non-sensitive health and integration status."""
    return jsonify({
        "success": True,
        "config": Config.get_status(),
    })
