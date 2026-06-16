from flask import jsonify


def success_response(data=None, message='success', code=200):
    """Return a successful response."""
    response = {
        'code': code,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), code


def error_response(message='error', code=400, errors=None):
    """Return an error response."""
    response = {
        'code': code,
        'message': message,
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), code


def paginate_response(items, total, page, per_page, message='success'):
    """Return a paginated response."""
    return jsonify({
        'code': 200,
        'message': message,
        'data': {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
        }
    }), 200
