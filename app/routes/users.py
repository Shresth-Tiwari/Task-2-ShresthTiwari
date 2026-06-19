from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User
from app.schemas import user_schema, users_schema, user_update_schema

users_bp = Blueprint("users", __name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _check_duplicate(username=None, email=None, exclude_id=None):
    """
    Return a 409 JSON response if username or email already exist.
    `exclude_id` skips the check for the user being updated.
    Returns None if no duplicate is found.
    """
    query = User.query
    if exclude_id:
        query = query.filter(User.id != exclude_id)

    if username:
        existing = query.filter(User.username == username).first()
        if existing:
            return jsonify({
                "error": "Conflict",
                "message": f"Username '{username}' is already taken.",
                "field": "username",
            }), 409

    if email:
        existing = query.filter(User.email == email).first()
        if existing:
            return jsonify({
                "error": "Conflict",
                "message": f"Email '{email}' is already registered.",
                "field": "email",
            }), 409

    return None


# ---------------------------------------------------------------------------
# CREATE — POST /api/users
# ---------------------------------------------------------------------------

@users_bp.route("/users", methods=["POST"])
def create_user():
    """Create a new user. Returns 201 on success, 400 on validation error, 409 on duplicate."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"error": "Bad Request", "message": "Request body must be valid JSON."}), 400

    # Validate input
    try:
        user = user_schema.load(json_data, session=db.session)
    except ValidationError as err:
        return jsonify({"error": "Validation Error", "messages": err.messages}), 400

    # Duplicate check (before hitting DB constraint)
    conflict = _check_duplicate(username=user.username, email=user.email)
    if conflict:
        return conflict

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Conflict",
            "message": "A user with that username or email already exists.",
        }), 409

    return jsonify({
        "message": "User created successfully.",
        "user": user.to_dict(),
    }), 201


# ---------------------------------------------------------------------------
# READ ALL — GET /api/users
# ---------------------------------------------------------------------------

@users_bp.route("/users", methods=["GET"])
def get_users():
    """Return a paginated list of all users."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "users": [u.to_dict() for u in pagination.items],
        "pagination": {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        },
    }), 200


# ---------------------------------------------------------------------------
# READ ONE — GET /api/users/<id>
# ---------------------------------------------------------------------------

@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Return a single user by ID. Returns 404 if not found."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": f"No user with id={user_id}."}), 404

    return jsonify({"user": user.to_dict()}), 200


# ---------------------------------------------------------------------------
# UPDATE — PUT /api/users/<id>
# ---------------------------------------------------------------------------

@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update an existing user (partial update supported). Returns 200 on success."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": f"No user with id={user_id}."}), 404

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"error": "Bad Request", "message": "Request body must be valid JSON."}), 400

    # Validate with partial schema (all fields optional)
    try:
        updated_user = user_update_schema.load(json_data, instance=user, session=db.session)
    except ValidationError as err:
        return jsonify({"error": "Validation Error", "messages": err.messages}), 400

    # Duplicate check — exclude the current user from the lookup
    new_username = json_data.get("username")
    new_email = json_data.get("email")
    conflict = _check_duplicate(username=new_username, email=new_email, exclude_id=user_id)
    if conflict:
        return conflict

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Conflict",
            "message": "A user with that username or email already exists.",
        }), 409

    return jsonify({
        "message": "User updated successfully.",
        "user": updated_user.to_dict(),
    }), 200


# ---------------------------------------------------------------------------
# DELETE — DELETE /api/users/<id>
# ---------------------------------------------------------------------------

@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user by ID. Returns 200 on success, 404 if not found."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": f"No user with id={user_id}."}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": f"User id={user_id} deleted successfully.",
    }), 200


# ---------------------------------------------------------------------------
# Global error handlers
# ---------------------------------------------------------------------------

@users_bp.app_errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": str(e)}), 404


@users_bp.app_errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method Not Allowed", "message": str(e)}), 405


@users_bp.app_errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500
