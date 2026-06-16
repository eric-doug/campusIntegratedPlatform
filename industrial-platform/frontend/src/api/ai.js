import request from './request'

export function smartSearch(query) {
  return request.post('/industrial/ai/search', { query })
}

export function getRecommendations(data) {
  return request.post('/industrial/ai/recommend', data)
}

export function inquiryMatch(data) {
  return request.post('/industrial/ai/inquiry-match', data)
}

export function riskAnalysis(data) {
  return request.post('/industrial/ai/risk-analysis', data)
}

export function aiChat(data) {
  return request.post('/industrial/ai/chat', data)
}
