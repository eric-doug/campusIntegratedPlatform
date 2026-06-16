from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

emission_bp = Blueprint('emission', __name__)


@emission_bp.route('', methods=['GET'])
def list_emission():
    enterprise_id = request.args.get('enterprise_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        query = "SELECT id, enterprise_id, type, period, value, limit_value, unit, is_exceeding, created_at FROM emission_records WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM emission_records WHERE 1=1"
        params = []
        if enterprise_id:
            query += " AND enterprise_id = %s"
            count_query += " AND enterprise_id = %s"
            params.append(enterprise_id)
        total = session.execute(count_query, params).fetchone()[0]
        query += " ORDER BY period DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        results = session.execute(query, params).fetchall()
        items = [{
            'id': r[0], 'enterprise_id': r[1], 'type': r[2],
            'period': r[3].isoformat() if r[3] else None,
            'value': float(r[4]) if r[4] else None,
            'limit_value': float(r[5]) if r[5] else None,
            'unit': r[6], 'is_exceeding': r[7],
            'created_at': r[8].isoformat() if r[8] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@emission_bp.route('', methods=['POST'])
@require_auth
def create_emission():
    data = request.get_json()
    if not data or not data.get('enterprise_id') or not data.get('type') or not data.get('period'):
        return error_response('enterprise_id, type and period are required', 400)
    is_exceeding = data.get('value', 0) > data.get('limit_value', float('inf'))
    session = db.get_session()
    try:
        result = session.execute(
            "INSERT INTO emission_records (enterprise_id, type, period, value, limit_value, unit, is_exceeding) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (data['enterprise_id'], data['type'], data['period'], data['value'],
             data.get('limit_value'), data.get('unit'), is_exceeding)
        )
        record_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': record_id}, 'Emission record created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
