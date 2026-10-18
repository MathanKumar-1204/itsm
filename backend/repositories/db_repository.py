import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from repositories.mongo_client import get_mongo_db, sanitize_doc
from repositories.supabase_client import get_supabase_admin_client

logger = logging.getLogger(__name__)


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


class DBRepository:
    """
    Unified Data Access Layer supporting MongoDB Cloud Atlas as primary database.
    Provides automated fallbacks to maintain system stability and zero-demo-data cleanliness.
    """

    def __init__(self):
        self._memory_users: Dict[str, Dict[str, Any]] = {}
        self._memory_tickets: Dict[str, Dict[str, Any]] = {}
        self._memory_comments: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_sessions: Dict[str, Dict[str, Any]] = {}
        self._memory_messages: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_documents: Dict[str, Dict[str, Any]] = {}
        self._memory_articles: Dict[str, Dict[str, Any]] = {}
        self._memory_automation_runs: Dict[str, Dict[str, Any]] = {}
        self._memory_catalog: Dict[str, Dict[str, Any]] = {}
        self._memory_software_requests: Dict[str, Dict[str, Any]] = {}
        self._memory_audit_logs: List[Dict[str, Any]] = []
        self._ticket_counter = 1000
        self._request_counter = 5000

        self._seed_default_catalog_and_users()

    def _seed_default_catalog_and_users(self):
        """Seeds corporate software catalog and default system accounts (no demo tickets/articles)."""
        catalog_items = [
            {
                "id": "11111111-1111-1111-1111-111111111101",
                "name": "Visual Studio Code",
                "description": "Standard corporate IDE for software engineering, scripting, and web development.",
                "vendor": "Microsoft",
                "category": "Developer Tools",
                "approval_required": False,
                "enabled": True,
                "provisioning_mode": "simulated",
                "instructions": "Automated silent installation via enterprise package manager winget install Microsoft.VisualStudioCode",
                "created_at": utc_now_iso(),
            },
            {
                "id": "11111111-1111-1111-1111-111111111102",
                "name": "Python 3.12 Developer Suite",
                "description": "Official Python runtime environment with pip, virtualenv, and standard developer tools.",
                "vendor": "Python Software Foundation",
                "category": "Developer Tools",
                "approval_required": False,
                "enabled": True,
                "provisioning_mode": "simulated",
                "instructions": "Deploys standard Python 3.12 runtime configured with company trusted PyPI mirror.",
                "created_at": utc_now_iso(),
            },
            {
                "id": "11111111-1111-1111-1111-111111111103",
                "name": "Microsoft Teams Enterprise",
                "description": "Primary collaboration, voice, video conferencing, and internal communication client.",
                "vendor": "Microsoft",
                "category": "Collaboration",
                "approval_required": False,
                "enabled": True,
                "provisioning_mode": "integrated",
                "instructions": "Provisioned via Microsoft 365 licensing portal and Intune endpoint deployment.",
                "created_at": utc_now_iso(),
            },
            {
                "id": "11111111-1111-1111-1111-111111111104",
                "name": "Docker Desktop Enterprise",
                "description": "Containerization software for local development and microservice testing. Requires paid corporate license.",
                "vendor": "Docker Inc.",
                "category": "Developer Tools",
                "approval_required": True,
                "enabled": True,
                "provisioning_mode": "simulated",
                "instructions": "Assigned via Docker Business admin console after departmental billing approval.",
                "created_at": utc_now_iso(),
            },
            {
                "id": "11111111-1111-1111-1111-111111111105",
                "name": "Postman Enterprise",
                "description": "API platform for building, designing, and testing RESTful and GraphQL APIs.",
                "vendor": "Postman",
                "category": "Developer Tools",
                "approval_required": True,
                "enabled": True,
                "provisioning_mode": "simulated",
                "instructions": "Requires IT security review for API workspace sharing permissions.",
                "created_at": utc_now_iso(),
            },
            {
                "id": "11111111-1111-1111-1111-111111111106",
                "name": "Internal Financial ERP Access",
                "description": "Privileged access to enterprise resource planning portal and accounting records.",
                "vendor": "Enterprise Internal",
                "category": "Security & Access",
                "approval_required": True,
                "enabled": True,
                "provisioning_mode": "manual",
                "instructions": "Manual provisioning ticket dispatched to Identity & Access Management team.",
                "created_at": utc_now_iso(),
            },
        ]
        for item in catalog_items:
            self._memory_catalog[item["id"]] = item

        # Default system accounts
        default_users = [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "email": "admin@enterprise.com",
                "password_hash": generate_password_hash("Admin123!"),
                "full_name": "Morgan Enterprise Admin",
                "role": "admin",
                "department": "IT Operations",
                "created_at": utc_now_iso(),
            },
            {
                "id": "00000000-0000-0000-0000-000000000002",
                "email": "agent@enterprise.com",
                "password_hash": generate_password_hash("Agent123!"),
                "full_name": "Jordan Support Agent",
                "role": "it_agent",
                "department": "IT Support",
                "created_at": utc_now_iso(),
            },
            {
                "id": "00000000-0000-0000-0000-000000000003",
                "email": "employee@enterprise.com",
                "password_hash": generate_password_hash("Employee123!"),
                "full_name": "Alex Employee",
                "role": "employee",
                "department": "Engineering",
                "created_at": utc_now_iso(),
            },
        ]
        for u in default_users:
            self._memory_users[u["email"]] = u

        # Seed MongoDB collections if connected and empty
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                # Seed software catalog if empty
                if mongo_db.software_catalog.count_documents({}) == 0:
                    mongo_db.software_catalog.insert_many(catalog_items)
                    logger.info("Seeded initial software catalog in MongoDB Atlas.")

                # Seed default users if empty
                if mongo_db.users.count_documents({}) == 0:
                    mongo_db.users.insert_many(default_users)
                    logger.info("Seeded default enterprise accounts in MongoDB Atlas.")
            except Exception as e:
                logger.warning(f"Could not seed initial MongoDB collections: {e}")

    # ==================== USERS & AUTH ====================

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new user record in MongoDB Atlas or memory store."""
        user_id = data.get("id") or str(uuid.uuid4())
        email = data["email"].strip().lower()
        now = utc_now_iso()

        raw_password = data.get("password")
        password_hash = data.get("password_hash")
        if raw_password and not password_hash:
            password_hash = generate_password_hash(raw_password)

        record = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": data.get("full_name", email.split("@")[0].title()),
            "role": data.get("role", "employee"),
            "department": data.get("department", "General"),
            "created_at": now,
            "updated_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.users.insert_one(record)
                clean = sanitize_doc(record)
                clean.pop("password_hash", None)
                return clean
            except Exception as e:
                logger.error(f"MongoDB create_user error: {e}")
                raise

        self._memory_users[email] = record
        clean = dict(record)
        clean.pop("password_hash", None)
        return clean

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves user by email address."""
        if not email:
            return None
        clean_email = email.strip().lower()
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                user = mongo_db.users.find_one({"email": clean_email})
                return sanitize_doc(user)
            except Exception as e:
                logger.error(f"MongoDB get_user_by_email error: {e}")

        user = self._memory_users.get(clean_email)
        return dict(user) if user else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves user by UUID."""
        if not user_id:
            return None
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                user = mongo_db.users.find_one({"id": user_id})
                return sanitize_doc(user)
            except Exception as e:
                logger.error(f"MongoDB get_user_by_id error: {e}")

        for u in self._memory_users.values():
            if u.get("id") == user_id:
                return dict(u)
        return None

    def verify_user_password(self, user: Dict[str, Any], password: str) -> bool:
        """Verifies plaintext password against hashed password."""
        stored_hash = user.get("password_hash")
        if not stored_hash:
            return False
        return check_password_hash(stored_hash, password)

    # ==================== TICKETS ====================

    def create_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new incident/service ticket."""
        now = utc_now_iso()
        ticket_id = data.get("id") or str(uuid.uuid4())
        
        # Determine ticket number
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                count = mongo_db.tickets.count_documents({}) + 1001
                ticket_number = data.get("ticket_number") or f"INC-{count}"
            except Exception:
                self._ticket_counter += 1
                ticket_number = data.get("ticket_number") or f"INC-{self._ticket_counter}"
        else:
            self._ticket_counter += 1
            ticket_number = data.get("ticket_number") or f"INC-{self._ticket_counter}"

        record = {
            "id": ticket_id,
            "ticket_number": ticket_number,
            "requester_id": data.get("requester_id", "00000000-0000-0000-0000-000000000001"),
            "requester_name": data.get("requester_name", "Alex Employee"),
            "requester_email": data.get("requester_email", "employee@enterprise.com"),
            "title": data["title"],
            "description": data["description"],
            "category": data.get("category", "General IT"),
            "ticket_type": data.get("ticket_type", "incident"),
            "impact": data.get("impact", "medium"),
            "urgency": data.get("urgency", "medium"),
            "priority": data.get("priority", "medium"),
            "status": data.get("status", "open"),
            "source": data.get("source", "portal"),
            "ai_summary": data.get("ai_summary"),
            "ai_confidence": data.get("ai_confidence"),
            "assigned_to": data.get("assigned_to"),
            "resolution": data.get("resolution"),
            "external_system": data.get("external_system"),
            "external_record_id": data.get("external_record_id"),
            "external_record_url": data.get("external_record_url"),
            "last_synced_at": data.get("last_synced_at"),
            "created_at": now,
            "updated_at": now,
            "resolved_at": data.get("resolved_at"),
        }

        if mongo_db is not None:
            try:
                mongo_db.tickets.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB create_ticket error: {e}")

        # Supabase fallback if configured
        admin_client = get_supabase_admin_client()
        if admin_client:
            try:
                res = admin_client.table("tickets").insert(record).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception:
                pass

        self._memory_tickets[ticket_id] = record
        return record

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves ticket by ID or ticket number."""
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                ticket = mongo_db.tickets.find_one({"$or": [{"id": ticket_id}, {"ticket_number": ticket_id}]})
                if ticket:
                    return sanitize_doc(ticket)
            except Exception as e:
                logger.error(f"MongoDB get_ticket error: {e}")

        for t in self._memory_tickets.values():
            if t.get("id") == ticket_id or t.get("ticket_number") == ticket_id:
                return dict(t)
        return self._memory_tickets.get(ticket_id)

    def list_tickets(
        self,
        requester_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Lists tickets with filtering, search, and pagination."""
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                query: Dict[str, Any] = {}
                if requester_id:
                    query["requester_id"] = requester_id
                if status:
                    query["status"] = status
                if category:
                    query["category"] = category
                if priority:
                    query["priority"] = priority
                if search:
                    s_regex = {"$regex": search, "$options": "i"}
                    query["$or"] = [{"title": s_regex}, {"description": s_regex}, {"ticket_number": s_regex}]

                cursor = mongo_db.tickets.find(query).sort("created_at", -1).skip(offset).limit(limit)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_tickets error: {e}")

        # Memory store
        items = list(self._memory_tickets.values())
        if requester_id:
            items = [t for t in items if t.get("requester_id") == requester_id]
        if status:
            items = [t for t in items if t.get("status") == status]
        if category:
            items = [t for t in items if t.get("category") == category]
        if priority:
            items = [t for t in items if t.get("priority") == priority]
        if search:
            s = search.lower()
            items = [t for t in items if s in t.get("title", "").lower() or s in t.get("description", "").lower()]

        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset : offset + limit]

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Updates ticket fields."""
        updates["updated_at"] = utc_now_iso()
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.tickets.update_one({"id": ticket_id}, {"$set": updates})
                updated = mongo_db.tickets.find_one({"id": ticket_id})
                if updated:
                    return sanitize_doc(updated)
            except Exception as e:
                logger.error(f"MongoDB update_ticket error: {e}")

        if ticket_id in self._memory_tickets:
            self._memory_tickets[ticket_id].update(updates)
            return self._memory_tickets[ticket_id]
        return None

    def add_ticket_comment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adds comment to a ticket."""
        comment_id = str(uuid.uuid4())
        now = utc_now_iso()
        record = {
            "id": comment_id,
            "ticket_id": data["ticket_id"],
            "author_id": data.get("author_id"),
            "author_name": data.get("author_name", "Support Agent"),
            "comment": data["comment"],
            "visibility": data.get("visibility", "public"),
            "created_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.ticket_comments.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB add_ticket_comment error: {e}")

        t_id = data["ticket_id"]
        if t_id not in self._memory_comments:
            self._memory_comments[t_id] = []
        self._memory_comments[t_id].append(record)
        return record

    def list_ticket_comments(self, ticket_id: str, include_internal: bool = True) -> List[Dict[str, Any]]:
        """Lists comments for a given ticket."""
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                query = {"ticket_id": ticket_id}
                if not include_internal:
                    query["visibility"] = "public"
                cursor = mongo_db.ticket_comments.find(query).sort("created_at", 1)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_ticket_comments error: {e}")

        comments = self._memory_comments.get(ticket_id, [])
        if not include_internal:
            comments = [c for c in comments if c.get("visibility") == "public"]
        return comments

    # ==================== KNOWLEDGE DOCUMENTS ====================

    def create_knowledge_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Registers an uploaded knowledge document."""
        now = utc_now_iso()
        doc_id = data.get("id") or str(uuid.uuid4())
        record = {
            "id": doc_id,
            "uploaded_by": data.get("uploaded_by"),
            "title": data["title"],
            "original_filename": data["original_filename"],
            "storage_path": data.get("storage_path", ""),
            "mime_type": data.get("mime_type"),
            "file_size": data.get("file_size", 0),
            "status": data.get("status", "uploaded"),
            "chunk_count": data.get("chunk_count", 0),
            "error_message": data.get("error_message"),
            "created_at": now,
            "updated_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.knowledge_documents.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB create_knowledge_document error: {e}")

        self._memory_documents[doc_id] = record
        return record

    def update_knowledge_document(self, doc_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now_iso()
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.knowledge_documents.update_one({"id": doc_id}, {"$set": updates})
                doc = mongo_db.knowledge_documents.find_one({"id": doc_id})
                if doc:
                    return sanitize_doc(doc)
            except Exception as e:
                logger.error(f"MongoDB update_knowledge_document error: {e}")

        if doc_id in self._memory_documents:
            self._memory_documents[doc_id].update(updates)
            return self._memory_documents[doc_id]
        return None

    def list_knowledge_documents(self) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                cursor = mongo_db.knowledge_documents.find({}).sort("created_at", -1)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_knowledge_documents error: {e}")

        docs = list(self._memory_documents.values())
        docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return docs

    def get_knowledge_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                doc = mongo_db.knowledge_documents.find_one({"id": doc_id})
                if doc:
                    return sanitize_doc(doc)
            except Exception as e:
                logger.error(f"MongoDB get_knowledge_document error: {e}")

        return self._memory_documents.get(doc_id)

    def delete_knowledge_document(self, doc_id: str) -> bool:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.knowledge_documents.delete_one({"id": doc_id})
            except Exception as e:
                logger.error(f"MongoDB delete_knowledge_document error: {e}")

        if doc_id in self._memory_documents:
            del self._memory_documents[doc_id]
        return True

    # ==================== KNOWLEDGE ARTICLES ====================

    def create_knowledge_article(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        art_id = data.get("id") or str(uuid.uuid4())
        record = {
            "id": art_id,
            "title": data["title"],
            "summary": data.get("summary"),
            "content": data["content"],
            "category": data.get("category", "General IT"),
            "source_ticket_id": data.get("source_ticket_id"),
            "status": data.get("status", "draft"),
            "created_by": data.get("created_by"),
            "approved_by": data.get("approved_by"),
            "approved_at": data.get("approved_at"),
            "created_at": now,
            "updated_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.knowledge_articles.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB create_knowledge_article error: {e}")

        self._memory_articles[art_id] = record
        return record

    def list_knowledge_articles(self, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                query: Dict[str, Any] = {}
                if status:
                    query["status"] = status
                if category:
                    query["category"] = category
                cursor = mongo_db.knowledge_articles.find(query).sort("created_at", -1)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_knowledge_articles error: {e}")

        articles = list(self._memory_articles.values())
        if status:
            articles = [a for a in articles if a.get("status") == status]
        if category:
            articles = [a for a in articles if a.get("category") == category]
        articles.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return articles

    def get_knowledge_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                art = mongo_db.knowledge_articles.find_one({"id": article_id})
                if art:
                    return sanitize_doc(art)
            except Exception as e:
                logger.error(f"MongoDB get_knowledge_article error: {e}")

        return self._memory_articles.get(article_id)

    def update_knowledge_article(self, article_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now_iso()
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.knowledge_articles.update_one({"id": article_id}, {"$set": updates})
                art = mongo_db.knowledge_articles.find_one({"id": article_id})
                if art:
                    return sanitize_doc(art)
            except Exception as e:
                logger.error(f"MongoDB update_knowledge_article error: {e}")

        if article_id in self._memory_articles:
            self._memory_articles[article_id].update(updates)
            return self._memory_articles[article_id]
        return None

    # ==================== SOFTWARE CATALOG & REQUESTS ====================

    def list_software_catalog(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                query = {"enabled": True} if enabled_only else {}
                cursor = mongo_db.software_catalog.find(query)
                items = [sanitize_doc(d) for d in cursor]
                if items:
                    return items
            except Exception as e:
                logger.error(f"MongoDB list_software_catalog error: {e}")

        items = list(self._memory_catalog.values())
        if enabled_only:
            items = [i for i in items if i.get("enabled")]
        return items

    def get_software_item(self, software_id: str) -> Optional[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                item = mongo_db.software_catalog.find_one({"id": software_id})
                if item:
                    return sanitize_doc(item)
            except Exception as e:
                logger.error(f"MongoDB get_software_item error: {e}")

        return self._memory_catalog.get(software_id)

    def create_software_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        req_id = data.get("id") or str(uuid.uuid4())
        
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                count = mongo_db.software_requests.count_documents({}) + 5001
                req_number = data.get("request_number") or f"SR-{count}"
            except Exception:
                self._request_counter += 1
                req_number = data.get("request_number") or f"SR-{self._request_counter}"
        else:
            self._request_counter += 1
            req_number = data.get("request_number") or f"SR-{self._request_counter}"

        record = {
            "id": req_id,
            "request_number": req_number,
            "requester_id": data.get("requester_id"),
            "requester_name": data.get("requester_name", "Employee"),
            "software_id": data.get("software_id"),
            "software_name": data.get("software_name"),
            "business_justification": data.get("business_justification"),
            "status": data.get("status", "submitted"),
            "approved_by": data.get("approved_by"),
            "approval_comment": data.get("approval_comment"),
            "provisioning_status": data.get("provisioning_status", "pending"),
            "execution_mode": data.get("execution_mode", "simulated"),
            "external_record_id": data.get("external_record_id"),
            "created_at": now,
            "updated_at": now,
            "completed_at": data.get("completed_at"),
        }

        if mongo_db is not None:
            try:
                mongo_db.software_requests.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB create_software_request error: {e}")

        self._memory_software_requests[req_id] = record
        return record

    def list_software_requests(self, requester_id: Optional[str] = None) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                query = {"requester_id": requester_id} if requester_id else {}
                cursor = mongo_db.software_requests.find(query).sort("created_at", -1)
                reqs = [sanitize_doc(d) for d in cursor]
                for r in reqs:
                    sw_item = self.get_software_item(r.get("software_id"))
                    if sw_item:
                        r["software_name"] = sw_item.get("name")
                        r["software_vendor"] = sw_item.get("vendor")
                return reqs
            except Exception as e:
                logger.error(f"MongoDB list_software_requests error: {e}")

        requests = list(self._memory_software_requests.values())
        if requester_id:
            requests = [r for r in requests if r.get("requester_id") == requester_id]
        for r in requests:
            sw = self._memory_catalog.get(r.get("software_id"))
            if sw:
                r["software_name"] = sw.get("name")
                r["software_vendor"] = sw.get("vendor")
        requests.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return requests

    def get_software_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                req = mongo_db.software_requests.find_one({"id": request_id})
                if req:
                    r = sanitize_doc(req)
                    sw_item = self.get_software_item(r.get("software_id"))
                    if sw_item:
                        r["software_catalog"] = sw_item
                    return r
            except Exception as e:
                logger.error(f"MongoDB get_software_request error: {e}")

        req = self._memory_software_requests.get(request_id)
        if req:
            sw = self._memory_catalog.get(req.get("software_id"))
            if sw:
                req["software_catalog"] = sw
        return req

    def update_software_request(self, request_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now_iso()
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.software_requests.update_one({"id": request_id}, {"$set": updates})
                req = mongo_db.software_requests.find_one({"id": request_id})
                if req:
                    return sanitize_doc(req)
            except Exception as e:
                logger.error(f"MongoDB update_software_request error: {e}")

        if request_id in self._memory_software_requests:
            self._memory_software_requests[request_id].update(updates)
            return self._memory_software_requests[request_id]
        return None

    # ==================== AUTOMATION RUNS ====================

    def create_automation_run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        run_id = data.get("id") or str(uuid.uuid4())
        record = {
            "id": run_id,
            "ticket_id": data.get("ticket_id"),
            "initiated_by": data.get("initiated_by"),
            "workflow_name": data["workflow_name"],
            "issue_category": data.get("issue_category"),
            "input_summary": data.get("input_summary"),
            "status": data.get("status", "started"),
            "steps": data.get("steps", []),
            "result_summary": data.get("result_summary"),
            "error_message": data.get("error_message"),
            "resolved": data.get("resolved", False),
            "requires_approval": data.get("requires_approval", False),
            "execution_mode": data.get("execution_mode", "simulated"),
            "started_at": now,
            "completed_at": data.get("completed_at"),
            "created_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.automation_runs.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB create_automation_run error: {e}")

        self._memory_automation_runs[run_id] = record
        return record

    def update_automation_run(self, run_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.automation_runs.update_one({"id": run_id}, {"$set": updates})
                run = mongo_db.automation_runs.find_one({"id": run_id})
                if run:
                    return sanitize_doc(run)
            except Exception as e:
                logger.error(f"MongoDB update_automation_run error: {e}")

        if run_id in self._memory_automation_runs:
            self._memory_automation_runs[run_id].update(updates)
            return self._memory_automation_runs[run_id]
        return None

    def list_automation_runs(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                query = {"initiated_by": user_id} if user_id else {}
                cursor = mongo_db.automation_runs.find(query).sort("created_at", -1).limit(limit)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_automation_runs error: {e}")

        runs = list(self._memory_automation_runs.values())
        if user_id:
            runs = [r for r in runs if r.get("initiated_by") == user_id]
        runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return runs[:limit]

    def get_automation_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                run = mongo_db.automation_runs.find_one({"id": run_id})
                if run:
                    return sanitize_doc(run)
            except Exception as e:
                logger.error(f"MongoDB get_automation_run error: {e}")

        return self._memory_automation_runs.get(run_id)

    # ==================== AUDIT LOGS ====================

    def log_audit(self, actor_id: Optional[str], action: str, entity_type: str, entity_id: Optional[str], metadata: Dict[str, Any] = None):
        now = utc_now_iso()
        record = {
            "id": str(uuid.uuid4()),
            "actor_id": actor_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "created_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.audit_logs.insert_one(record)
                return
            except Exception as e:
                logger.error(f"MongoDB log_audit error: {e}")

        self._memory_audit_logs.insert(0, record)

    def list_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                cursor = mongo_db.audit_logs.find({}).sort("created_at", -1).limit(limit)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_audit_logs error: {e}")

        return self._memory_audit_logs[:limit]

    # ==================== CHAT ====================

    def create_chat_session(self, user_id: str, title: str = "New Conversation") -> Dict[str, Any]:
        now = utc_now_iso()
        session_id = str(uuid.uuid4())
        record = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.chat_sessions.insert_one(record)
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB create_chat_session error: {e}")

        self._memory_sessions[session_id] = record
        self._memory_messages[session_id] = []
        return record

    def list_chat_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                cursor = mongo_db.chat_sessions.find({"user_id": user_id}).sort("updated_at", -1)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB list_chat_sessions error: {e}")

        sessions = [s for s in self._memory_sessions.values() if s.get("user_id") == user_id]
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions

    def add_chat_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        now = utc_now_iso()
        msg_id = str(uuid.uuid4())
        record = {
            "id": msg_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": now,
        }

        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                mongo_db.chat_messages.insert_one(record)
                mongo_db.chat_sessions.update_one({"id": session_id}, {"$set": {"updated_at": now}})
                return sanitize_doc(record)
            except Exception as e:
                logger.error(f"MongoDB add_chat_message error: {e}")

        if session_id not in self._memory_messages:
            self._memory_messages[session_id] = []
        self._memory_messages[session_id].append(record)
        if session_id in self._memory_sessions:
            self._memory_sessions[session_id]["updated_at"] = now
        return record

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            try:
                cursor = mongo_db.chat_messages.find({"session_id": session_id}).sort("created_at", 1)
                return [sanitize_doc(d) for d in cursor]
            except Exception as e:
                logger.error(f"MongoDB get_session_messages error: {e}")

        return self._memory_messages.get(session_id, [])

    # ==================== METRICS ====================

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Calculates live metrics from actual database records (no static mock counts)."""
        tickets = self.list_tickets(limit=1000)
        software_reqs = self.list_software_requests()
        docs = self.list_knowledge_documents()
        runs = self.list_automation_runs(limit=500)

        total_tickets = len(tickets)
        open_tickets = len([t for t in tickets if t.get("status") in ("new", "open")])
        in_progress_tickets = len([t for t in tickets if t.get("status") == "in_progress"])
        resolved_tickets = len([t for t in tickets if t.get("status") in ("resolved", "closed")])
        high_priority_tickets = len([t for t in tickets if t.get("priority") in ("high", "critical")])
        pending_software = len([r for r in software_reqs if r.get("status") == "pending_approval"])
        indexed_docs = len([d for d in docs if d.get("status") == "indexed"])
        failed_runs = len([r for r in runs if r.get("status") == "failed"])

        by_category: Dict[str, int] = {}
        for t in tickets:
            cat = t.get("category", "General IT")
            by_category[cat] = by_category.get(cat, 0) + 1

        by_status: Dict[str, int] = {}
        for t in tickets:
            st = t.get("status", "open")
            by_status[st] = by_status.get(st, 0) + 1

        by_priority: Dict[str, int] = {}
        for t in tickets:
            pr = t.get("priority", "medium")
            by_priority[pr] = by_priority.get(pr, 0) + 1

        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "resolved_tickets": resolved_tickets,
            "high_priority_tickets": high_priority_tickets,
            "pending_software_approvals": pending_software,
            "knowledge_documents_indexed": indexed_docs,
            "failed_automation_runs": failed_runs,
            "by_category": [{"category": k, "count": v} for k, v in by_category.items()],
            "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
            "by_priority": [{"priority": k, "count": v} for k, v in by_priority.items()],
        }


# Singleton database repository instance
db = DBRepository()
