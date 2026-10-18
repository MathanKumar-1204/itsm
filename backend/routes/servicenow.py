from flask import Blueprint, jsonify, g
from utils.auth_middleware import require_role
from integrations.servicenow import servicenow_client

servicenow_bp = Blueprint("servicenow", __name__)


@servicenow_bp.route("/api/integrations/servicenow/status", methods=["GET"])
@require_role(["it_agent", "admin"])
def get_status():
    """Returns integration configuration and demo mode state."""
    status = servicenow_client.get_connection_status()
    return jsonify({
        "success": True,
        "status": status,
    })


@servicenow_bp.route("/api/integrations/servicenow/test", methods=["POST"])
@require_role(["it_agent", "admin"])
def test_connection():
    """Tests connection to live ServiceNow instance or returns demo confirmation."""
    result = servicenow_client.test_connection()
    return jsonify({
        "success": True,
        "result": result,
    })
