import request from './request'
export const getEnterprises = (params) => request.get('/park/enterprises', { params })
export const getEnterprise = (id) => request.get(`/park/enterprises/${id}`)
export const createEnterprise = (data) => request.post('/park/enterprises', data)
