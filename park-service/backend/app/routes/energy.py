from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

energy_bp = Blueprint('energy', __name__)


@energy_bp.route('', methods=['GET'])
def list_energy():
    enterprise_id = request.args.get('enterprise_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        query = "SELECT id, enterprise_id, type, period, value, unit, reported, created_at FROM energy_consumption WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM energy_consumption WHERE 1=1"
        params = {}
        if enterprise_id:
            query += " AND enterprise_id = :enterprise_id"
            count_query += " AND enterprise_id = :enterprise_id"
            params['enterprise_id'] = enterprise_id
        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY period DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'enterprise_id': r[1], 'type': r[2],
            'period': r[3].isoformat() if r[3] else None,
            'value': float(r[4]) if r[4] else None, 'unit': r[5], 'reported': r[6],
            'created_at': r[7].isoformat() if r[7] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@energy_bp.route('', methods=['POST'])
@require_auth
def create_energy():
    data = request.get_json()
    if not data or not data.get('enterprise_id') or not data.get('type') or not data.get('period'):
        return error_response('enterprise_id, type and period are required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO energy_consumption (enterprise_id, type, period, value, unit, reported) VALUES (:enterprise_id, :type, :period, :value, :unit, :reported) RETURNING id"),
            {'enterprise_id': data['enterprise_id'], 'type': data['type'], 'period': data['period'], 'value': data['value'],
             'unit': data.get('unit'), 'reported': data.get('reported', False)}
        )
        record_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': record_id}, 'Energy record created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
