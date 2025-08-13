import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import Cookies from 'js-cookie'
import { authAPI } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(Cookies.get('token') || '')
  const userInfo = ref({
    id: null,
    username: '',
    email: '',
    avatar: '',
    role: '',
    permissions: []
  })
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const hasPermission = computed(() => (permission) => {
    return userInfo.value.permissions.includes(permission)
  })

  // 登录
  const login = async (loginData) => {
    try {
      loading.value = true
      const response = await authAPI.login(loginData)
      
      // 后端返回的数据结构：{success: true, data: {access_token, user, ...}}
      // request.js会将data.data作为response.data返回
      const { access_token, user } = response.data
      
      if (!access_token || !user) {
        throw new Error('登录响应数据格式错误')
      }
      
      token.value = access_token
      userInfo.value = {
        id: user.id,
        username: user.username,
        email: user.email,
        avatar: user.avatar || '',
        role: user.role || 'user',
        permissions: user.permissions || []
      }
      
      // 保存token到cookie
      Cookies.set('token', access_token, { expires: 7 })
      
      // 不在这里显示成功消息，让Login.vue组件处理
      return true
    } catch (error) {
      console.error('登录失败详情:', error)
      ElMessage.error(error.response?.data?.message || error.message || '登录失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (registerData) => {
    try {
      loading.value = true
      const response = await authAPI.register(registerData)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '注册失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      token.value = ''
      userInfo.value = {
        id: null,
        username: '',
        email: '',
        avatar: '',
        role: '',
        permissions: []
      }
      Cookies.remove('token')
      ElMessage.success('已退出登录')
    }
  }

  // 检查认证状态
  const checkAuth = async () => {
    if (!token.value) return false
    
    try {
      const response = await authAPI.getUserProfile()
      const user = response.data
      userInfo.value = {
        id: user.id,
        username: user.username,
        email: user.email,
        avatar: user.avatar || '',
        role: user.role || 'user',
        permissions: user.permissions || []
      }
      return true
    } catch (error) {
      // token无效，清除登录状态
      token.value = ''
      Cookies.remove('token')
      return false
    }
  }

  // 更新用户信息
  const updateUserInfo = async (data) => {
    try {
      loading.value = true
      const response = await api.put('/auth/profile', data)
      userInfo.value = { ...userInfo.value, ...response.data }
      ElMessage.success('用户信息更新成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '更新失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (passwordData) => {
    try {
      loading.value = true
      await api.put('/auth/password', passwordData)
      ElMessage.success('密码修改成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '密码修改失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    token,
    userInfo,
    loading,
    isAuthenticated,
    hasPermission,
    login,
    register,
    logout,
    checkAuth
  }
})