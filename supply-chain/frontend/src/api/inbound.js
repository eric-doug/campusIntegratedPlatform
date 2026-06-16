import request from './request'
export const getInboundOrders = (params) => request.get('/supply/inbound', { params })
export const createInboundOrder = (data) => request.post('/supply/inbound', data)
