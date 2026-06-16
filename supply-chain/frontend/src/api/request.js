import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({ baseURL: '/api', timeout: 30000 })

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
}, (error) => Promise.reject(error))

request.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.code === 200 || data.code === 201) return data
    ElMessage.error(data.message || 'Request failed')
    return Promise.reject(new Error(data.message))
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      router.push('/login')
    } else {
      ElMessage.error(error.response?.data?.message || 'Network error')
    }
    return Promise.reject(error)
  }
)

export default request
