import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from utils.error_handlers import register_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("itsm_helpdesk")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for configured frontend origin and localhost
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers="*",
    )

    # Register blueprints
    from routes.auth import auth_bp
    from routes.tickets import tickets_bp
    from routes.chat import chat_bp
    from routes.knowledge import knowledge_bp
    from routes.automation import automation_bp
    from routes.software import software_bp
    from routes.servicenow import servicenow_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(automation_bp)
    app.register_blueprint(software_bp)
    app.register_blueprint(servicenow_bp)
    app.register_blueprint(dashboard_bp)

    # Register error handlers
    register_error_handlers(app)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "ITSM AI Helpdesk Platform API",
            "version": "1.0.0",
            "integrations": Config.get_status(),
        })

    return app


app = create_app()

if __name__ == "__main__":
    status = Config.get_status()
    logger.info("=" * 60)
    logger.info("ITSM AI-Powered Helpdesk Automation Platform API starting...")
    logger.info(f"Port: {Config.PORT} | Environment: {Config.FLASK_ENV}")
    logger.info(f"MongoDB configured: {status.get('mongodb_configured')} (DB: {status.get('mongodb_db')})")
    logger.info(f"Groq API configured: {status['groq_configured']} (Model: {status['groq_model']})")
    logger.info(f"Pinecone configured: {status['pinecone_configured']} (Index: {status['pinecone_index']})")
    logger.info(f"ServiceNow Demo Mode: {status['servicenow_demo_mode']}")
    logger.info("=" * 60)

    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.FLASK_DEBUG,
    )
