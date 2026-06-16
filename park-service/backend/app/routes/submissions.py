from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.database.db import db
from shared.utils.response import success_response, error_response, paginate_response

submissions_bp = Blueprint('submissions', __name__)


@submissions_bp.route('', methods=['GET'])
def list_submissions():
    form_id = request.args.get('form_id', type=int)
    department = request.args.get('department')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    session = db.get_session()
    try:
        query = "SELECT id, form_id, department, status, submitted_at, feedback, reviewed_at FROM submissions WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM submissions WHERE 1=1"
        params = []
        if form_id:
            query += " AND form_id = %s"
            count_query += " AND form_id = %s"
            params.append(form_id)
        if department:
            query += " AND department = %s"
            count_query += " AND department = %s"
            params.append(department)
        total = session.execute(count_query, params).fetchone()[0]
        query += " ORDER BY submitted_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        results = session.execute(query, params).fetchall()
        items = [{
            'id': r[0], 'form_id': r[1], 'department': r[2], 'status': r[3],
            'submitted_at': r[4].isoformat() if r[4] else None,
            'feedback': r[5], 'reviewed_at': r[6].isoformat() if r[6] else None,
        } for r in results]
        return paginate_response(items, total, page, per_page)
    finally:
        session.close()


@submissions_bp.route('', methods=['POST'])
@require_auth
def create_submission():
    data = request.get_json()
    if not data or not data.get('form_id') or not data.get('department'):
        return error_response('form_id and department are required', 400)
    session = db.get_session()
    try:
        # Create submission
        result = session.execute(
            "INSERT INTO submissions (form_id, department, status) VALUES (%s, %s, 'submitted') RETURNING id",
            (data['form_id'], data['department'])
        )
        submission_id = result.fetchone()[0]
        # Update form status
        session.execute(
            "UPDATE report_forms SET status = 'submitted', submitted_at = NOW() WHERE id = %s",
            (data['form_id'],)
        )
        session.commit()
        return success_response({'id': submission_id}, 'Submission created', 201)
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()


@submissions_bp.route('/<int:submission_id>/review', methods=['POST'])
@require_auth
def review_submission(submission_id):
    data = request.get_json()
    if not data or not data.get('action'):
        return error_response('Review action is required', 400)
    session = db.get_session()
    try:
        session.execute(
            "UPDATE submissions SET status = %s, feedback = %s, reviewed_at = NOW() WHERE id = %s",
            (data['action'], data.get('feedback'), submission_id)
        )
        session.commit()
        return success_response(message=f'Submission {data["action"]}')
    except Exception as e:
        session.rollback()
        return error_response(str(e), 500)
    finally:
        session.close()
