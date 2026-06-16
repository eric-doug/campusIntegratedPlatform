import request from './request'

export function getProducts(params) {
  return request.get('/industrial/products', { params })
}

export function getProduct(id) {
  return request.get(`/industrial/products/${id}`)
}

export function createProduct(data) {
  return request.post('/industrial/products', data)
}

export function updateProduct(id, data) {
  return request.put(`/industrial/products/${id}`, data)
}

export function deleteProduct(id) {
  return request.delete(`/industrial/products/${id}`)
}
