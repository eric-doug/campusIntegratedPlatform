from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('', methods=['GET'])
def list_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    session = db.get_session()
    try:
        query = "SELECT id, warehouse_id, product_sku_id, qty, locked_qty, batch_no, updated_at FROM inventory WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM inventory WHERE 1=1"
        params = {}
        if warehouse_id:
            query += " AND warehouse_id = :warehouse_id"
            count_query += " AND warehouse_id = :warehouse_id"
            params['warehouse_id'] = warehouse_id
        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY updated_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'warehouse_id': r[1], 'product_sku_id': r[2],
            'qty': r[3], 'locked_qty': r[4], 'available_qty': r[3] - r[4],
            'batch_no': r[5], 'updated_at': r[6].isoformat() if r[6] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@inventory_bp.route('/summary', methods=['GET'])
def inventory_summary():
    session = db.get_session()
    try:
        result = session.execute(
            text("SELECT COUNT(*) as total_skus, SUM(qty) as total_qty, SUM(locked_qty) as total_locked FROM inventory")
        ).fetchone()
        return success_response({
            'total_skus': result[0], 'total_qty': result[1] or 0, 'total_locked': result[2] or 0,
            'total_available': (result[1] or 0) - (result[2] or 0),
        })
    finally:
        session.close()
