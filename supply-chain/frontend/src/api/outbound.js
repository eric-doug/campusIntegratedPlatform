import request from './request'
export const getOutboundOrders = (params) => request.get('/supply/outbound', { params })
export const createOutboundOrder = (data) => request.post('/supply/outbound', data)
