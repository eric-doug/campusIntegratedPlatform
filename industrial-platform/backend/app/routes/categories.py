from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
def list_categories():
    """List all categories as tree structure."""
    session = db.get_session()
    try:
        result = session.execute(
            "SELECT id, name, parent_id, level, sort_order, icon, status FROM categories WHERE status = 'active' ORDER BY sort_order, id"
        )
        categories = [{
            'id': r[0], 'name': r[1], 'parent_id': r[2], 'level': r[3],
            'sort_order': r[4], 'icon': r[5], 'status': r[6],
        } for r in result.fetchall()]

        # Build tree
        tree = []
        lookup = {c['id']: {**c, 'children': []} for c in categories}
        for c in categories:
            node = lookup[c['id']]
            if c['parent_id'] and c['parent_id'] in lookup:
                lookup[c['parent_id']]['children'].append(node)
            else:
                tree.append(node)

        return success_response(tree)
    finally:
        session.close()


@categories_bp.route('', methods=['POST'])
@require_auth
def create_category():
    """Create a new category."""
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response('Category name is required', 400)

    session = db.get_session()
    try:
        result = session.execute(
            "INSERT INTO categories (name, parent_id, level, sort_order, icon, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (data['name'], data.get('parent_id'), data.get('level', 1),
             data.get('sort_order', 0), data.get('icon'), data.get('status', 'active'))
        )
        category_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': category_id}, 'Category created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
