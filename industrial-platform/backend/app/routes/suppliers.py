from flask import Blueprint, request
from sqlalchemy import text
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response
from shared.utils.logger import setup_logger

logger = setup_logger('industrial.suppliers')
suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('', methods=['GET'])
def list_suppliers():
    """List suppliers with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    audit_status = request.args.get('audit_status')

    session = db.get_session()
    try:
        query = "SELECT id, name, code, contact_person, contact_phone, status, audit_status, created_at FROM suppliers WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM suppliers WHERE 1=1"
        params = {}

        if keyword:
            query += " AND (name ILIKE :keyword1 OR code ILIKE :keyword2)"
            count_query += " AND (name ILIKE :keyword1 OR code ILIKE :keyword2)"
            params['keyword1'] = f'%{keyword}%'
            params['keyword2'] = f'%{keyword}%'
        if audit_status:
            query += " AND audit_status = :audit_status"
            count_query += " AND audit_status = :audit_status"
            params['audit_status'] = audit_status

        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page

        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'code': r[2], 'contact_person': r[3],
            'contact_phone': r[4], 'status': r[5], 'audit_status': r[6],
            'created_at': r[7].isoformat() if r[7] else None,
        } for r in results]

        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@suppliers_bp.route('', methods=['POST'])
@require_auth
def create_supplier():
    """Apply as a supplier."""
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response('Supplier name is required', 400)

    session = db.get_session()
    try:
        result = session.execute(
            text("""INSERT INTO suppliers (name, code, contact_person, contact_phone, business_license, address, status, audit_status)
               VALUES (:name, :code, :contact_person, :contact_phone, :business_license, :address, 'active', 'pending') RETURNING id"""),
            {'name': data['name'], 'code': data.get('code'), 'contact_person': data.get('contact_person'),
             'contact_phone': data.get('contact_phone'), 'business_license': data.get('business_license'), 'address': data.get('address')}
        )
        supplier_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': supplier_id}, 'Supplier application submitted', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@suppliers_bp.route('/<int:supplier_id>/audit', methods=['POST'])
@require_auth
def audit_supplier(supplier_id):
    """Audit a suppliers application."""
    data = request.get_json()
    if not data or not data.get('action'):
        return error_response('Audit action is required', 400)

    action = data['action']  # approved / rejected
    session = db.get_session()
    try:
        session.execute(
            text("UPDATE suppliers SET audit_status = :action, audit_remark = :remark, updated_at = NOW() WHERE id = :supplier_id"),
            {'action': action, 'remark': data.get('remark'), 'supplier_id': supplier_id}
        )
        session.commit()
        return success_response(message=f'Supplier {action}')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


# ==================== 供应商商品录入功能 ====================

def _get_supplier_by_user(session, user_id):
    """根据当前用户ID查询关联的供应商，返回 supplier 记录或 None。"""
    result = session.execute(
        text("SELECT id, name, code, contact_person, contact_phone, status, audit_status FROM suppliers WHERE user_id = :user_id"),
        {'user_id': user_id}
    )
    return result.fetchone()


@suppliers_bp.route('/me', methods=['GET'])
@require_auth
def get_my_supplier_profile():
    """获取当前登录用户关联的供应商信息。"""
    user_id = request.current_user['user_id']
    session = db.get_session()
    try:
        supplier = _get_supplier_by_user(session, user_id)
        if not supplier:
            return error_response('当前用户未关联供应商账号', 404)
        return success_response({
            'id': supplier[0], 'name': supplier[1], 'code': supplier[2],
            'contact_person': supplier[3], 'contact_phone': supplier[4],
            'status': supplier[5], 'audit_status': supplier[6],
        })
    finally:
        session.close()


@suppliers_bp.route('/me/products', methods=['GET'])
@require_auth
def list_my_products():
    """供应商查看自己录入的商品列表。"""
    user_id = request.current_user['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status')

    session = db.get_session()
    try:
        supplier = _get_supplier_by_user(session, user_id)
        if not supplier:
            return error_response('当前用户未关联供应商账号', 404)
        supplier_id = supplier[0]

        query = """SELECT p.id, p.name, p.category_id, p.specs, p.unit, p.description,
                          p.images, p.status, p.created_at,
                          (SELECT COUNT(*) FROM product_skus ps WHERE ps.product_id = p.id) as sku_count
                   FROM products p WHERE p.supplier_id = :supplier_id"""
        count_query = "SELECT COUNT(*) FROM products WHERE supplier_id = :supplier_id"
        params = {'supplier_id': supplier_id}

        if status:
            query += " AND p.status = :status"
            count_query += " AND status = :status"
            params['status'] = status
        if keyword:
            query += " AND (p.name ILIKE :keyword1 OR p.description ILIKE :keyword2)"
            count_query += " AND (name ILIKE :keyword1 OR description ILIKE :keyword2)"
            params['keyword1'] = f'%{keyword}%'
            params['keyword2'] = f'%{keyword}%'

        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY p.created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page

        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'category_id': r[2], 'specs': r[3],
            'unit': r[4], 'description': r[5], 'images': r[6],
            'status': r[7], 'created_at': r[8].isoformat() if r[8] else None,
            'sku_count': r[9],
        } for r in results]

        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@suppliers_bp.route('/me/products', methods=['POST'])
@require_auth
def create_my_product():
    """供应商录入商品（含SKU规格），一个事务完成商品和SKU的创建。"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response('商品名称为必填项', 400)
    if not data.get('skus') or not isinstance(data['skus'], list) or len(data['skus']) == 0:
        return error_response('至少需要添加一个SKU规格', 400)

    # 校验每个 SKU
    for idx, sku in enumerate(data['skus']):
        if not sku.get('sku_code'):
            return error_response(f'第{idx + 1}个SKU的编码为必填项', 400)
        if sku.get('price') is None:
            return error_response(f'第{idx + 1}个SKU的价格为必填项', 400)

    session = db.get_session()
    try:
        supplier = _get_supplier_by_user(session, user_id)
        if not supplier:
            return error_response('当前用户未关联供应商账号', 404)
        if supplier[6] != 'approved':
            return error_response('供应商资质未审核通过，无法录入商品', 403)
        supplier_id = supplier[0]

        # 创建商品
        specs = json.dumps(data.get('specs', {}), ensure_ascii=False)
        images = json.dumps(data.get('images', []), ensure_ascii=False)
        result = session.execute(
            text("""INSERT INTO products (name, category_id, supplier_id, specs, unit, description, images, status)
               VALUES (:name, :category_id, :supplier_id, :specs, :unit, :description, :images, :status) RETURNING id"""),
            {
                'name': data['name'],
                'category_id': data.get('category_id'),
                'supplier_id': supplier_id,
                'specs': specs,
                'unit': data.get('unit'),
                'description': data.get('description'),
                'images': images,
                'status': data.get('status', 'active'),
            }
        )
        product_id = result.fetchone()[0]

        # 创建 SKU 列表
        created_skus = []
        for sku in data['skus']:
            sku_attrs = json.dumps(sku.get('attributes', {}), ensure_ascii=False)
            result = session.execute(
                text("""INSERT INTO product_skus (product_id, sku_code, attributes, price, original_price, stock, min_order_qty, status)
                   VALUES (:product_id, :sku_code, :attributes, :price, :original_price, :stock, :min_order_qty, :status) RETURNING id"""),
                {
                    'product_id': product_id,
                    'sku_code': sku['sku_code'],
                    'attributes': sku_attrs,
                    'price': sku['price'],
                    'original_price': sku.get('original_price'),
                    'stock': sku.get('stock', 0),
                    'min_order_qty': sku.get('min_order_qty', 1),
                    'status': sku.get('status', 'active'),
                }
            )
            created_skus.append({'id': result.fetchone()[0], 'sku_code': sku['sku_code']})

        session.commit()
        logger.info(f"供应商(user_id={user_id}, supplier_id={supplier_id})录入商品 product_id={product_id}, sku_count={len(created_skus)}")
        return success_response({'product_id': product_id, 'skus': created_skus}, '商品录入成功', 201)
    except Exception as e:
        session.rollback()
        logger.error(f"供应商录入商品失败: {e}")
        return error_response(str(e), 500)
    finally:
        session.close()


