from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

warehouses_bp = Blueprint('warehouses', __name__)


@warehouses_bp.route('', methods=['GET'])
def list_warehouses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        total = session.execute(text("SELECT COUNT(*) FROM warehouses")).fetchone()[0]
        results = session.execute(
            text("SELECT id, name, code, location, capacity, used_capacity, status, created_at FROM warehouses ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
            {'limit': per_page, 'offset': (page - 1) * per_page}
        ).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'code': r[2], 'location': r[3],
            'capacity': float(r[4]) if r[4] else None, 'used_capacity': float(r[5]) if r[5] else None,
            'status': r[6], 'created_at': r[7].isoformat() if r[7] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@warehouses_bp.route('', methods=['POST'])
@require_auth
def create_warehouse():
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response('Warehouse name is required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO warehouses (name, code, location, capacity, status) VALUES (:name, :code, :location, :capacity, :status) RETURNING id"),
            {'name': data['name'], 'code': data.get('code'), 'location': str(data.get('location', {})), 'capacity': data.get('capacity'), 'status': data.get('status', 'active')}
        )
        warehouse_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': warehouse_id}, 'Warehouse created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
