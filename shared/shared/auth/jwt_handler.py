import jwt
import time
import os

JWT_SECRET = os.getenv('JWT_SECRET', 'change-this-in-production')
JWT_ACCESS_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
JWT_REFRESH_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))


def generate_tokens(user_id, roles=None, permissions=None):
    """Generate access token and refresh token."""
    now = int(time.time())
    access_payload = {
        'user_id': user_id,
        'roles': roles or [],
        'permissions': permissions or [],
        'type': 'access',
        'iat': now,
        'exp': now + JWT_ACCESS_EXPIRES,
    }
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'iat': now,
        'exp': now + JWT_REFRESH_EXPIRES,
    }
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm='HS256')
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': JWT_ACCESS_EXPIRES,
    }


def verify_token(token, token_type='access'):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if payload.get('type') != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_access_token(refresh_token):
    """Use refresh token to generate new access token."""
    payload = verify_token(refresh_token, token_type='refresh')
    if not payload:
        return None
    return generate_tokens(
        user_id=payload['user_id'],
        roles=payload.get('roles', []),
        permissions=payload.get('permissions', []),
    )