@suppliers_bp.route('/me/products/<int:product_id>', methods=['PUT'])
@require_auth
def update_my_product(product_id):
    """供应商更新自己的商品信息。"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    if not data:
        return error_response('未提供更新数据', 400)

    session = db.get_session()
    try:
        supplier = _get_supplier_by_user(session, user_id)
        if not supplier:
            return error_response('当前用户未关联供应商账号', 404)
        supplier_id = supplier[0]

        # 校验商品归属
        result = session.execute(
            text("SELECT id FROM products WHERE id = :product_id AND supplier_id = :supplier_id"),
            {'product_id': product_id, 'supplier_id': supplier_id}
        )
        if not result.fetchone():
            return error_response('商品不存在或无权操作', 404)

        fields = []
        params = {'product_id': product_id}
        for key in ['name', 'category_id', 'unit', 'description', 'status']:
            if key in data:
                fields.append(f"{key} = :{key}")
                params[key] = data[key]
        if 'specs' in data:
            fields.append("specs = :specs")
            params['specs'] = json.dumps(data['specs'], ensure_ascii=False)
        if 'images' in data:
            fields.append("images = :images")
            params['images'] = json.dumps(data['images'], ensure_ascii=False)

        if not fields:
            return error_response('没有需要更新的字段', 400)

        fields.append("updated_at = NOW()")
        session.execute(
            text(f"UPDATE products SET {', '.join(fields)} WHERE id = :product_id"),
            params
        )
        session.commit()
        return success_response(message='商品更新成功')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@suppliers_bp.route('/me/products/<int:product_id>/skus', methods=['POST'])
@require_auth
def add_product_sku(product_id):
    """供应商为已有商品追加 SKU 规格。"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    if not data or not data.get('sku_code') or data.get('price') is None:
        return error_response('SKU编码和价格为必填项', 400)

    session = db.get_session()
    try:
        supplier = _get_supplier_by_user(session, user_id)
        if not supplier:
            return error_response('当前用户未关联供应商账号', 404)
        supplier_id = supplier[0]

        # 校验商品归属
        result = session.execute(
            text("SELECT id FROM products WHERE id = :product_id AND supplier_id = :supplier_id"),
            {'product_id': product_id, 'supplier_id': supplier_id}
        )
        if not result.fetchone():
            return error_response('商品不存在或无权操作', 404)

        sku_attrs = json.dumps(data.get('attributes', {}), ensure_ascii=False)
        result = session.execute(
            text("""INSERT INTO product_skus (product_id, sku_code, attributes, price, original_price, stock, min_order_qty, status)
               VALUES (:product_id, :sku_code, :attributes, :price, :original_price, :stock, :min_order_qty, :status) RETURNING id"""),
            {
                'product_id': product_id,
                'sku_code': data['sku_code'],
                'attributes': sku_attrs,
                'price': data['price'],
                'original_price': data.get('original_price'),
                'stock': data.get('stock', 0),
                'min_order_qty': data.get('min_order_qty', 1),
                'status': data.get('status', 'active'),
            }
        )
        sku_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': sku_id}, 'SKU添加成功', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
