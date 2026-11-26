import axios from 'axios'

// 开发环境走 Vite 代理（/api -> FastAPI），生产环境可用 VITE_API_BASE_URL 覆盖
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 20000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('wdr_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('wdr_token')
      localStorage.removeItem('wdr_user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default client
