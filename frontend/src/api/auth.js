import request from '@/utils/request'

// 认证相关API接口
export const authAPI = {
  // 用户登录
  login(data) {
    return request.post('/auth/login', data)
  },

  // 用户注册
  register(data) {
    return request.post('/auth/register', data)
  },

  // 刷新token
  refreshToken() {
    return request.post('/auth/refresh')
  },

  // 用户登出
  logout() {
    return request.post('/auth/logout')
  },

  // 获取用户信息
  getUserProfile() {
    return request.get('/auth/profile')
  },

  // 更新用户信息
  updateProfile(data) {
    return request.put('/auth/profile', data)
  },

  // 修改密码
  changePassword(data) {
    return request.post('/auth/change-password', data)
  },

  // 验证token
  verifyToken() {
    return request.post('/auth/verify-token')
  }
}

export default authAPI