import request from './request'

export function getCategories() {
  return request.get('/industrial/categories')
}

export function createCategory(data) {
  return request.post('/industrial/categories', data)
}
