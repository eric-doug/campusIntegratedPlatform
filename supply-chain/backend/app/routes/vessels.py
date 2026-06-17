from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

vessels_bp = Blueprint('vessels', __name__)


@vessels_bp.route('', methods=['GET'])
def list_vessels():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    port = request.args.get('port')
    session = db.get_session()
    try:
        query = "SELECT id, vessel_name, imo, port, eta, ata, berth_status, cargo_progress, raw_data, updated_at FROM vessel_dynamics WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM vessel_dynamics WHERE 1=1"
        params = {}
        if port:
            query += " AND port = :port"
            count_query += " AND port = :port"
            params['port'] = port
        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY updated_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'vessel_name': r[1], 'imo': r[2], 'port': r[3],
            'eta': r[4].isoformat() if r[4] else None, 'ata': r[5].isoformat() if r[5] else None,
            'berth_status': r[6], 'cargo_progress': float(r[7]) if r[7] else None,
            'raw_data': r[8], 'updated_at': r[9].isoformat() if r[9] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@vessels_bp.route('', methods=['POST'])
@require_auth
def create_vessel():
    data = request.get_json()
    if not data or not data.get('vessel_name'):
        return error_response('Vessel name is required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO vessel_dynamics (vessel_name, imo, port, eta, berth_status, cargo_progress, raw_data) VALUES (:vessel_name, :imo, :port, :eta, :berth_status, :cargo_progress, :raw_data) RETURNING id"),
            {'vessel_name': data['vessel_name'], 'imo': data.get('imo'), 'port': data.get('port'), 'eta': data.get('eta'),
             'berth_status': data.get('berth_status'), 'cargo_progress': data.get('cargo_progress', 0), 'raw_data': str(data.get('raw_data', {}))}
        )
        vessel_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': vessel_id}, 'Vessel record created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@vessels_bp.route('/<int:vessel_id>', methods=['GET'])
def get_vessel(vessel_id):
    session = db.get_session()
    try:
        result = session.execute(
            text("SELECT id, vessel_name, imo, port, eta, ata, berth_status, cargo_progress, raw_data, updated_at FROM vessel_dynamics WHERE id = :vessel_id"),
            {'vessel_id': vessel_id}
        ).fetchone()
        if not result:
            return error_response('Vessel not found', 404)
        return success_response({
            'id': result[0], 'vessel_name': result[1], 'imo': result[2], 'port': result[3],
            'eta': result[4].isoformat() if result[4] else None,
            'ata': result[5].isoformat() if result[5] else None,
            'berth_status': result[6], 'cargo_progress': float(result[7]) if result[7] else None,
            'raw_data': result[8], 'updated_at': result[9].isoformat() if result[9] else None,
        })
    finally:
        session.close()
