import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory or root directory
backend_dir = Path(__file__).resolve().parent
root_dir = backend_dir.parent

if (backend_dir / ".env").exists():
    load_dotenv(backend_dir / ".env")
elif (root_dir / ".env").exists():
    load_dotenv(root_dir / ".env")
else:
    load_dotenv()


class Config:
    # Server configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    PORT = int(os.getenv("PORT", 5000))
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # Supabase configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    # Groq API configuration (GPT-OSS models)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    GROQ_FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b").strip()

    # Pinecone Vector Database
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "itsm-knowledge").strip()
    PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "itsm-public").strip()

    # Embedding Model (384-dimensional)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2").strip()

    # ServiceNow REST API Configuration
    SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "").strip().rstrip("/")
    SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", "").strip()
    SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "").strip()
    SERVICENOW_CLIENT_ID = os.getenv("SERVICENOW_CLIENT_ID", "").strip()
    SERVICENOW_CLIENT_SECRET = os.getenv("SERVICENOW_CLIENT_SECRET", "").strip()
    SERVICENOW_AUTH_MODE = os.getenv("SERVICENOW_AUTH_MODE", "basic").strip().lower()
    SERVICENOW_DEMO_MODE = os.getenv("SERVICENOW_DEMO_MODE", "true").lower() in ("true", "1", "yes")

    # MongoDB Cloud Atlas configuration
    MONGO_URI = os.getenv("MONGO_URI", os.getenv("MONGODB_URI", "")).strip()
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "itsm_platform").strip()
    JWT_SECRET = os.getenv("JWT_SECRET", "itsm-secure-jwt-secret-key-2026").strip()

    # Uploads
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 10))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    @classmethod
    def get_status(cls):
        """Returns non-sensitive status of configured integrations."""
        return {
            "mongodb_configured": bool(cls.MONGO_URI),
            "mongodb_db": cls.MONGO_DB_NAME,
            "supabase_configured": bool(cls.SUPABASE_URL and (cls.SUPABASE_SERVICE_ROLE_KEY or cls.SUPABASE_ANON_KEY)),
            "groq_configured": bool(cls.GROQ_API_KEY),
            "groq_model": cls.GROQ_MODEL,
            "groq_fallback_model": cls.GROQ_FALLBACK_MODEL,
            "pinecone_configured": bool(cls.PINECONE_API_KEY),
            "pinecone_index": cls.PINECONE_INDEX_NAME,
            "embedding_model": cls.EMBEDDING_MODEL,
            "servicenow_configured": bool(cls.SERVICENOW_INSTANCE_URL and cls.SERVICENOW_USERNAME and cls.SERVICENOW_PASSWORD),
            "servicenow_instance": cls.SERVICENOW_INSTANCE_URL or None,
            "servicenow_demo_mode": cls.SERVICENOW_DEMO_MODE,
        }
