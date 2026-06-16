import request from './request'
export const autoFill = (data) => request.post('/park/ai/auto-fill', data)
export const complianceCheck = (data) => request.post('/park/ai/compliance-check', data)
export const generateReport = (data) => request.post('/park/ai/report-generate', data)
