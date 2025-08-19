import request, { type ApiResponse } from './request'

// 后端响应格式接口
interface BackendResponse<T = any> {
  code: number
  message: string
  data: T
}

// 标准化响应格式接口
interface StandardResponse<T = any> {
  success: boolean
  data: T
  message: string
}

/**
 * API适配器类
 * 用于统一处理不同的后端响应格式
 */
class ApiAdapter {
  /**
   * 适配后端响应格式到标准格式
   * @param response 后端响应数据
   * @returns 标准化响应数据
   */
  private adaptResponse<T>(response: BackendResponse<T>): StandardResponse<T> {
    return {
      success: response.code === 200 || response.code === 0,
      data: response.data,
      message: response.message || '操作成功'
    }
  }

  /**
   * 处理请求并适配响应格式
   * @param requestPromise 请求Promise
   * @returns 标准化响应Promise
   */
  private async handleRequest<T>(requestPromise: Promise<any>): Promise<StandardResponse<T>> {
    try {
      const response = await requestPromise
      
      // 如果响应已经是标准格式，直接返回
      if (typeof response.success === 'boolean') {
        return response as StandardResponse<T>
      }
      
      // 如果是后端格式，进行适配
      if (typeof response.code === 'number') {
        return this.adaptResponse<T>(response as BackendResponse<T>)
      }
      
      // 默认处理
      return {
        success: true,
        data: response as T,
        message: '操作成功'
      }
    } catch (error: any) {
      // 统一错误处理
      return {
        success: false,
        data: null as T,
        message: error.message || '请求失败'
      }
    }
  }

  /**
   * GET请求适配器
   */
  async get<T = any>(url: string, config?: any): Promise<StandardResponse<T>> {
    return this.handleRequest<T>(request.get(url, config))
  }

  /**
   * POST请求适配器
   */
  async post<T = any>(url: string, data?: any, config?: any): Promise<StandardResponse<T>> {
    return this.handleRequest<T>(request.post(url, data, config))
  }

  /**
   * PUT请求适配器
   */
  async put<T = any>(url: string, data?: any, config?: any): Promise<StandardResponse<T>> {
    return this.handleRequest<T>(request.put(url, data, config))
  }

  /**
   * DELETE请求适配器
   */
  async delete<T = any>(url: string, config?: any): Promise<StandardResponse<T>> {
    return this.handleRequest<T>(request.delete(url, config))
  }

  /**
   * 文件上传适配器
   */
  async upload<T = any>(url: string, file: File, config?: any): Promise<StandardResponse<T>> {
    return this.handleRequest<T>(request.upload(url, file, config))
  }

  /**
   * 批量请求适配器
   * @param requests 请求数组
   * @returns 批量响应结果
   */
  async batch<T = any>(requests: Array<() => Promise<any>>): Promise<StandardResponse<T[]>> {
    try {
      const results = await Promise.allSettled(requests.map(req => req()))
      const data = results.map(result => {
        if (result.status === 'fulfilled') {
          return result.value
        } else {
          return { error: result.reason?.message || '请求失败' }
        }
      })
      
      return {
        success: true,
        data: data as T[],
        message: '批量请求完成'
      }
    } catch (error: any) {
      return {
        success: false,
        data: [] as T[],
        message: error.message || '批量请求失败'
      }
    }
  }

  /**
   * 重试请求适配器
   * @param requestFn 请求函数
   * @param maxRetries 最大重试次数
   * @param delay 重试延迟时间（毫秒）
   */
  async retry<T = any>(
    requestFn: () => Promise<any>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<StandardResponse<T>> {
    let lastError: any
    
    for (let i = 0; i <= maxRetries; i++) {
      try {
        const result = await this.handleRequest<T>(requestFn())
        if (result.success) {
          return result
        }
        lastError = new Error(result.message)
      } catch (error) {
        lastError = error
        if (i < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
        }
      }
    }
    
    return {
      success: false,
      data: null as T,
      message: lastError?.message || '请求重试失败'
    }
  }

  /**
   * 缓存请求适配器
   * @param key 缓存键
   * @param requestFn 请求函数
   * @param ttl 缓存时间（毫秒）
   */
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>()
  
  async cached<T = any>(
    key: string,
    requestFn: () => Promise<any>,
    ttl: number = 5 * 60 * 1000 // 默认5分钟
  ): Promise<StandardResponse<T>> {
    const now = Date.now()
    const cached = this.cache.get(key)
    
    // 检查缓存是否有效
    if (cached && (now - cached.timestamp) < cached.ttl) {
      return {
        success: true,
        data: cached.data,
        message: '从缓存获取数据'
      }
    }
    
    // 发起新请求
    const result = await this.handleRequest<T>(requestFn())
    
    // 缓存成功的响应
    if (result.success) {
      this.cache.set(key, {
        data: result.data,
        timestamp: now,
        ttl
      })
    }
    
    return result
  }

  /**
   * 清除缓存
   * @param key 缓存键，不传则清除所有缓存
   */
  clearCache(key?: string) {
    if (key) {
      this.cache.delete(key)
    } else {
      this.cache.clear()
    }
  }
}

// 创建API适配器实例
const apiAdapter = new ApiAdapter()

export default apiAdapter
export type { StandardResponse, BackendResponse }