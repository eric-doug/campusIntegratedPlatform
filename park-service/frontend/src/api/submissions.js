import request from './request'
export const getSubmissions = (params) => request.get('/park/submissions', { params })
export const createSubmission = (data) => request.post('/park/submissions', data)
export const reviewSubmission = (id, data) => request.post(`/park/submissions/${id}/review`, data)
