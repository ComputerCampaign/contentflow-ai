import { BaseApiService } from './base'
import apiAdapter, { type StandardResponse } from '@/utils/api-adapter'

// 用户信息接口
export interface User {
  id: number
  username: string
  email: string
  role: 'normal' | 'advanced' | 'admin'
  avatar?: string
  nickname?: string
  phone?: string
  status: 'active' | 'inactive' | 'banned'
  lastLoginTime?: string
  createdAt: string
  updatedAt: string
}

// 登录请求参数
export interface LoginParams {
  username: string
  password: string
  captcha?: string
  rememberMe?: boolean
}

// 登录响应数据
export interface LoginResponse {
  user: User
  token: string
  refreshToken: string
  expiresIn: number
}

// 注册请求参数
export interface RegisterParams {
  username: string
  email: string
  password: string
  confirmPassword: string
  captcha?: string
  inviteCode?: string
}

// 修改密码参数
export interface ChangePasswordParams {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}

// 重置密码参数
export interface ResetPasswordParams {
  email: string
  code: string
  newPassword: string
  confirmPassword: string
}

// 更新用户信息参数
export interface UpdateUserParams {
  nickname?: string
  email?: string
  phone?: string
  avatar?: string
}

/**
 * 用户认证API服务
 */
class AuthApiService extends BaseApiService {
  constructor() {
    super('/api/auth')
  }

  /**
   * 用户登录
   * @param params 登录参数
   */
  async login(params: LoginParams): Promise<StandardResponse<LoginResponse>> {
    return apiAdapter.post<LoginResponse>(`${this.baseUrl}/login`, params)
  }

  /**
   * 用户注册
   * @param params 注册参数
   */
  async register(params: RegisterParams): Promise<StandardResponse<User>> {
    return apiAdapter.post<User>(`${this.baseUrl}/register`, params)
  }

  /**
   * 用户登出
   */
  async logout(): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/logout`)
  }

  /**
   * 刷新Token
   * @param refreshToken 刷新令牌
   */
  async refreshToken(refreshToken: string): Promise<StandardResponse<{
    token: string
    refreshToken: string
    expiresIn: number
  }>> {
    return apiAdapter.post(`${this.baseUrl}/refresh-token`, { refreshToken })
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<StandardResponse<User>> {
    return apiAdapter.get<User>(`${this.baseUrl}/me`)
  }

  /**
   * 更新用户信息
   * @param params 更新参数
   */
  async updateProfile(params: UpdateUserParams): Promise<StandardResponse<User>> {
    return apiAdapter.put<User>(`${this.baseUrl}/profile`, params)
  }

  /**
   * 修改密码
   * @param params 修改密码参数
   */
  async changePassword(params: ChangePasswordParams): Promise<StandardResponse<void>> {
    return apiAdapter.put<void>(`${this.baseUrl}/change-password`, params)
  }

  /**
   * 发送重置密码邮件
   * @param email 邮箱地址
   */
  async sendResetPasswordEmail(email: string): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/send-reset-email`, { email })
  }

  /**
   * 重置密码
   * @param params 重置密码参数
   */
  async resetPassword(params: ResetPasswordParams): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/reset-password`, params)
  }

  /**
   * 发送邮箱验证码
   * @param email 邮箱地址
   * @param type 验证码类型
   */
  async sendEmailCode(
    email: string,
    type: 'register' | 'reset-password' | 'change-email' = 'register'
  ): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/send-email-code`, { email, type })
  }

  /**
   * 验证邮箱验证码
   * @param email 邮箱地址
   * @param code 验证码
   * @param type 验证码类型
   */
  async verifyEmailCode(
    email: string,
    code: string,
    type: 'register' | 'reset-password' | 'change-email' = 'register'
  ): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/verify-email-code`, { email, code, type })
  }

  /**
   * 获取图形验证码
   */
  async getCaptcha(): Promise<StandardResponse<{
    captchaId: string
    captchaImage: string
  }>> {
    return apiAdapter.get(`${this.baseUrl}/captcha`)
  }

  /**
   * 验证图形验证码
   * @param captchaId 验证码ID
   * @param captcha 验证码
   */
  async verifyCaptcha(captchaId: string, captcha: string): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/verify-captcha`, { captchaId, captcha })
  }

  /**
   * 上传头像
   * @param file 头像文件
   */
  async uploadAvatar(file: File): Promise<StandardResponse<{ avatar: string }>> {
    return apiAdapter.upload<{ avatar: string }>(`${this.baseUrl}/upload-avatar`, file)
  }

  /**
   * 绑定第三方账号
   * @param provider 第三方平台
   * @param code 授权码
   */
  async bindThirdParty(
    provider: 'github' | 'google' | 'wechat',
    code: string
  ): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/bind/${provider}`, { code })
  }

  /**
   * 解绑第三方账号
   * @param provider 第三方平台
   */
  async unbindThirdParty(
    provider: 'github' | 'google' | 'wechat'
  ): Promise<StandardResponse<void>> {
    return apiAdapter.delete<void>(`${this.baseUrl}/bind/${provider}`)
  }

  /**
   * 获取用户权限列表
   */
  async getUserPermissions(): Promise<StandardResponse<string[]>> {
    return apiAdapter.get<string[]>(`${this.baseUrl}/permissions`)
  }

  /**
   * 检查用户权限
   * @param permission 权限标识
   */
  async checkPermission(permission: string): Promise<StandardResponse<boolean>> {
    return apiAdapter.get<boolean>(`${this.baseUrl}/check-permission?permission=${permission}`)
  }

  /**
   * 获取用户操作日志
   * @param params 查询参数
   */
  async getUserLogs(params?: {
    page?: number
    pageSize?: number
    startDate?: string
    endDate?: string
    action?: string
  }): Promise<StandardResponse<{
    list: Array<{
      id: number
      action: string
      description: string
      ip: string
      userAgent: string
      createdAt: string
    }>
    total: number
    page: number
    pageSize: number
  }>> {
    const queryParams = params ? new URLSearchParams(params as any).toString() : ''
    return apiAdapter.get(`${this.baseUrl}/logs${queryParams ? '?' + queryParams : ''}`)
  }

  /**
   * 注销账号
   * @param password 确认密码
   * @param reason 注销原因
   */
  async deleteAccount(
    password: string,
    reason?: string
  ): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/delete-account`, { password, reason })
  }
}

// 创建并导出API服务实例
const authApi = new AuthApiService()

export default authApi