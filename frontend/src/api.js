import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://teamify.pro/api',
})

// Автоматически добавляем токен к каждому запросу
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('user_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обрабатываем 401 — автоматический logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('user_token')
      router.push({ name: 'home' })
    }
    return Promise.reject(error)
  },
)

export default api
