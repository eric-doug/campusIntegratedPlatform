from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

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
        params = []

        if keyword:
            query += " AND (name ILIKE %s OR code ILIKE %s)"
            count_query += " AND (name ILIKE %s OR code ILIKE %s)"
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        if audit_status:
            query += " AND audit_status = %s"
            count_query += " AND audit_status = %s"
            params.append(audit_status)

        total = session.execute(count_query, params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])

        results = session.execute(query, params).fetchall()
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
            """INSERT INTO suppliers (name, code, contact_person, contact_phone, business_license, address, status, audit_status)
               VALUES (%s, %s, %s, %s, %s, %s, 'active', 'pending') RETURNING id""",
            (data['name'], data.get('code'), data.get('contact_person'),
             data.get('contact_phone'), data.get('business_license'), data.get('address'))
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
    """Audit a supplier application."""
    data = request.get_json()
    if not data or not data.get('action'):
        return error_response('Audit action is required', 400)

    action = data['action']  # approved / rejected
    session = db.get_session()
    try:
        session.execute(
            "UPDATE suppliers SET audit_status = %s, audit_remark = %s, updated_at = NOW() WHERE id = %s",
            (action, data.get('remark'), supplier_id)
        )
        session.commit()
        return success_response(message=f'Supplier {action}')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
