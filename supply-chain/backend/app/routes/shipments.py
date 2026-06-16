from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

shipments_bp = Blueprint('shipments', __name__)


@shipments_bp.route('', methods=['GET'])
def list_shipments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    session = db.get_session()
    try:
        query = "SELECT id, tracking_no, origin, destination, carrier, status, current_location, eta, actual_arrival, created_at FROM shipments WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM shipments WHERE 1=1"
        params = []
        if status:
            query += " AND status = %s"
            count_query += " AND status = %s"
            params.append(status)
        total = session.execute(count_query, params).fetchone()[0]
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        results = session.execute(query, params).fetchall()
        items = [{
            'id': r[0], 'tracking_no': r[1], 'origin': r[2], 'destination': r[3],
            'carrier': r[4], 'status': r[5], 'current_location': r[6],
            'eta': r[7].isoformat() if r[7] else None,
            'actual_arrival': r[8].isoformat() if r[8] else None,
            'created_at': r[9].isoformat() if r[9] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@shipments_bp.route('/<int:shipment_id>', methods=['GET'])
def get_shipment(shipment_id):
    session = db.get_session()
    try:
        result = session.execute(
            "SELECT id, tracking_no, origin, destination, carrier, status, current_location, eta, actual_arrival, created_at FROM shipments WHERE id = %s",
            (shipment_id,)
        ).fetchone()
        if not result:
            return error_response('Shipment not found', 404)
        return success_response({
            'id': result[0], 'tracking_no': result[1], 'origin': result[2],
            'destination': result[3], 'carrier': result[4], 'status': result[5],
            'current_location': result[6],
            'eta': result[7].isoformat() if result[7] else None,
            'actual_arrival': result[8].isoformat() if result[8] else None,
            'created_at': result[9].isoformat() if result[9] else None,
        })
    finally:
        session.close()
