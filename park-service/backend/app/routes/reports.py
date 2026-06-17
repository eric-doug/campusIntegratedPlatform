from flask import Blueprint, request
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/templates', methods=['GET'])
def list_templates():
    session = db.get_session()
    try:
        result = session.execute(
            text("SELECT id, name, department, format_config, period_type, status, created_at FROM report_templates WHERE status = 'active' ORDER BY created_at DESC")
        ).fetchall()
        items = [{
            'id': r[0], 'name': r[1], 'department': r[2], 'format_config': r[3],
            'period_type': r[4], 'status': r[5],
            'created_at': r[6].isoformat() if r[6] else None,
        } for r in result]
        return success_response(items)
    finally:
        session.close()


@reports_bp.route('/templates', methods=['POST'])
@require_auth
def create_template():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('department'):
        return error_response('Name and department are required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO report_templates (name, department, format_config, period_type, status) VALUES (:name, :department, :format_config, :period_type, :status) RETURNING id"),
            {'name': data['name'], 'department': data['department'], 'format_config': data.get('format_config', {}), 'period_type': data.get('period_type', 'monthly'), 'status': data.get('status', 'active')}
        )
        template_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': template_id}, 'Template created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@reports_bp.route('', methods=['GET'])
def list_reports():
    enterprise_id = request.args.get('enterprise_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        query = "SELECT rf.id, rf.enterprise_id, rf.template_id, rf.period, rf.data, rf.status, rf.submitted_at, rf.created_at, rt.name as template_name FROM report_forms rf LEFT JOIN report_templates rt ON rf.template_id = rt.id WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM report_forms rf WHERE 1=1"
        params = {}
        if enterprise_id:
            query += " AND rf.enterprise_id = :enterprise_id"
            count_query += " AND enterprise_id = :enterprise_id"
            params['enterprise_id'] = enterprise_id
        total = session.execute(text(count_query), params).fetchone()[0]
        query += " ORDER BY rf.created_at DESC LIMIT :limit OFFSET :offset"
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        results = session.execute(text(query), params).fetchall()
        items = [{
            'id': r[0], 'enterprise_id': r[1], 'template_id': r[2], 'period': r[3],
            'data': r[4], 'status': r[5],
            'submitted_at': r[6].isoformat() if r[6] else None,
            'created_at': r[7].isoformat() if r[7] else None,
            'template_name': r[8],
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@reports_bp.route('', methods=['POST'])
@require_auth
def create_report():
    data = request.get_json()
    if not data or not data.get('enterprise_id') or not data.get('template_id'):
        return error_response('enterprise_id and template_id are required', 400)
    session = db.get_session()
    try:
        result = session.execute(
            text("INSERT INTO report_forms (enterprise_id, template_id, period, data, status) VALUES (:enterprise_id, :template_id, :period, :data, :status) RETURNING id"),
            {'enterprise_id': data['enterprise_id'], 'template_id': data['template_id'], 'period': data.get('period', ''), 'data': data.get('data', {}), 'status': data.get('status', 'draft')}
        )
        form_id = result.fetchone()[0]
        session.commit()
        return success_response({'id': form_id}, 'Report form created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@reports_bp.route('/<int:form_id>', methods=['PUT'])
@require_auth
def update_report(form_id):
    data = request.get_json()
    session = db.get_session()
    try:
        fields = []
        params = {'form_id': form_id}
        for key in ['period', 'data', 'status']:
            if key in data:
                fields.append(f"{key} = :{key}")
                params[key] = data[key]
        if not fields:
            return error_response('No fields to update', 400)
        session.execute(text(f"UPDATE report_forms SET {', '.join(fields)}, updated_at = NOW() WHERE id = :form_id"), params)
        session.commit()
        return success_response(message='Report form updated')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
