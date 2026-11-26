import axios from 'axios'

// 开发环境走 Vite 代理（/api -> FastAPI），生产环境可用 VITE_API_BASE_URL 覆盖
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

export default client
