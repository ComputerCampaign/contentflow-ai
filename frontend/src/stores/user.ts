import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import authApi from '@/api/auth'
import type { User, LoginParams, RegisterParams } from '@/api/auth'
import { removeToken, setToken, getToken } from '@/utils/auth'
import router from '@/router'

// 用户角色枚举
export enum UserRole {
  NORMAL = 'normal',
  ADVANCED = 'advanced',
  ADMIN = 'admin'
}

// 用户状态接口
interface UserState {
  token: string | null
  userInfo: User | null
  permissions: string[]
  isLoggedIn: boolean
  loginLoading: boolean
  logoutLoading: boolean
}

export const useUserStore = defineStore('user', () => {
  // 状态定义
  const token = ref<string | null>(getToken())
  const userInfo = ref<User | null>(null)
  const permissions = ref<string[]>([])
  const loginLoading = ref(false)
  const logoutLoading = ref(false)
  const profileLoading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const isAdmin = computed(() => userInfo.value?.role === UserRole.ADMIN)
  const isAdvanced = computed(() => 
    userInfo.value?.role === UserRole.ADVANCED || userInfo.value?.role === UserRole.ADMIN
  )
  const userName = computed(() => userInfo.value?.username || '')
  const userEmail = computed(() => userInfo.value?.email || '')
  const userAvatar = computed(() => userInfo.value?.avatar || '')
  const userRole = computed(() => userInfo.value?.role || UserRole.NORMAL)

  // 登录
  const login = async (loginData: LoginParams): Promise<boolean> => {
    try {
      loginLoading.value = true
      const response = await authApi.login(loginData)
      
      if (response.success && response.data) {
        console.log('Login response.data.access_token:', response.data.access_token)
        console.log('Login response.data.user:', response.data.user)
        
        // 保存token (后端返回的是 access_token 字段)
        token.value = response.data.access_token
        setToken(response.data.access_token)
        
        // 验证token是否保存成功
        console.log('After setToken - token.value:', token.value)
        console.log('After setToken - localStorage:', localStorage.getItem('access_token'))
        
        // 保存用户信息
        userInfo.value = response.data.user
        permissions.value = await getUserPermissions()
        
        ElMessage.success('登录成功')
        return true
      } else {
        console.log('Login failed - response:', response)
        ElMessage.error(response.message || '登录失败')
        return false
      }
    } catch (error: any) {
      console.error('Login error:', error)
      ElMessage.error(error.message || '登录失败，请稍后重试')
      return false
    } finally {
      loginLoading.value = false
    }
  }

  // 注册
  const register = async (registerData: RegisterParams): Promise<boolean> => {
    try {
      loginLoading.value = true
      const response = await authApi.register(registerData)
      
      if (response.success) {
        ElMessage.success('注册成功，请登录')
        return true
      } else {
        ElMessage.error(response.message || '注册失败')
        return false
      }
    } catch (error: any) {
      console.error('Register error:', error)
      ElMessage.error(error.message || '注册失败，请稍后重试')
      return false
    } finally {
      loginLoading.value = false
    }
  }

  // 忘记密码
  const forgotPassword = async (email: string): Promise<boolean> => {
    try {
      const response = await authApi.sendResetPasswordEmail(email)
      
      if (response.success) {
        return true
      } else {
        throw new Error(response.message || '发送失败')
      }
    } catch (error: any) {
      console.error('Forgot password error:', error)
      throw error
    }
  }

  // 获取用户信息
  const getUserInfo = async (): Promise<boolean> => {
    try {
      if (!token.value) {
        return false
      }

      profileLoading.value = true
      const response = await authApi.getCurrentUser()
      
      if (response.success && response.data) {
        userInfo.value = response.data
        permissions.value = await getUserPermissions()
        return true
      } else {
        // Token可能已过期，清除登录状态
        await logout(false)
        return false
      }
    } catch (error: any) {
      console.error('Get user info error:', error)
      // 如果是401错误，清除登录状态
      if (error.status === 401) {
        await logout(false)
      }
      return false
    } finally {
      profileLoading.value = false
    }
  }

  // 获取用户权限
  const getUserPermissions = async (): Promise<string[]> => {
    try {
      const response = await authApi.getUserPermissions()
      return response.success && response.data ? response.data : []
    } catch (error) {
      console.error('Get user permissions error:', error)
      return []
    }
  }

  // 更新用户信息
  const updateUserInfo = async (updateData: Partial<User>): Promise<boolean> => {
    try {
      profileLoading.value = true
      const response = await authApi.updateProfile(updateData)
      
      if (response.success && response.data) {
        userInfo.value = { ...userInfo.value, ...response.data }
        ElMessage.success('个人信息更新成功')
        return true
      } else {
        ElMessage.error(response.message || '更新失败')
        return false
      }
    } catch (error: any) {
      console.error('Update user info error:', error)
      ElMessage.error(error.message || '更新失败，请稍后重试')
      return false
    } finally {
      profileLoading.value = false
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string, confirmPassword: string): Promise<boolean> => {
    try {
      profileLoading.value = true
      const response = await authApi.changePassword({
        oldPassword,
        newPassword,
        confirmPassword
      })
      
      if (response.success) {
        ElMessage.success('密码修改成功，请重新登录')
        await logout()
        return true
      } else {
        ElMessage.error(response.message || '密码修改失败')
        return false
      }
    } catch (error: any) {
      console.error('Change password error:', error)
      ElMessage.error(error.message || '密码修改失败，请稍后重试')
      return false
    } finally {
      profileLoading.value = false
    }
  }

  // 登出
  const logout = async (showMessage = true): Promise<void> => {
    try {
      logoutLoading.value = true
      
      // 调用登出API
      if (token.value) {
        try {
          await authApi.logout()
        } catch (error) {
          // 忽略登出API错误，继续清除本地状态
          console.warn('Logout API error:', error)
        }
      }
      
      // 清除本地状态
      token.value = null
      userInfo.value = null
      permissions.value = []
      removeToken()
      
      if (showMessage) {
        ElMessage.success('已退出登录')
      }
      
      // 跳转到登录页
      await router.push('/login')
    } catch (error: any) {
      console.error('Logout error:', error)
    } finally {
      logoutLoading.value = false
    }
  }

  // 刷新Token
  const refreshToken = async (refreshTokenValue?: string): Promise<boolean> => {
    try {
      const response = await authApi.refreshToken(refreshTokenValue || '')
      
      if (response.success && response.data) {
        token.value = response.data.token
        setToken(response.data.token)
        return true
      } else {
        await logout(false)
        return false
      }
    } catch (error: any) {
      console.error('Refresh token error:', error)
      await logout(false)
      return false
    }
  }

  // 检查权限
  const hasPermission = (permission: string): boolean => {
    if (isAdmin.value) {
      return true
    }
    
    // 检查是否有完全匹配的权限
    if (permissions.value.includes(permission)) {
      return true
    }
    
    // 检查通配符权限，如 admin:* 包含所有权限
    if (permissions.value.includes('*') || permissions.value.includes('admin:*')) {
      return true
    }
    
    // 检查模块级通配符权限，如 task:* 包含 task:view, task:create 等
    return permissions.value.some(userPerm => {
      if (userPerm.endsWith(':*')) {
        const prefix = userPerm.slice(0, -1)
        return permission.startsWith(prefix)
      }
      return false
    })
  }

  // 检查多个权限（需要全部拥有）
  const hasAllPermissions = (permissionList: string[]): boolean => {
    if (isAdmin.value) {
      return true
    }
    return permissionList.every(permission => hasPermission(permission))
  }

  // 检查多个权限（拥有其中一个即可）
  const hasAnyPermission = (permissionList: string[]): boolean => {
    if (isAdmin.value) {
      return true
    }
    return permissionList.some(permission => hasPermission(permission))
  }

  // 检查角色
  const hasRole = (role: UserRole): boolean => {
    return userInfo.value?.role === role
  }

  // 检查是否有更高或相等的角色权限
  const hasRoleOrHigher = (role: UserRole): boolean => {
    const roleHierarchy = {
      [UserRole.NORMAL]: 1,
      [UserRole.ADVANCED]: 2,
      [UserRole.ADMIN]: 3
    }
    
    const currentRoleLevel = roleHierarchy[userInfo.value?.role || UserRole.NORMAL]
    const requiredRoleLevel = roleHierarchy[role]
    
    return currentRoleLevel >= requiredRoleLevel
  }

  // 重置状态
  const resetState = () => {
    token.value = null
    userInfo.value = null
    permissions.value = []
    loginLoading.value = false
    logoutLoading.value = false
    profileLoading.value = false
    removeToken()
  }

  // 初始化用户状态（应用启动时调用）
  const initUserState = async (): Promise<boolean> => {
    if (token.value) {
      return await getUserInfo()
    }
    return false
  }

  return {
    // 状态
    token,
    userInfo,
    permissions,
    loginLoading,
    logoutLoading,
    profileLoading,
    
    // 计算属性
    isLoggedIn,
    isAdmin,
    isAdvanced,
    userName,
    userEmail,
    userAvatar,
    userRole,
    
    // 方法
    login,
    register,
    forgotPassword,
    logout,
    getUserInfo,
    getUserPermissions,
    updateUserInfo,
    changePassword,
    refreshToken,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    hasRole,
    hasRoleOrHigher,
    resetState,
    initUserState
  }
})