from flask import Blueprint, request, Response, stream_with_context
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.auth.decorators import require_auth
from shared.ai_service.client import AIClient
from shared.ai_service.tasks import AITaskRunner
from shared.utils.response import success_response, error_response

ai_bp = Blueprint('ai', __name__)
ai_runner = AITaskRunner()


@ai_bp.route('/search', methods=['POST'])
def smart_search():
    """AI-powered smart search - convert natural language to structured query."""
    data = request.get_json()
    if not data or not data.get('query'):
        return error_response('Search query is required', 400)

    result = ai_runner.smart_search(data['query'])
    return success_response(result)


@ai_bp.route('/recommend', methods=['POST'])
@require_auth
def recommend_products():
    """AI-powered product recommendations."""
    data = request.get_json()
    user_id = request.current_user['user_id']

    result = ai_runner.recommend_products(
        purchase_history=json.dumps(data.get('purchase_history', [])),
        browse_history=json.dumps(data.get('browse_history', [])),
        current_product=json.dumps(data.get('current_product', {})),
    )
    return success_response({'recommendation': result})


@ai_bp.route('/inquiry-match', methods=['POST'])
@require_auth
def inquiry_match():
    """AI-powered inquiry supplier matching."""
    data = request.get_json()
    if not data or not data.get('inquiry'):
        return error_response('Inquiry data is required', 400)

    result = ai_runner.match_inquiry(
        inquiry=json.dumps(data['inquiry']),
        suppliers=json.dumps(data.get('suppliers', [])),
    )
    return success_response(result)


@ai_bp.route('/risk-analysis', methods=['POST'])
@require_auth
def risk_analysis():
    """AI-powered supplier risk analysis."""
    data = request.get_json()
    if not data or not data.get('supplier_id'):
        return error_response('Supplier ID is required', 400)

    result = ai_runner.analyze_risk(
        supplier_info=json.dumps(data.get('supplier_info', {})),
        transactions=json.dumps(data.get('transactions', [])),
    )
    return success_response(result)


@ai_bp.route('/chat', methods=['POST'])
@require_auth
def ai_chat():
    """General AI chat with streaming support."""
    data = request.get_json()
    if not data or not data.get('message'):
        return error_response('Message is required', 400)

    stream = data.get('stream', False)
    client = AIClient()
    messages = [{'role': 'user', 'content': data['message']}]

    if stream:
        def generate():
            for chunk in client.chat_stream(messages):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    result = client.chat(messages)
    return success_response({'reply': result})
