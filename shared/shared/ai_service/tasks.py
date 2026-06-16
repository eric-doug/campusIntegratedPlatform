"""AI task scheduling and async execution."""
import logging
from threading import Thread
from .client import AIClient
from .prompts import *

logger = logging.getLogger(__name__)


def _run_async(fn, *args, **kwargs):
    """Run a function in a background thread."""
    thread = Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


class AITaskRunner:
    """Execute AI tasks with prompt templates."""

    def __init__(self):
        self.client = AIClient()

    def smart_search(self, query):
        """Convert natural language to structured search conditions."""
        messages = [{'role': 'user', 'content': PRODUCT_SEARCH_PROMPT.format(query=query)}]
        schema = {
            'type': 'object',
            'properties': {
                'keywords': {'type': 'array', 'items': {'type': 'string'}},
                'category': {'type': 'string'},
                'price_range': {'type': 'object'},
                'specs': {'type': 'object'},
            }
        }
        return self.client.structured_output(messages, schema)

    def recommend_products(self, purchase_history, browse_history, current_product):
        """Generate product recommendations."""
        messages = [{
            'role': 'user',
            'content': PRODUCT_RECOMMEND_PROMPT.format(
                purchase_history=purchase_history,
                browse_history=browse_history,
                current_product=current_product,
            )
        }]
        return self.client.chat(messages)

    def match_inquiry(self, inquiry, suppliers):
        """Match inquiry with suppliers."""
        messages = [{
            'role': 'user',
            'content': INQUIRY_MATCH_PROMPT.format(
                inquiry=inquiry,
                suppliers=suppliers,
            )
        }]
        schema = {
            'type': 'object',
            'properties': {
                'matches': {'type': 'array'},
            }
        }
        return self.client.structured_output(messages, schema)

    def analyze_risk(self, supplier_info, transactions):
        """Analyze supplier risk."""
        messages = [{
            'role': 'user',
            'content': RISK_ANALYSIS_PROMPT.format(
                supplier_info=supplier_info,
                transactions=transactions,
            )
        }]
        schema = {
            'type': 'object',
            'properties': {
                'risk_level': {'type': 'string'},
                'risk_factors': {'type': 'array'},
                'suggestions': {'type': 'array'},
            }
        }
        return self.client.structured_output(messages, schema)

    def forecast_inventory(self, history, current_inventory, seasonal_factors):
        """Forecast inventory demand."""
        messages = [{
            'role': 'user',
            'content': INVENTORY_FORECAST_PROMPT.format(
                history=history,
                current_inventory=current_inventory,
                seasonal_factors=seasonal_factors,
            )
        }]
        return self.client.chat(messages)

    def optimize_logistics(self, shipment_info, routes, vessel_data):
        """Optimize logistics route."""
        messages = [{
            'role': 'user',
            'content': LOGISTICS_OPTIMIZE_PROMPT.format(
                shipment_info=shipment_info,
                routes=routes,
                vessel_data=vessel_data,
            )
        }]
        return self.client.chat(messages)

    def auto_fill_report(self, enterprise_data, template, period):
        """Auto-fill report form."""
        messages = [{
            'role': 'user',
            'content': AUTO_FILL_PROMPT.format(
                enterprise_data=enterprise_data,
                template=template,
                period=period,
            )
        }]
        schema = {
            'type': 'object',
            'properties': {
                'filled_data': {'type': 'object'},
                'confidence': {'type': 'object'},
                'notes': {'type': 'array'},
            }
        }
        return self.client.structured_output(messages, schema)

    def check_compliance(self, enterprise_data, policy_standards):
        """Check compliance with policies."""
        messages = [{
            'role': 'user',
            'content': COMPLIANCE_CHECK_PROMPT.format(
                enterprise_data=enterprise_data,
                policy_standards=policy_standards,
            )
        }]
        schema = {
            'type': 'object',
            'properties': {
                'compliance_status': {'type': 'string'},
                'issues': {'type': 'array'},
                'suggestions': {'type': 'array'},
                'risk_level': {'type': 'string'},
            }
        }
        return self.client.structured_output(messages, schema)

    def generate_report(self, enterprise_data, report_type, time_range):
        """Generate analysis report."""
        messages = [{
            'role': 'user',
            'content': REPORT_GENERATE_PROMPT.format(
                enterprise_data=enterprise_data,
                report_type=report_type,
                time_range=time_range,
            )
        }]
        return self.client.chat(messages, max_tokens=4000)
