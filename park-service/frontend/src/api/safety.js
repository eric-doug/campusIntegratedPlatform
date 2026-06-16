import request from './request'
export const getSafetyRecords = (params) => request.get('/park/safety', { params })
export const createSafetyRecord = (data) => request.post('/park/safety', data)
