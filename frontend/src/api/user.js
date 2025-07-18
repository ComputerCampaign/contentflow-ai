import api from './index'

export default {
  // 获取所有用户列表（仅管理员）
  getUsers() {
    return api.get('/user/users')
  },
  
  // 获取用户详情（仅管理员）
  getUserDetail(userId) {
    return api.get(`/user/users/${userId}`)
  },
  
  // 更新用户信息（仅管理员）
  updateUser(userId, userData) {
    return api.put(`/user/users/${userId}`, userData)
  },
  
  // 获取所有用户组
  getGroups() {
    return api.get('/user/groups')
  },
  
  // 创建新的用户组（仅管理员）
  createGroup(groupData) {
    return api.post('/user/groups', groupData)
  }
}