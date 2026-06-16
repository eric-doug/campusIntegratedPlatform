from functools import wraps
from flask import request, jsonify
from .jwt_handler import verify_token


def require_auth(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'code': 401, 'message': 'Missing or invalid token'}), 401

        token = auth_header.split(' ', 1)[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': 'Invalid or expired token'}), 401

        request.current_user = payload
        return f(*args, **kwargs)
    return decorated


def require_permission(platform, resource, action):
    """Decorator to require specific platform permission."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            permissions = request.current_user.get('permissions', [])
            required = f"{platform}:{resource}:{action}"
            admin_required = f"{platform}:*:*"
            super_admin = "*:*:*"

            if required in permissions or admin_required in permissions or super_admin in permissions:
                return f(*args, **kwargs)
            return jsonify({'code': 403, 'message': 'Permission denied'}), 403
        return decorated
    return decorator
