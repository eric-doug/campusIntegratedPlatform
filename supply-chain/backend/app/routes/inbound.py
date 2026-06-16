import uuid
from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

inbound_bp = Blueprint('inbound', __name__)


@inbound_bp.route('', methods=['GET'])
def list_inbound():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    session = db.get_session()
    try:
        query = "SELECT id, order_no, warehouse_id, supplier_id, status, total_qty, remark, created_at FROM inbound_orders WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM inbound_orders WHERE 1=1"
        params = []
        if status:
            query += " AND status = %s"
            count_query += " AND status = %s"
            params.append(status)
        total = session.execute(count_query, params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        results = session.execute(query, params).fetchall()
        items = [{
            'id': r[0], 'order_no': r[1], 'warehouse_id': r[2], 'supplier_id': r[3],
            'status': r[4], 'total_qty': r[5], 'remark': r[6],
            'created_at': r[7].isoformat() if r[7] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@inbound_bp.route('', methods=['POST'])
@require_auth
def create_inbound():
    data = request.get_json()
    if not data or not data.get('warehouse_id'):
        return error_response('Warehouse ID is required', 400)
    order_no = f"INB{uuid.uuid4().hex[:12].upper()}"
    session = db.get_session()
    try:
        result = session.execute(
            "INSERT INTO inbound_orders (order_no, warehouse_id, supplier_id, status, total_qty, remark) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (order_no, data['warehouse_id'], data.get('supplier_id'), 'pending', data.get('total_qty', 0), data.get('remark'))
        )
        order_id = result.fetchone()[0]
        if data.get('items'):
            for item in data['items']:
                session.execute(
                    "INSERT INTO inbound_items (inbound_order_id, product_sku_id, qty, batch_no, location_id, status) VALUES (%s, %s, %s, %s, %s, %s)",
                    (order_id, item.get('product_sku_id'), item['qty'], item.get('batch_no'), item.get('location_id'), 'pending')
                )
        session.commit()
        return success_response({'id': order_id, 'order_no': order_no}, 'Inbound order created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
