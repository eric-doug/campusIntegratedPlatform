import json
from flask import Blueprint, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.ai_service.tasks import AITaskRunner
from shared.utils.response import success_response, error_response

ai_bp = Blueprint('ai', __name__)
ai_runner = AITaskRunner()


@ai_bp.route('/inventory-forecast', methods=['POST'])
@require_auth
def inventory_forecast():
    data = request.get_json()
    result = ai_runner.forecast_inventory(
        history=json.dumps(data.get('history', [])),
        current_inventory=json.dumps(data.get('current_inventory', {})),
        seasonal_factors=json.dumps(data.get('seasonal_factors', '')),
    )
    return success_response({'forecast': result})


@ai_bp.route('/logistics-optimize', methods=['POST'])
@require_auth
def logistics_optimize():
    data = request.get_json()
    result = ai_runner.optimize_logistics(
        shipment_info=json.dumps(data.get('shipment_info', {})),
        routes=json.dumps(data.get('routes', [])),
        vessel_data=json.dumps(data.get('vessel_data', [])),
    )
    return success_response({'optimization': result})
