import request from './request'

export function getInquiries(params) {
  return request.get('/industrial/inquiries', { params })
}

export function getInquiry(id) {
  return request.get(`/industrial/inquiries/${id}`)
}

export function createInquiry(data) {
  return request.post('/industrial/inquiries', data)
}
