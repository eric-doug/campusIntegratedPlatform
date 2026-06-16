import bcrypt
from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.jwt_handler import generate_tokens, verify_token, refresh_access_token
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response
from shared.utils.validators import validate_required, validate_phone, validate_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    valid, msg = validate_required(data, ['username', 'password'])
    if not valid:
        return error_response(msg, 400)

    if data.get('phone') and not validate_phone(data['phone']):
        return error_response('Invalid phone number', 400)
    if data.get('email') and not validate_email(data['email']):
        return error_response('Invalid email', 400)

    session = db.get_session()
    try:
        # Check if username exists
        result = session.execute(
            "SELECT id FROM users WHERE username = %s", (data['username'],)
        )
        if result.fetchone():
            return error_response('Username already exists', 409)

        # Hash password
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

        # Insert user
        result = session.execute(
            "INSERT INTO users (username, phone, email, password_hash) VALUES (%s, %s, %s, %s) RETURNING id",
            (data['username'], data.get('phone'), data.get('email'), password_hash)
        )
        user_id = result.fetchone()[0]
        session.commit()

        tokens = generate_tokens(user_id)
        return success_response({'user_id': user_id, **tokens}, 'Registration successful', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with username and password."""
    data = request.get_json()
    valid, msg = validate_required(data, ['username', 'password'])
    if not valid:
        return error_response(msg, 400)

    session = db.get_session()
    try:
        result = session.execute(
            "SELECT id, password_hash, status FROM users WHERE username = %s",
            (data['username'],)
        )
        user = result.fetchone()
        if not user:
            return error_response('Invalid credentials', 401)

        user_id, password_hash, status = user
        if status != 'active':
            return error_response('Account is disabled', 403)

        if not bcrypt.checkpw(data['password'].encode('utf-8'), password_hash.encode('utf-8')):
            return error_response('Invalid credentials', 401)

        # Get user roles and permissions
        result = session.execute(
            """SELECT r.code, pp.platform, pp.resource, pp.action
               FROM user_roles ur
               JOIN roles r ON ur.role_id = r.id
               LEFT JOIN platform_permissions pp ON pp.role_id = r.id
               WHERE ur.user_id = %s""",
            (user_id,)
        )
        roles = []
        permissions = []
        for row in result.fetchall():
            roles.append(row[0])
            if row[1] and row[2] and row[3]:
                permissions.append(f"{row[1]}:{row[2]}:{row[3]}")

        tokens = generate_tokens(user_id, roles=roles, permissions=permissions)
        return success_response({'user_id': user_id, **tokens})
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        session.close()


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token."""
    data = request.get_json()
    if not data or not data.get('refresh_token'):
        return error_response('Refresh token required', 400)

    result = refresh_access_token(data['refresh_token'])
    if not result:
        return error_response('Invalid refresh token', 401)

    return success_response(result)


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info."""
    user_id = request.current_user['user_id']
    session = db.get_session()
    try:
        result = session.execute(
            "SELECT id, username, phone, email, status FROM users WHERE id = %s",
            (user_id,)
        )
        user = result.fetchone()
        if not user:
            return error_response('User not found', 404)
        return success_response({
            'id': user[0],
            'username': user[1],
            'phone': user[2],
            'email': user[3],
            'status': user[4],
            'roles': request.current_user.get('roles', []),
        })
    finally:
        session.close()
