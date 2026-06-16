import json
from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.ai_service.tasks import AITaskRunner
from shared.utils.response import success_response, error_response

ai_bp = Blueprint('ai', __name__)
ai_runner = AITaskRunner()


@ai_bp.route('/auto-fill', methods=['POST'])
@require_auth
def auto_fill():
    data = request.get_json()
    if not data or not data.get('template_id'):
        return error_response('template_id is required', 400)
    result = ai_runner.auto_fill_report(
        enterprise_data=json.dumps(data.get('enterprise_data', {})),
        template=json.dumps(data.get('template', {})),
        period=data.get('period', ''),
    )
    return success_response(result)


@ai_bp.route('/compliance-check', methods=['POST'])
@require_auth
def compliance_check():
    data = request.get_json()
    if not data or not data.get('enterprise_id'):
        return error_response('enterprise_id is required', 400)
    result = ai_runner.check_compliance(
        enterprise_data=json.dumps(data.get('enterprise_data', {})),
        policy_standards=json.dumps(data.get('policy_standards', {})),
    )
    return success_response(result)


@ai_bp.route('/report-generate', methods=['POST'])
@require_auth
def report_generate():
    data = request.get_json()
    if not data or not data.get('enterprise_id'):
        return error_response('enterprise_id is required', 400)
    result = ai_runner.generate_report(
        enterprise_data=json.dumps(data.get('enterprise_data', {})),
        report_type=data.get('report_type', 'comprehensive'),
        time_range=data.get('time_range', ''),
    )
    return success_response({'report': result})
