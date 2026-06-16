import request from './request'

export function getOrders(params) {
  return request.get('/industrial/orders', { params })
}

export function getOrder(id) {
  return request.get(`/industrial/orders/${id}`)
}

export function createOrder(data) {
  return request.post('/industrial/orders', data)
}
