import request from './request'
export const getWarehouses = (params) => request.get('/supply/warehouses', { params })
export const createWarehouse = (data) => request.post('/supply/warehouses', data)
