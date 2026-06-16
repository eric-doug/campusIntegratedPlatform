import request from './request'
export const getInventory = (params) => request.get('/supply/inventory', { params })
export const getInventorySummary = () => request.get('/supply/inventory/summary')
