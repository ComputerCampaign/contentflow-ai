import api from './index'

export default {
  // 设置认证头
  setAuthHeader(token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },
  
  // 移除认证头
  removeAuthHeader() {
    delete api.defaults.headers.common['Authorization']
  },
  
  // 用户注册
  register(userData) {
    return api.post('/auth/register', userData)
  },
  
  // 用户登录
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  
  // 获取当前用户信息
  getUserInfo() {
    return api.get('/auth/me')
  }
}