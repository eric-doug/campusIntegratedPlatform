import uuid
from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

outbound_bp = Blueprint('outbound', __name__)


@outbound_bp.route('', methods=['GET'])
def list_outbound():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        total = session.execute(text("SELECT COUNT(*) FROM outbound_orders")).fetchone()[0]
        results = session.execute(
            text("SELECT id, order_no, warehouse_id, type, status, total_qty, remark, created_at FROM outbound_orders ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
            {'limit': per_page, 'offset': (page - 1) * per_page}
        ).fetchall()
        items = [{
            'id': r[0], 'order_no': r[1], 'warehouse_id': r[2], 'type': r[3],
            'status': r[4], 'total_qty': r[5], 'remark': r[6],
            'created_at': r[7].isoformat() if r[7] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@outbound_bp.route('', methods=['POST'])
@require_auth
def create_outbound():
    data = request.get_json()
    if not data or not data.get('warehouse_id') or not data.get('type'):
        return error_response('Warehouse ID and type are required', 400)
    order_no = f"OUT{uuid.uuid4().hex[:12].upper()}"
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO outbound_orders (order_no, warehouse_id, type, status, total_qty, remark) VALUES (:order_no, :warehouse_id, :type, 'pending', :total_qty, :remark) RETURNING id"),
            {'order_no': order_no, 'warehouse_id': data['warehouse_id'], 'type': data['type'], 'total_qty': data.get('total_qty', 0), 'remark': data.get('remark')}
        )
        order_id = result.fetchone()[0]
        if data.get('items'):
            for item in data['items']:
                session.execute(
                    text("INSERT INTO outbound_items (outbound_order_id, product_sku_id, qty, batch_no, location_id) VALUES (:order_id, :product_sku_id, :qty, :batch_no, :location_id)"),
                    {'order_id': order_id, 'product_sku_id': item.get('product_sku_id'), 'qty': item['qty'], 'batch_no': item.get('batch_no'), 'location_id': item.get('location_id')}
                )
        session.commit()
        return success_response({'id': order_id, 'order_no': order_no}, 'Outbound order created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
