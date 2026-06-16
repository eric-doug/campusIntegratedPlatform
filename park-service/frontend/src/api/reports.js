import request from './request'
export const getReportTemplates = () => request.get('/park/reports/templates')
export const createReportTemplate = (data) => request.post('/park/reports/templates', data)
export const getReports = (params) => request.get('/park/reports', { params })
export const createReport = (data) => request.post('/park/reports', data)
export const updateReport = (id, data) => request.put(`/park/reports/${id}`, data)
