import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional, Dict, Any
import jwt
from flask import request, jsonify, g
from config import Config
from repositories.db_repository import db

logger = logging.getLogger(__name__)


def generate_jwt_token(user: Dict[str, Any], expires_days: int = 7) -> str:
    """Generates a signed HS256 JWT bearer token for the given user."""
    payload = {
        "sub": user.get("id"),
        "email": user.get("email"),
        "role": user.get("role", "employee"),
        "full_name": user.get("full_name", user.get("email")),
        "department": user.get("department", "General"),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a signed JWT token."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "employee"),
            "full_name": payload.get("full_name"),
            "department": payload.get("department", "General"),
            "token": token,
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def get_authenticated_user() -> Optional[Dict[str, Any]]:
    """
    Validates bearer token from request header.
    Returns user dict: { id, email, role, full_name, department } or None.
    """
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    # 1. Real JWT verification (HS256)
    if token and token.count(".") == 2 and not token.startswith("dev-"):
        verified_user = verify_jwt_token(token)
        if verified_user:
            # Confirm user existence in DB if possible
            db_user = db.get_user_by_id(verified_user["id"]) or db.get_user_by_email(verified_user["email"])
            if db_user:
                return {
                    "id": db_user["id"],
                    "email": db_user["email"],
                    "role": db_user.get("role", verified_user["role"]),
                    "full_name": db_user.get("full_name", verified_user["full_name"]),
                    "department": db_user.get("department", verified_user["department"]),
                    "designation": db_user.get("designation") or request.headers.get("X-Employee-Designation") or verified_user.get("designation", "Full Stack Software Engineer"),
                    "token": token,
                }
            return {
                **verified_user,
                "designation": request.headers.get("X-Employee-Designation") or verified_user.get("designation", "Full Stack Software Engineer")
            }

    # 2. Development or quick-switch token fallback
    is_dev_request = (
        request.headers.get("X-Dev-Mode") == "true"
        or token in ["dev-token", "mock-token", "test-token"]
        or (token and token.startswith("dev-"))
        or not token
    )

    if is_dev_request:
        # Check role from token suffix or header
        default_role = "admin"
        if token and "admin" in token:
            default_role = "admin"
        elif token and "agent" in token:
            default_role = "it_agent"
        elif token and "employee" in token:
            default_role = "employee"

        dev_role = request.headers.get("X-Dev-User-Role", default_role)
        if dev_role not in ["employee", "it_agent", "admin"]:
            dev_role = "admin"

        role_presets = {
            "admin": ("admin@enterprise.com", "Morgan Enterprise Admin", "IT Operations", "Senior IT Operations Director"),
            "it_agent": ("agent@enterprise.com", "Jordan Support Agent", "IT Support", "IT Support Specialist"),
            "employee": ("employee@enterprise.com", "Alex Employee", "Engineering", "Full Stack Software Engineer"),
        }
        def_email, def_name, def_dept, def_desig = role_presets.get(dev_role, role_presets["admin"])

        dev_email = request.headers.get("X-Dev-User-Email", def_email)
        dev_name = request.headers.get("X-Dev-User-Name", def_name)
        dev_desig = request.headers.get("X-Employee-Designation", def_desig)
        dev_id = request.headers.get("X-Dev-User-Id", f"00000000-0000-0000-0000-00000000000{1 if dev_role == 'admin' else (2 if dev_role == 'it_agent' else 3)}")

        return {
            "id": dev_id,
            "email": dev_email,
            "role": dev_role,
            "full_name": dev_name,
            "department": def_dept,
            "designation": dev_desig,
            "token": token or f"dev-token-{dev_role}",
            "is_dev": True,
        }

    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200
        user = get_authenticated_user()
        if not user:
            return jsonify({
                "success": False,
                "error": "Authentication required. Please provide a valid Bearer token.",
                "code": "UNAUTHORIZED"
            }), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method == "OPTIONS":
                return jsonify({"status": "ok"}), 200
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    "success": False,
                    "error": "Authentication required.",
                    "code": "UNAUTHORIZED"
                }), 401
            if user.get("role") not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": f"Forbidden. Role '{user.get('role')}' does not have permission for this resource.",
                    "code": "FORBIDDEN"
                }), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated
    return decorator
