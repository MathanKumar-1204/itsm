import logging
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, generate_jwt_token
from repositories.db_repository import db

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticates a user via email and password, returning a signed JWT token."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
    if not password:
        return jsonify({"success": False, "error": "Password is required."}), 400

    # Look up user in database
    user = db.get_user_by_email(email)

    # Check password
    if user and db.verify_user_password(user, password):
        clean_user = {
            "id": user["id"],
            "email": user["email"],
            "role": user.get("role", "employee"),
            "full_name": user.get("full_name", email.split("@")[0].title()),
            "department": user.get("department", "General"),
        }
        token = generate_jwt_token(clean_user)
        return jsonify({
            "success": True,
            "token": token,
            "user": clean_user,
            "message": "Login successful.",
        })

    # If default admin/agent/employee entered with standard password
    defaults = {
        "admin@enterprise.com": ("Admin123!", "admin", "Morgan Enterprise Admin", "IT Operations"),
        "agent@enterprise.com": ("Agent123!", "it_agent", "Jordan Support Agent", "IT Support"),
        "employee@enterprise.com": ("Employee123!", "employee", "Alex Employee", "Engineering"),
    }
    if email in defaults:
        expected_pw, role, name, dept = defaults[email]
        if password == expected_pw:
            new_user = db.create_user({
                "email": email,
                "password": password,
                "full_name": name,
                "role": role,
                "department": dept,
            })
            clean_user = {
                "id": new_user["id"],
                "email": new_user["email"],
                "role": new_user["role"],
                "full_name": new_user["full_name"],
                "department": new_user["department"],
            }
            token = generate_jwt_token(clean_user)
            return jsonify({
                "success": True,
                "token": token,
                "user": clean_user,
                "message": "Login successful.",
            })

    return jsonify({"success": False, "error": "Invalid email or password."}), 401


@auth_bp.route("/api/auth/register", methods=["POST"])
@auth_bp.route("/api/auth/signup", methods=["POST"])
def register():
    """Registers a new user account with hashed password in database."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "employee").strip().lower()
    department = data.get("department", "General").strip()

    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
    if not password or len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400
    if not full_name:
        full_name = email.split("@")[0].title()

    if role not in ["employee", "it_agent", "admin"]:
        role = "employee"

    # Check if email is already registered
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({"success": False, "error": "An account with this email already exists."}), 400

    try:
        new_user = db.create_user({
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": role,
            "department": department,
        })

        clean_user = {
            "id": new_user["id"],
            "email": new_user["email"],
            "role": new_user["role"],
            "full_name": new_user["full_name"],
            "department": new_user["department"],
        }
        token = generate_jwt_token(clean_user)

        return jsonify({
            "success": True,
            "token": token,
            "user": clean_user,
            "message": "Account created successfully.",
        }), 201
    except Exception as e:
        logger.error(f"User registration error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/api/me", methods=["GET"])
@auth_bp.route("/api/auth/me", methods=["GET"])
@require_auth
def get_current_user_profile():
    """Returns the authenticated user profile."""
    return jsonify({
        "success": True,
        "user": g.current_user,
    })


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Client logout handler."""
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })
