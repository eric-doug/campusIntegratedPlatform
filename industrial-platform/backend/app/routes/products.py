from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response
from shared.utils.logger import setup_logger

logger = setup_logger('industrial.products')
products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
def list_products():
    """List products with pagination and filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', 'active')

    session = db.get_session()
    try:
        query = "SELECT id, name, category_id, supplier_id, specs, unit, description, images, status, created_at FROM products WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM products WHERE 1=1"
        params = []

        if status:
            query += " AND status = %s"
            count_query += " AND status = %s"
            params.append(status)
        if category_id:
            query += " AND category_id = %s"
            count_query += " AND category_id = %s"
            params.append(category_id)
        if keyword:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            count_query += " AND (name ILIKE %s OR description ILIKE %s)"
            params.extend([f'%{keyword}%', f'%{keyword}%'])

        # Count
        total = session.execute(count_query, params).fetchone()[0]

        # Paginate
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])

        results = session.execute(query, params).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'category_id': r[2], 'supplier_id': r[3],
            'specs': r[4], 'unit': r[5], 'description': r[6], 'images': r[7],
            'status': r[8], 'created_at': r[9].isoformat() if r[9] else None,
        } for r in results]

        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product detail."""
    session = db.get_session()
    try:
        result = session.execute(
            "SELECT id, name, category_id, supplier_id, specs, unit, description, images, status, created_at FROM products WHERE id = %s",
            (product_id,)
        )
        product = result.fetchone()
        if not product:
            return error_response('Product not found', 404)

        # Get SKUs
        sku_result = session.execute(
            "SELECT id, sku_code, attributes, price, original_price, stock, min_order_qty, status FROM product_skus WHERE product_id = %s",
            (product_id,)
        )
        skus = [{
            'id': r[0], 'sku_code': r[1], 'attributes': r[2],
            'price': float(r[3]) if r[3] else None,
            'original_price': float(r[4]) if r[4] else None,
            'stock': r[5], 'min_order_qty': r[6], 'status': r[7],
        } for r in sku_result.fetchall()]

        return success_response({
            'id': product[0], 'name': product[1], 'category_id': product[2],
            'supplier_id': product[3], 'specs': product[4], 'unit': product[5],
            'description': product[6], 'images': product[7], 'status': product[8],
            'created_at': product[9].isoformat() if product[9] else None,
            'skus': skus,
        })
    finally:
        session.close()


@products_bp.route('', methods=['POST'])
@require_auth
def create_product():
    """Create a new product."""
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response('Product name is required', 400)

    session = db.get_session()
    try:
        result = session.execute(
            """INSERT INTO products (name, category_id, supplier_id, specs, unit, description, images, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (data['name'], data.get('category_id'), data.get('supplier_id'),
             data.get('specs', {}), data.get('unit'), data.get('description'),
             data.get('images', []), data.get('status', 'active'))
        )
        product_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': product_id}, 'Product created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@products_bp.route('/<int:product_id>', methods=['PUT'])
@require_auth
def update_product(product_id):
    """Update a product."""
    data = request.get_json()
    if not data:
        return error_response('No data provided', 400)

    session = db.get_session()
    try:
        fields = []
        params = []
        for key in ['name', 'category_id', 'supplier_id', 'specs', 'unit', 'description', 'images', 'status']:
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])

        if not fields:
            return error_response('No fields to update', 400)

        params.append(product_id)
        session.execute(
            f"UPDATE products SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s",
            params
        )
        session.commit()
        return success_response(message='Product updated')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    """Soft delete a product."""
    session = db.get_session()
    try:
        session.execute(
            "UPDATE products SET status = 'deleted', updated_at = NOW() WHERE id = %s",
            (product_id,)
        )
        session.commit()
        return success_response(message='Product deleted')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
