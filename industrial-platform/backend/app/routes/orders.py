import uuid
from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('', methods=['GET'])
@require_auth
def list_orders():
    """List orders for current user."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.current_user['user_id']

    session = db.get_session()
    try:
        total = session.execute(
            "SELECT COUNT(*) FROM orders WHERE buyer_id = %s", (user_id,)
        ).fetchone()[0]

        results = session.execute(
            """SELECT id, order_no, buyer_id, status, total_amount, payment_status, delivery_address, remark, created_at
               FROM orders WHERE buyer_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s""",
            (user_id, per_page, (page - 1) * per_page)
        ).fetchall()

        items = [{
            'id': r[0], 'order_no': r[1], 'buyer_id': r[2], 'status': r[3],
            'total_amount': float(r[4]) if r[4] else None, 'payment_status': r[5],
            'delivery_address': r[6], 'remark': r[7],
            'created_at': r[8].isoformat() if r[8] else None,
        } for r in results]

        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@orders_bp.route('', methods=['POST'])
@require_auth
def create_order():
    """Create a new order."""
    data = request.get_json()
    if not data or not data.get('items'):
        return error_response('Order items are required', 400)

    user_id = request.current_user['user_id']
    order_no = f"ORD{uuid.uuid4().hex[:12].upper()}"
    session = db.get_session()
    try:
        total_amount = 0
        order_items = []

        # Calculate total
        for item in data['items']:
            sku_result = session.execute(
                "SELECT price, stock FROM product_skus WHERE id = %s",
                (item['product_sku_id'],)
            ).fetchone()
            if not sku_result:
                return error_response(f"SKU {item['product_sku_id']} not found", 400)
            price = float(sku_result[0])
            qty = item['qty']
            amount = price * qty
            total_amount += amount
            order_items.append({
                'product_sku_id': item['product_sku_id'],
                'qty': qty, 'unit_price': price, 'amount': amount,
            })

        # Create order
        result = session.execute(
            """INSERT INTO orders (order_no, buyer_id, status, total_amount, payment_status, delivery_address, remark)
               VALUES (%s, %s, 'pending', %s, 'unpaid', %s, %s) RETURNING id""",
            (order_no, user_id, total_amount,
             data.get('delivery_address', {}), data.get('remark'))
        )
        order_id = result.fetchone()[0]

        # Create order items
        for item in order_items:
            session.execute(
                "INSERT INTO order_items (order_id, product_sku_id, qty, unit_price, amount) VALUES (%s, %s, %s, %s, %s)",
                (order_id, item['product_sku_id'], item['qty'], item['unit_price'], item['amount'])
            )

        session.commit()
        return success_response({'id': order_id, 'order_no': order_no}, 'Order created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@orders_bp.route('/<int:order_id>', methods=['GET'])
@require_auth
def get_order(order_id):
    """Get order detail."""
    session = db.get_session()
    try:
        result = session.execute(
            """SELECT id, order_no, buyer_id, status, total_amount, payment_status, delivery_address, remark, created_at
               FROM orders WHERE id = %s""",
            (order_id,)
        )
        order = result.fetchone()
        if not order:
            return error_response('Order not found', 404)

        # Get items
        items_result = session.execute(
            "SELECT id, product_sku_id, qty, unit_price, amount FROM order_items WHERE order_id = %s",
            (order_id,)
        )
        items = [{
            'id': r[0], 'product_sku_id': r[1], 'qty': r[2],
            'unit_price': float(r[3]) if r[3] else None,
            'amount': float(r[4]) if r[4] else None,
        } for r in items_result.fetchall()]

        return success_response({
            'id': order[0], 'order_no': order[1], 'buyer_id': order[2],
            'status': order[3], 'total_amount': float(order[4]) if order[4] else None,
            'payment_status': order[5], 'delivery_address': order[6],
            'remark': order[7], 'created_at': order[8].isoformat() if order[8] else None,
            'items': items,
        })
    finally:
        session.close()
