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

// ==================== 供应商商品录入 ====================

export function getMySupplierProfile() {
  return request.get('/industrial/suppliers/me')
}

export function getMyProducts(params) {
  return request.get('/industrial/suppliers/me/products', { params })
}

export function createMyProduct(data) {
  return request.post('/industrial/suppliers/me/products', data)
}

export function updateMyProduct(id, data) {
  return request.put(`/industrial/suppliers/me/products/${id}`, data)
}

export function addProductSku(productId, data) {
  return request.post(`/industrial/suppliers/me/products/${productId}/skus`, data)
}
