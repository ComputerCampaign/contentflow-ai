import apiAdapter, { type StandardResponse } from '@/utils/api-adapter'

/**
 * API服务基类
 * 提供通用的CRUD操作方法
 */
export abstract class BaseApiService {
  protected baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * 获取列表数据
   * @param params 查询参数
   */
  async getList<T = any>(params?: Record<string, any>): Promise<StandardResponse<T[]>> {
    const url = params ? `${this.baseUrl}?${new URLSearchParams(params).toString()}` : this.baseUrl
    return apiAdapter.get<T[]>(url)
  }

  /**
   * 获取分页列表数据
   * @param params 查询参数
   */
  async getPagedList<T = any>(params?: {
    page?: number
    pageSize?: number
    [key: string]: any
  }): Promise<StandardResponse<{
    list: T[]
    total: number
    page: number
    pageSize: number
  }>> {
    const queryParams = {
      page: 1,
      pageSize: 10,
      ...params
    }
    const url = `${this.baseUrl}?${new URLSearchParams(queryParams as any).toString()}`
    return apiAdapter.get(url)
  }

  /**
   * 根据ID获取单条数据
   * @param id 数据ID
   */
  async getById<T = any>(id: string | number): Promise<StandardResponse<T>> {
    return apiAdapter.get<T>(`${this.baseUrl}/${id}`)
  }

  /**
   * 创建新数据
   * @param data 创建数据
   */
  async create<T = any>(data: Record<string, any>): Promise<StandardResponse<T>> {
    return apiAdapter.post<T>(this.baseUrl, data)
  }

  /**
   * 更新数据
   * @param id 数据ID
   * @param data 更新数据
   */
  async update<T = any>(id: string | number, data: Record<string, any>): Promise<StandardResponse<T>> {
    return apiAdapter.put<T>(`${this.baseUrl}/${id}`, data)
  }

  /**
   * 删除数据
   * @param id 数据ID
   */
  async delete<T = any>(id: string | number): Promise<StandardResponse<T>> {
    return apiAdapter.delete<T>(`${this.baseUrl}/${id}`)
  }

  /**
   * 批量删除数据
   * @param ids 数据ID数组
   */
  async batchDelete<T = any>(ids: (string | number)[]): Promise<StandardResponse<T>> {
    return apiAdapter.post<T>(`${this.baseUrl}/batch-delete`, { ids })
  }

  /**
   * 批量操作
   * @param action 操作类型
   * @param ids 数据ID数组
   * @param data 操作数据
   */
  async batchAction<T = any>(
    action: string,
    ids: (string | number)[],
    data?: Record<string, any>
  ): Promise<StandardResponse<T>> {
    return apiAdapter.post<T>(`${this.baseUrl}/batch-${action}`, {
      ids,
      ...data
    })
  }

  /**
   * 搜索数据
   * @param keyword 搜索关键词
   * @param params 其他查询参数
   */
  async search<T = any>(
    keyword: string,
    params?: Record<string, any>
  ): Promise<StandardResponse<T[]>> {
    const queryParams = {
      keyword,
      ...params
    }
    return apiAdapter.get<T[]>(`${this.baseUrl}/search?${new URLSearchParams(queryParams).toString()}`)
  }

  /**
   * 导出数据
   * @param params 导出参数
   * @param format 导出格式
   */
  async export(
    params?: Record<string, any>,
    format: 'csv' | 'excel' | 'json' = 'csv'
  ): Promise<StandardResponse<Blob>> {
    const queryParams = {
      format,
      ...params
    }
    return apiAdapter.get<Blob>(`${this.baseUrl}/export?${new URLSearchParams(queryParams).toString()}`)
  }

  /**
   * 导入数据
   * @param file 导入文件
   * @param options 导入选项
   */
  async import<T = any>(
    file: File,
    options?: Record<string, any>
  ): Promise<StandardResponse<T>> {
    const formData = new FormData()
    formData.append('file', file)
    if (options) {
      Object.keys(options).forEach(key => {
        formData.append(key, options[key])
      })
    }
    return apiAdapter.upload<T>(`${this.baseUrl}/import`, file)
  }

  /**
   * 获取统计数据
   * @param params 统计参数
   */
  async getStats<T = any>(params?: Record<string, any>): Promise<StandardResponse<T>> {
    const url = params 
      ? `${this.baseUrl}/stats?${new URLSearchParams(params).toString()}`
      : `${this.baseUrl}/stats`
    return apiAdapter.get<T>(url)
  }

  /**
   * 验证数据
   * @param data 验证数据
   */
  async validate<T = any>(data: Record<string, any>): Promise<StandardResponse<T>> {
    return apiAdapter.post<T>(`${this.baseUrl}/validate`, data)
  }

  /**
   * 复制数据
   * @param id 源数据ID
   * @param data 复制时的修改数据
   */
  async duplicate<T = any>(
    id: string | number,
    data?: Record<string, any>
  ): Promise<StandardResponse<T>> {
    return apiAdapter.post<T>(`${this.baseUrl}/${id}/duplicate`, data)
  }

  /**
   * 切换状态
   * @param id 数据ID
   * @param status 新状态
   */
  async toggleStatus<T = any>(
    id: string | number,
    status: string | boolean
  ): Promise<StandardResponse<T>> {
    return apiAdapter.put<T>(`${this.baseUrl}/${id}/status`, { status })
  }
}

/**
 * 创建API服务实例的工厂函数
 * @param baseUrl API基础路径
 */
export function createApiService(baseUrl: string) {
  return new (class extends BaseApiService {
    constructor() {
      super(baseUrl)
    }
  })()
}

export default BaseApiService