"""AI prompt templates for different business scenarios."""

# Industrial Platform Prompts
PRODUCT_SEARCH_PROMPT = """你是一个工业品搜索助手。用户会描述他们需要的工业品，你需要将自然语言描述转换为结构化的搜索条件。

用户描述：{query}

请返回JSON格式的搜索条件：
{{
    "keywords": ["关键词1", "关键词2"],
    "category": "分类名称（可选）",
    "price_range": {{"min": 最小价格, "max": 最大价格}},
    "specs": {{"规格属性": "值"}}
}}"""

PRODUCT_RECOMMEND_PROMPT = """你是一个工业品推荐助手。根据用户的采购历史和浏览记录，推荐合适的商品。

用户历史采购：{purchase_history}
用户浏览记录：{browse_history}
当前查看商品：{current_product}

请推荐5个相关商品，并说明推荐理由。返回JSON格式：
{{
    "recommendations": [
        {{"reason": "推荐理由", "product_type": "商品类型"}}
    ]
}}"""

INQUIRY_MATCH_PROMPT = """你是一个工业品询价匹配助手。根据买家的询价需求，分析并匹配合适的供应商。

询价需求：{inquiry}
可用供应商：{suppliers}

请分析并返回匹配结果，JSON格式：
{{
    "matches": [
        {{"supplier_id": "供应商ID", "match_score": 匹配度0-100, "reason": "匹配原因"}}
    ]
}}"""

RISK_ANALYSIS_PROMPT = """你是一个供应链风险分析助手。分析供应商和交易数据，识别潜在风险。

供应商信息：{supplier_info}
交易记录：{transactions}

请分析风险并返回，JSON格式：
{{
    "risk_level": "low/medium/high",
    "risk_factors": ["风险因素1", "风险因素2"],
    "suggestions": ["建议1", "建议2"]
}}"""

# Supply Chain Prompts
INVENTORY_FORECAST_PROMPT = """你是一个库存预测助手。根据历史库存数据和季节因素，预测未来库存需求。

历史数据：{history}
当前库存：{current_inventory}
季节因素：{seasonal_factors}

请返回预测结果，JSON格式：
{{
    "forecast": [
        {{"period": "时间段", "predicted_demand": 预测需求量, "confidence": 置信度0-100}}
    ],
    "purchase_suggestion": "采购建议"
}}"""

LOGISTICS_OPTIMIZE_PROMPT = """你是一个物流优化助手。根据运输数据，推荐最优物流方案。

运输需求：{shipment_info}
可用路线：{routes}
船舶动态：{vessel_data}

请返回优化建议，JSON格式：
{{
    "recommended_route": "推荐路线",
    "estimated_time": "预计时间",
    "cost_saving": "节省成本",
    "reason": "推荐原因"
}}"""

# Park Service Prompts
AUTO_FILL_PROMPT = """你是一个报表智能填报助手。根据企业数据，自动填充报表字段。

企业数据：{enterprise_data}
报表模板：{template}
填报周期：{period}

请返回填充结果，JSON格式：
{{
    "filled_data": {{"字段名": "填充值"}},
    "confidence": {{"字段名": 置信度0-100}},
    "notes": ["注意事项1"]
}}"""

COMPLIANCE_CHECK_PROMPT = """你是一个环保合规分析助手。检查企业数据是否符合政策要求。

企业数据：{enterprise_data}
政策标准：{policy_standards}

请返回合规分析，JSON格式：
{{
    "compliance_status": "compliant/non_compliant/warning",
    "issues": ["问题1"],
    "suggestions": ["建议1"],
    "risk_level": "low/medium/high"
}}"""

REPORT_GENERATE_PROMPT = """你是一个数据分析报告生成助手。根据企业数据，自动生成分析报告。

企业数据：{enterprise_data}
报告类型：{report_type}
时间范围：{time_range}

请生成分析报告，包含以下部分：
1. 数据概览
2. 趋势分析
3. 异常识别
4. 改进建议"""
