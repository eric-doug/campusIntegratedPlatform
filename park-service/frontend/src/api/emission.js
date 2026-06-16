import request from './request'
export const getEmissionRecords = (params) => request.get('/park/emission', { params })
export const createEmissionRecord = (data) => request.post('/park/emission', data)
