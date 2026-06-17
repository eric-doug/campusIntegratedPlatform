from flask import Blueprint, request
from sqlalchemy import text
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
        params = {}
        if enterprise_id:
            query += " AND enterprise_id = :enterprise_id"
            count_query += " AND enterprise_id = :enterprise_id"
            params['enterprise_id'] = enterprise_id
        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        results = session.execute(text(query), params).fetchall()
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
            text("INSERT INTO safety_records (enterprise_id, type, incident_date, description, severity, measures, status) VALUES (:enterprise_id, :type, :incident_date, :description, :severity, :measures, :status) RETURNING id"),
            {'enterprise_id': data['enterprise_id'], 'type': data['type'], 'incident_date': data.get('incident_date'),
             'description': data.get('description'), 'severity': data.get('severity'), 'measures': data.get('measures'), 'status': data.get('status', 'pending')}
        )
        record_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': record_id}, 'Safety record created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
