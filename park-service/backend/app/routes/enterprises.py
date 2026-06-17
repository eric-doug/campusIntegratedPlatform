from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

enterprises_bp = Blueprint('enterprises', __name__)


@enterprises_bp.route('', methods=['GET'])
def list_enterprises():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    session = db.get_session()
    try:
        query = "SELECT id, name, unified_code, contact_person, contact_phone, address, industry, status, created_at FROM enterprises WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM enterprises WHERE 1=1"
        params = {}
        if keyword:
            query += " AND (name ILIKE :keyword1 OR unified_code ILIKE :keyword2)"
            count_query += " AND (name ILIKE :keyword1 OR unified_code ILIKE :keyword2)"
            params['keyword1'] = f'%{keyword}%'
            params['keyword2'] = f'%{keyword}%'
        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'unified_code': r[2], 'contact_person': r[3],
            'contact_phone': r[4], 'address': r[5], 'industry': r[6], 'status': r[7],
            'created_at': r[8].isoformat() if r[8] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@enterprises_bp.route('', methods=['POST'])
@require_auth
def create_enterprise():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('unified_code'):
        return error_response('Name and unified_code are required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO enterprises (name, unified_code, contact_person, contact_phone, address, industry, status) VALUES (:name, :unified_code, :contact_person, :contact_phone, :address, :industry, :status) RETURNING id"),
            {'name': data['name'], 'unified_code': data['unified_code'], 'contact_person': data.get('contact_person'), 'contact_phone': data.get('contact_phone'),
             'address': data.get('address'), 'industry': data.get('industry'), 'status': data.get('status', 'active')}
        )
        enterprise_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': enterprise_id}, 'Enterprise created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@enterprises_bp.route('/<int:enterprise_id>', methods=['GET'])
def get_enterprise(enterprise_id):
    session = db.get_session()
    try:
        result = session.execute(
            text("SELECT id, name, unified_code, contact_person, contact_phone, address, industry, status, created_at FROM enterprises WHERE id = :id"),
            {'id': enterprise_id}
        ).fetchone()
        if not result:
            return error_response('Enterprise not found', 404)
        return success_response({
            'id': result[0], 'name': result[1], 'unified_code': result[2],
            'contact_person': result[3], 'contact_phone': result[4],
            'address': result[5], 'industry': result[6], 'status': result[7],
            'created_at': result[8].isoformat() if result[8] else None,
        })
    finally:
        session.close()
