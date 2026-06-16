import request from './request'
export const inventoryForecast = (data) => request.post('/supply/ai/inventory-forecast', data)
export const logisticsOptimize = (data) => request.post('/supply/ai/logistics-optimize', data)
