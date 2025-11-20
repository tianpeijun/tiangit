import axios from 'axios'
import { Message } from 'element-ui'
import router from '../router'

const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api',
  timeout: 30000
})

// Request interceptor
service.interceptors.request.use(
  config => {
    const sessionId = localStorage.getItem('session_id')
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId
    }
    
    const csrfToken = getCookie('csrf_token')
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }
    
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    
    if (res.code === 200) {
      return res.data
    } else {
      Message.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    console.error('Response error:', error)
    
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        Message.error('登录已过期，请重新登录')
        localStorage.removeItem('session_id')
        localStorage.removeItem('user_info')
        // 避免重复导航到当前页面
        if (router.currentRoute.path !== '/login') {
          router.push('/login')
        }
      } else if (status === 403) {
        Message.error('无权限访问')
      } else if (status === 404) {
        Message.error('资源不存在')
      } else if (status === 429) {
        Message.error('请求过于频繁，请稍后再试')
      } else {
        Message.error(data.message || '请求失败')
      }
    } else {
      Message.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

export default service
