import request from './request'
export const getShipments = (params) => request.get('/supply/shipments', { params })
export const getShipment = (id) => request.get(`/supply/shipments/${id}`)
