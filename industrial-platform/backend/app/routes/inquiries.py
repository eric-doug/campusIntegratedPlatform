from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

inquiries_bp = Blueprint('inquiries', __name__)


@inquiries_bp.route('', methods=['GET'])
@require_auth
def list_inquiries():
    """List inquiries for current user."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.current_user['user_id']

    session = db.get_session()
    try:
        total = session.execute(
            text("SELECT COUNT(*) FROM inquiries WHERE buyer_id = :user_id"), {'user_id': user_id}
        ).fetchone()[0]

        results = session.execute(
            text("""SELECT id, buyer_id, status, total_items, remark, created_at, updated_at
               FROM inquiries WHERE buyer_id = :user_id ORDER BY created_at DESC LIMIT :limit OFFSET :offset"""),
            {'user_id': user_id, 'limit': per_page, 'offset': (page - 1) * per_page}
        ).fetchall()

        items = [{
            'id': r[0], 'buyer_id': r[1], 'status': r[2], 'total_items': r[3],
            'remark': r[4], 'created_at': r[5].isoformat() if r[5] else None,
            'updated_at': r[6].isoformat() if r[6] else None,
        } for r in results]

        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@inquiries_bp.route('', methods=['POST'])
@require_auth
def create_inquiry():
    """Create a new inquiry."""
    data = request.get_json()
    if not data or not data.get('items'):
        return error_response('Inquiry items are required', 400)

    user_id = request.current_user['user_id']
    session = db.get_session()
    try:
        # Create inquiry
        result = session.execute(
            text("INSERT INTO inquiries (buyer_id, total_items, remark) VALUES (:buyer_id, :total_items, :remark) RETURNING id"),
            {'buyer_id': user_id, 'total_items': len(data['items']), 'remark': data.get('remark')}
        )
        inquiry_id = result.fetchone()[0]

        # Create items
        for item in data['items']:
            session.execute(
                text("INSERT INTO inquiry_items (inquiry_id, product_sku_id, qty, target_price, remark) VALUES (:inquiry_id, :product_sku_id, :qty, :target_price, :remark)"),
                {'inquiry_id': inquiry_id, 'product_sku_id': item.get('product_sku_id'), 'qty': item['qty'],
                 'target_price': item.get('target_price'), 'remark': item.get('remark')}
            )

        session.commit()
        return success_response({'id': inquiry_id}, 'Inquiry created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@inquiries_bp.route('/<int:inquiry_id>', methods=['GET'])
@require_auth
def get_inquiry(inquiry_id):
    """Get inquiry detail with items and quotes."""
    session = db.get_session()
    try:
        result = session.execute(
            text("SELECT id, buyer_id, status, total_items, remark, created_at FROM inquiries WHERE id = :inquiry_id"),
            {'inquiry_id': inquiry_id}
        )
        inquiry = result.fetchone()
        if not inquiry:
            return error_response('Inquiry not found', 404)

        # Get items
        items_result = session.execute(
            text("""SELECT ii.id, ii.product_sku_id, ii.qty, ii.target_price, ii.remark
               FROM inquiry_items ii WHERE ii.inquiry_id = :inquiry_id"""),
            {'inquiry_id': inquiry_id}
        )
        items = [{
            'id': r[0], 'product_sku_id': r[1], 'qty': r[2],
            'target_price': float(r[3]) if r[3] else None, 'remark': r[4],
        } for r in items_result.fetchall()]

        return success_response({
            'id': inquiry[0], 'buyer_id': inquiry[1], 'status': inquiry[2],
            'total_items': inquiry[3], 'remark': inquiry[4],
            'created_at': inquiry[5].isoformat() if inquiry[5] else None,
            'items': items,
        })
    finally:
        session.close()
