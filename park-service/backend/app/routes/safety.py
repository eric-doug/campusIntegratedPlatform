from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

safety_bp = Blueprint('safety', __name__)


@safety_bp.route('', methods=['GET'])
def list_safety():
    enterprise_id = request.args.get('enterprise_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        query = "SELECT id, enterprise_id, type, incident_date, description, severity, measures, status, created_at FROM safety_records WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM safety_records WHERE 1=1"
        params = []
        if enterprise_id:
            query += " AND enterprise_id = %s"
            count_query += " AND enterprise_id = %s"
            params.append(enterprise_id)
        total = session.execute(count_query, params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        results = session.execute(query, params).fetchall()
        items = [{
            'id': r[0], 'enterprise_id': r[1], 'type': r[2],
            'incident_date': r[3].isoformat() if r[3] else None,
            'description': r[4], 'severity': r[5], 'measures': r[6], 'status': r[7],
            'created_at': r[8].isoformat() if r[8] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@safety_bp.route('', methods=['POST'])
@require_auth
def create_safety():
    data = request.get_json()
    if not data or not data.get('enterprise_id') or not data.get('type'):
        return error_response('enterprise_id and type are required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            "INSERT INTO safety_records (enterprise_id, type, incident_date, description, severity, measures, status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (data['enterprise_id'], data['type'], data.get('incident_date'),
             data.get('description'), data.get('severity'), data.get('measures'), data.get('status', 'pending'))
        )
        record_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': record_id}, 'Safety record created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
