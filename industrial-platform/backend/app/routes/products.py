from flask import Blueprint, request
from sqlalchemy import text
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
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    status = request.args.get('status', 'active')

    session = db.get_session()
    try:
        query = """SELECT p.id, p.name, p.category_id, p.supplier_id, p.specs, p.unit, p.description, p.images, p.status, p.created_at,
                          (SELECT MIN(ps.price) FROM product_skus ps WHERE ps.product_id = p.id AND ps.status = 'active') as min_price,
                          (SELECT MAX(ps.price) FROM product_skus ps WHERE ps.product_id = p.id AND ps.status = 'active') as max_price,
                          (SELECT COUNT(*) FROM product_skus ps WHERE ps.product_id = p.id) as sku_count
                   FROM products p WHERE 1=1"""
        count_query = "SELECT COUNT(*) FROM products p WHERE 1=1"
        params = {}

        if status:
            query += " AND p.status = :status"
            count_query += " AND p.status = :status"
            params['status'] = status
        if category_id:
            query += " AND p.category_id = :category_id"
            count_query += " AND p.category_id = :category_id"
            params['category_id'] = category_id
        if category:
            query += " AND EXISTS (SELECT 1 FROM categories c WHERE c.id = p.category_id AND c.name ILIKE :category)"
            count_query += " AND EXISTS (SELECT 1 FROM categories c WHERE c.id = p.category_id AND c.name ILIKE :category)"
            params['category'] = f'%{category}%'
        if keyword:
            query += " AND (p.name ILIKE :keyword1 OR p.description ILIKE :keyword2)"
            count_query += " AND (p.name ILIKE :keyword1 OR p.description ILIKE :keyword2)"
            params['keyword1'] = f'%{keyword}%'
            params['keyword2'] = f'%{keyword}%'
        if min_price is not None:
            query += " AND EXISTS (SELECT 1 FROM product_skus ps WHERE ps.product_id = p.id AND ps.status = 'active' AND ps.price >= :min_price)"
            count_query += " AND EXISTS (SELECT 1 FROM product_skus ps WHERE ps.product_id = p.id AND ps.status = 'active' AND ps.price >= :min_price)"
            params['min_price'] = min_price
        if max_price is not None:
            query += " AND EXISTS (SELECT 1 FROM product_skus ps WHERE ps.product_id = p.id AND ps.status = 'active' AND ps.price <= :max_price)"
            count_query += " AND EXISTS (SELECT 1 FROM product_skus ps WHERE ps.product_id = p.id AND ps.status = 'active' AND ps.price <= :max_price)"
            params['max_price'] = max_price

        # Count
        total = session.execute(text(count_query), params).fetchone()[0]

        # Paginate
        query += " ORDER BY p.created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page

        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'category_id': r[2], 'supplier_id': r[3],
            'specs': r[4], 'unit': r[5], 'description': r[6], 'images': r[7],
            'status': r[8], 'created_at': r[9].isoformat() if r[9] else None,
            'min_price': float(r[10]) if r[10] else None,
            'max_price': float(r[11]) if r[11] else None,
            'sku_count': r[12],
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
            text("SELECT id, name, category_id, supplier_id, specs, unit, description, images, status, created_at FROM products WHERE id = :product_id"),
            {'product_id': product_id}
        )
        product = result.fetchone()
        if not product:
            return error_response('Product not found', 404)

        # Get SKUs
        sku_result = session.execute(
            text("SELECT id, sku_code, attributes, price, original_price, stock, min_order_qty, status FROM product_skus WHERE product_id = :product_id"),
            {'product_id': product_id}
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
            text("""INSERT INTO products (name, category_id, supplier_id, specs, unit, description, images, status)
               VALUES (:name, :category_id, :supplier_id, :specs, :unit, :description, :images, :status) RETURNING id"""),
            {'name': data['name'], 'category_id': data.get('category_id'), 'supplier_id': data.get('supplier_id'),
             'specs': str(data.get('specs', {})), 'unit': data.get('unit'), 'description': data.get('description'),
             'images': str(data.get('images', [])), 'status': data.get('status', 'active')}
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
        params = {'product_id': product_id}
        for key in ['name', 'category_id', 'supplier_id', 'specs', 'unit', 'description', 'images', 'status']:
            if key in data:
                fields.append(f"{key} = :{key}")
                if key in ['specs', 'images']:
                    params[key] = str(data[key])
                else:
                    params[key] = data[key]

        if not fields:
            return error_response('No fields to update', 400)

        session.execute(
            text(f"UPDATE products SET {', '.join(fields)}, updated_at = NOW() WHERE id = :product_id"),
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
            text("UPDATE products SET status = 'deleted', updated_at = NOW() WHERE id = :product_id"),
            {'product_id': product_id}
        )
        session.commit()
        return success_response(message='Product deleted')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
