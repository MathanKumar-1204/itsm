import logging
import urllib.request
import json
import re
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None
_mongo_db = None
_is_connected = False


def _resolve_srv_via_https(srv_uri: str) -> str:
    """
    On networks where outbound UDP 53 is blocked (e.g. Windows firewalls/VPN adapters),
    this resolves MongoDB Atlas SRV & TXT records over HTTPS (Google Public DNS)
    and returns a direct replicaSet connection URI.
    """
    if not srv_uri or not srv_uri.startswith("mongodb+srv://"):
        return srv_uri

    try:
        match = re.match(r"^mongodb\+srv://([^@]+)@([^/?]+)(?:/([^?]*))?(?:\?(.*))?$", srv_uri)
        if not match:
            return srv_uri

        auth_part, host, db_name, query_params = match.groups()

        # Query SRV record via HTTPS
        srv_url = f"https://dns.google/resolve?name=_mongodb._tcp.{host}&type=SRV"
        req = urllib.request.Request(srv_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            srv_data = json.loads(res.read().decode())
            answers = srv_data.get("Answer", [])

        if not answers:
            return srv_uri

        targets = []
        for ans in answers:
            parts = ans.get("data", "").split()
            if len(parts) >= 4:
                port = parts[2]
                target = parts[3].rstrip(".")
                targets.append(f"{target}:{port}")

        if not targets:
            return srv_uri

        hosts_str = ",".join(targets)

        # Query TXT record for replicaSet and authSource
        txt_url = f"https://dns.google/resolve?name={host}&type=TXT"
        extra_params = "ssl=true&authSource=admin"
        try:
            req_txt = urllib.request.Request(txt_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_txt, timeout=5) as res:
                txt_data = json.loads(res.read().decode())
                txt_answers = txt_data.get("Answer", [])
                for ans in txt_answers:
                    txt_data_str = ans.get("data", "").strip('"')
                    if "replicaSet" in txt_data_str:
                        extra_params += f"&{txt_data_str}"
        except Exception:
            pass

        target_db = db_name or Config.MONGO_DB_NAME
        query_str = f"?{extra_params}"
        if query_params:
            query_str += f"&{query_params}"

        direct_uri = f"mongodb://{auth_part}@{hosts_str}/{target_db}{query_str}"
        logger.info("Successfully converted SRV URI to direct Atlas replicaSet URI via HTTPS DNS.")
        return direct_uri
    except Exception as e:
        logger.warning(f"Could not resolve SRV via HTTPS: {e}")
        return srv_uri


def get_mongo_client() -> Optional[MongoClient]:
    """Returns the singleton MongoDB MongoClient instance."""
    global _mongo_client, _is_connected
    if _mongo_client is not None:
        return _mongo_client

    if not Config.MONGO_URI:
        logger.info("MONGO_URI is not set. Operating in in-memory repository mode.")
        return None

    uris_to_try = [Config.MONGO_URI]
    if Config.MONGO_URI.startswith("mongodb+srv://"):
        direct = _resolve_srv_via_https(Config.MONGO_URI)
        if direct != Config.MONGO_URI:
            # Try resolved direct connection first for maximum Windows reliability
            uris_to_try = [direct, Config.MONGO_URI]

    for uri in uris_to_try:
        try:
            logger.info("Connecting to MongoDB Atlas...")
            client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                appname="ITSMHelpdeskPlatform"
            )
            # Test connection ping
            client.admin.command("ping")
            _mongo_client = client
            _is_connected = True
            logger.info(f"Successfully connected to MongoDB Cloud Atlas (Database: {Config.MONGO_DB_NAME})")
            
            # Initialize indexes on required collections
            _init_db_indexes(client[Config.MONGO_DB_NAME])
            return _mongo_client
        except Exception as err:
            logger.warning(f"Connection attempt failed: {err}")

    logger.error("All MongoDB Atlas connection attempts failed. Falling back to in-memory repository.")
    _mongo_client = None
    _is_connected = False
    return None


def get_mongo_db():
    """Returns the database instance from MongoDB Atlas, or None if not connected."""
    global _mongo_db
    if _mongo_db is not None:
        return _mongo_db

    client = get_mongo_client()
    if client is not None:
        _mongo_db = client[Config.MONGO_DB_NAME]
        return _mongo_db
    return None


def is_mongo_connected() -> bool:
    """Checks if MongoDB connection is active."""
    global _is_connected
    if not _is_connected:
        get_mongo_client()
    return _is_connected


def _init_db_indexes(db):
    """Creates essential indexes for performance and data integrity."""
    try:
        # Users collection
        db.users.create_index("email", unique=True, sparse=True)
        db.users.create_index("id", unique=True)
        db.users.create_index("role")

        # Tickets collection
        db.tickets.create_index("id", unique=True)
        db.tickets.create_index("ticket_number", unique=True)
        db.tickets.create_index("requester_id")
        db.tickets.create_index("status")
        db.tickets.create_index("category")
        db.tickets.create_index("created_at")

        # Knowledge collection
        db.knowledge_documents.create_index("id", unique=True)
        db.knowledge_documents.create_index("status")
        db.knowledge_articles.create_index("id", unique=True)
        db.knowledge_articles.create_index("status")

        # Software collection
        db.software_catalog.create_index("id", unique=True)
        db.software_requests.create_index("id", unique=True)
        db.software_requests.create_index("requester_id")
        db.software_requests.create_index("status")

        # Automation and audit
        db.automation_runs.create_index("id", unique=True)
        db.audit_logs.create_index("created_at")
        db.chat_messages.create_index("session_id")
        logger.info("MongoDB collection indexes verified in Atlas.")
    except Exception as e:
        logger.warning(f"Could not initialize all MongoDB indexes: {e}")


def sanitize_doc(doc):
    """Converts MongoDB document to JSON-serializable dict by converting ObjectId."""
    if not doc:
        return None
    if isinstance(doc, list):
        return [sanitize_doc(d) for d in doc]
    
    clean = dict(doc)
    if "_id" in clean:
        clean["_id"] = str(clean["_id"])
    return clean
