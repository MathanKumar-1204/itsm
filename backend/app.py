import os
import sys
import logging
from flask import Flask, jsonify, render_template, send_from_directory
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
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(backend_dir, "templates")

    app = Flask(
        __name__,
        template_folder=templates_dir if os.path.isdir(templates_dir) else backend_dir,
        static_folder=backend_dir,
    )
    app.config.from_object(Config)

    # Enable CORS for configured frontend origin and all callers
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
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

    @app.route("/", methods=["GET"])
    @app.route("/index.html", methods=["GET"])
    def home_page():
        """Serves the interactive landing dashboard for Vercel and web browsers."""
        try:
            return render_template("index.html")
        except Exception:
            index_path = os.path.join(backend_dir, "index.html")
            if os.path.exists(index_path):
                return send_from_directory(backend_dir, "index.html")
            return jsonify({
                "status": "healthy",
                "service": "ITSM AI Helpdesk Platform API",
                "version": "1.0.0",
                "database": "MongoDB Cloud Atlas",
                "integrations": Config.get_status(),
            })

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "ITSM AI Helpdesk Platform API",
            "version": "1.0.0",
            "database": "MongoDB Cloud Atlas",
            "integrations": Config.get_status(),
        })

    return app


app = create_app()

if __name__ == "__main__":
    status = Config.get_status()
    logger.info("=" * 60)
    logger.info("ITSM AI-Powered Helpdesk Automation Platform API starting...")
    logger.info(f"Port: {Config.PORT} | Environment: {Config.FLASK_ENV}")
    logger.info(f"Primary Database: MongoDB Cloud Atlas ({status.get('mongodb_db')})")
    logger.info("Supabase: Disabled (100% MongoDB for all platform features)")
    logger.info(f"Groq API: {status['groq_configured']} (Keys count: {status.get('groq_keys_count')})")
    logger.info(f"Pinecone: {status['pinecone_configured']} (Index: {status['pinecone_index']})")
    logger.info(f"ServiceNow Demo Mode: {status['servicenow_demo_mode']}")
    logger.info("=" * 60)

    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.FLASK_DEBUG,
    )
