import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "success": False,
            "error": "Bad request",
            "message": str(e.description) if hasattr(e, "description") else "Invalid request data",
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Valid authentication credentials are required.",
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "success": False,
            "error": "Forbidden",
            "message": "You do not have permission to access this resource.",
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": "Not found",
            "message": "The requested endpoint does not exist.",
        }), 404

    @app.errorhandler(413)
    def payload_too_large(e):
        return jsonify({
            "success": False,
            "error": "Payload too large",
            "message": "File exceeds the configured maximum upload limit.",
        }), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please contact IT support.",
        }), 500
