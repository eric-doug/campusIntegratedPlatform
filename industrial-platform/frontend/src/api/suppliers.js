import request from './request'

export function getSuppliers(params) {
  return request.get('/industrial/suppliers', { params })
}

export function createSupplier(data) {
  return request.post('/industrial/suppliers', data)
}

export function auditSupplier(id, data) {
  return request.post(`/industrial/suppliers/${id}/audit`, data)
}
