import request from './request'
export const getEnergyRecords = (params) => request.get('/park/energy', { params })
export const createEnergyRecord = (data) => request.post('/park/energy', data)
