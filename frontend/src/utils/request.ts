import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 响应数据接口
interface ApiResponse<T = any> {
  success: boolean
  data: T
  message: string
  code?: number
}

// 请求配置接口
interface RequestConfig extends AxiosRequestConfig {
  showLoading?: boolean
  showError?: boolean
  timeout?: number
}

class RequestService {
  private instance: AxiosInstance
  private loadingInstance: any = null
  private requestCount = 0

  constructor() {
    // 创建axios实例
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const userStore = useUserStore()
        
        // 添加认证token
        if (userStore.token) {
          config.headers.Authorization = `Bearer ${userStore.token}`
        }

        // 显示loading
        const requestConfig = config as RequestConfig
        if (requestConfig.showLoading !== false) {
          this.showLoading()
        }

        return config
      },
      (error) => {
        this.hideLoading()
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        this.hideLoading()
        
        const { data } = response
        const requestConfig = response.config as RequestConfig

        // 统一处理响应格式
        if (data.success === false) {
          if (requestConfig.showError !== false) {
            ElMessage.error(data.message || '请求失败')
          }
          return Promise.reject(new Error(data.message || '请求失败'))
        }

        // 返回原始响应，让具体的API方法处理数据提取
        return response
      },
      (error) => {
        this.hideLoading()
        const requestConfig = error.config as RequestConfig
        
        if (error.response) {
          const { status, data } = error.response
          let message = '请求失败'

          switch (status) {
            case 401:
              message = '未授权，请重新登录'
              this.handleUnauthorized()
              break
            case 403:
              message = '拒绝访问'
              break
            case 404:
              message = '请求地址出错'
              break
            case 408:
              message = '请求超时'
              break
            case 422:
              message = data?.message || '数据验证失败'
              break
            case 500:
              message = '服务器内部错误'
              break
            case 502:
              message = '网关错误'
              break
            case 503:
              message = '服务不可用'
              break
            case 504:
              message = '网关超时'
              break
            default:
              message = data?.message || `连接错误${status}`
          }

          if (requestConfig.showError !== false) {
            ElMessage.error(message)
          }
        } else if (error.request) {
          const message = '网络连接异常，请检查网络设置'
          if (requestConfig.showError !== false) {
            ElMessage.error(message)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  private showLoading() {
    this.requestCount++
    if (this.requestCount === 1 && !this.loadingInstance) {
      this.loadingInstance = ElLoading.service({
        text: '加载中...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
    }
  }

  private hideLoading() {
    this.requestCount--
    if (this.requestCount <= 0) {
      this.requestCount = 0
      if (this.loadingInstance) {
        this.loadingInstance.close()
        this.loadingInstance = null
      }
    }
  }

  private handleUnauthorized() {
    const userStore = useUserStore()
    userStore.logout()
    router.push('/login')
  }

  // 通用请求方法
  public async request<T = any>(config: RequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.request(config)
    return response.data
  }

  // GET请求
  public async get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.get(url, config)
    return response.data
  }

  // POST请求
  public async post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.post(url, data, config)
    return response.data
  }

  // PUT请求
  public async put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.put(url, data, config)
    return response.data
  }

  // DELETE请求
  public async delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.delete(url, config)
    return response.data
  }

  // 文件上传
  public async upload<T = any>(url: string, file: File, config?: RequestConfig): Promise<ApiResponse<T>> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers
      }
    })
    return response.data
  }

  // 文件下载
  public download(url: string, filename?: string, config?: RequestConfig): Promise<void> {
    return this.instance.get(url, {
      ...config,
      responseType: 'blob'
    }).then((response) => {
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

// 创建请求实例
const request = new RequestService()

export default request
export type { ApiResponse, RequestConfig }