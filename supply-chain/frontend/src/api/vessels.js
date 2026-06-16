import request from './request'
export const getVessels = (params) => request.get('/supply/vessels', { params })
export const getVessel = (id) => request.get(`/supply/vessels/${id}`)
export const createVessel = (data) => request.post('/supply/vessels', data)
