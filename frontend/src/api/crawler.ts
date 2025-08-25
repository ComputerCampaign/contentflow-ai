import { BaseApiService } from './base'
import apiAdapter, { type StandardResponse } from '@/utils/api-adapter'

// 爬虫配置状态枚举
export type CrawlerStatus = 'active' | 'inactive' | 'testing' | 'error'

// 爬虫类型枚举
export type CrawlerType = 'web' | 'api' | 'rss' | 'sitemap'

// 数据提取方式枚举
export type ExtractionMethod = 'xpath' | 'css' | 'regex' | 'json'

// 爬虫配置接口
export interface CrawlerConfig {
  id: number
  name: string
  description?: string
  type: CrawlerType
  status: CrawlerStatus
  targetUrl: string
  allowedDomains: string[]
  userAgent?: string
  headers?: Record<string, string>
  cookies?: Record<string, string>
  proxyConfig?: {
    enabled: boolean
    host?: string
    port?: number
    username?: string
    password?: string
  }
  rateLimit?: {
    enabled: boolean
    requestsPerSecond?: number
    delayBetweenRequests?: number
  }
  retryConfig?: {
    enabled: boolean
    maxRetries?: number
    retryDelay?: number
    retryOnStatus?: number[]
  }
  extractionRules: ExtractionRule[]
  filterRules?: FilterRule[]
  transformRules?: TransformRule[]
  outputConfig?: {
    format: 'json' | 'csv' | 'xml'
    fields?: string[]
    filename?: string
  }
  scheduleConfig?: {
    enabled: boolean
    cron?: string
    timezone?: string
    nextRunTime?: string
  }
  notificationConfig?: {
    enabled: boolean
    email?: string[]
    webhook?: string
    onSuccess?: boolean
    onError?: boolean
  }
  userId: number
  createdAt: string
  updatedAt: string
  lastRunTime?: string
  lastRunStatus?: 'success' | 'failed'
  totalRuns?: number
  successRuns?: number
  failedRuns?: number
}

// 数据提取规则接口
export interface ExtractionRule {
  id?: number
  name: string
  field: string
  method: ExtractionMethod
  selector: string
  attribute?: string
  required?: boolean
  multiple?: boolean
  defaultValue?: string
  validation?: {
    type?: 'string' | 'number' | 'email' | 'url' | 'date'
    pattern?: string
    minLength?: number
    maxLength?: number
    min?: number
    max?: number
  }
}

// 过滤规则接口
export interface FilterRule {
  id?: number
  name: string
  field: string
  operator: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'regex' | 'gt' | 'lt' | 'gte' | 'lte'
  value: string | number
  caseSensitive?: boolean
}

// 转换规则接口
export interface TransformRule {
  id?: number
  name: string
  field: string
  type: 'replace' | 'trim' | 'lowercase' | 'uppercase' | 'format' | 'calculate'
  config: Record<string, any>
}

// 创建爬虫配置参数
export interface CreateCrawlerParams {
  name: string
  description?: string
  type: CrawlerType
  targetUrl: string
  allowedDomains?: string[]
  userAgent?: string
  headers?: Record<string, string>
  cookies?: Record<string, string>
  proxyConfig?: CrawlerConfig['proxyConfig']
  rateLimit?: CrawlerConfig['rateLimit']
  retryConfig?: CrawlerConfig['retryConfig']
  extractionRules: Omit<ExtractionRule, 'id'>[]
  filterRules?: Omit<FilterRule, 'id'>[]
  transformRules?: Omit<TransformRule, 'id'>[]
  outputConfig?: CrawlerConfig['outputConfig']
  scheduleConfig?: CrawlerConfig['scheduleConfig']
  notificationConfig?: CrawlerConfig['notificationConfig']
}

// 更新爬虫配置参数
export interface UpdateCrawlerParams extends Partial<CreateCrawlerParams> {}

// 爬虫配置查询参数
export interface CrawlerQueryParams {
  page?: number
  pageSize?: number
  status?: CrawlerStatus
  type?: CrawlerType
  keyword?: string
  sortBy?: 'createdAt' | 'updatedAt' | 'lastRunTime' | 'name'
  sortOrder?: 'asc' | 'desc'
}

// 爬虫测试结果
export interface CrawlerTestResult {
  success: boolean
  message: string
  data?: Record<string, any>[]
  errors?: string[]
  warnings?: string[]
  statistics?: {
    totalPages: number
    processedPages: number
    extractedItems: number
    executionTime: number
    averageResponseTime: number
  }
}

// 爬虫运行结果
export interface CrawlerRunResult {
  id: number
  crawlerConfigId: number
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  startTime: string
  endTime?: string
  totalPages: number
  processedPages: number
  extractedItems: number
  failedPages: number
  errors?: string[]
  warnings?: string[]
  outputFile?: string
  statistics?: {
    executionTime: number
    averageResponseTime: number
    dataSize: number
    memoryUsage: number
    cpuUsage: number
  }
}

/**
 * 爬虫配置API服务
 */
class CrawlerApiService extends BaseApiService {
  constructor() {
    super('/crawler-configs')
  }

  /**
   * 过滤爬虫查询参数中的undefined和null值
   * @param params 原始参数
   */
  protected filterParams(params?: Record<string, any>): Record<string, string> {
    if (!params) return {}
    
    const filtered: Record<string, string> = {}
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          filtered[key] = value.join(',')
        } else {
          filtered[key] = String(value)
        }
      }
    })
    return filtered
  }

  /**
   * 获取爬虫配置列表
   * @param params 查询参数
   */
  async getCrawlerConfigs(params?: CrawlerQueryParams): Promise<StandardResponse<{
    configs: CrawlerConfig[]
    pagination: {
      page: number
      per_page: number
      total: number
    }
  }>> {
    const queryParams = this.filterParams(params)
    const queryString = new URLSearchParams(queryParams).toString()
    return apiAdapter.get(`${this.baseUrl}/configs${queryString ? '?' + queryString : ''}`)
  }

  /**
   * 获取爬虫配置详情
   * @param id 配置ID
   */
  async getCrawlerConfig(id: number): Promise<StandardResponse<CrawlerConfig>> {
    return this.getById<CrawlerConfig>(id)
  }

  /**
   * 创建爬虫配置
   * @param params 创建参数
   */
  async createCrawlerConfig(params: CreateCrawlerParams): Promise<StandardResponse<CrawlerConfig>> {
    return apiAdapter.post<CrawlerConfig>(`${this.baseUrl}/configs`, params)
  }

  /**
   * 更新爬虫配置
   * @param id 配置ID
   * @param params 更新参数
   */
  async updateCrawlerConfig(id: number, params: UpdateCrawlerParams): Promise<StandardResponse<CrawlerConfig>> {
    return this.update<CrawlerConfig>(id, params)
  }

  /**
   * 删除爬虫配置
   * @param id 配置ID
   */
  async deleteCrawlerConfig(id: number): Promise<StandardResponse<void>> {
    return this.delete<void>(id)
  }

  /**
   * 批量删除爬虫配置
   * @param ids 配置ID数组
   */
  async batchDeleteCrawlerConfigs(ids: number[]): Promise<StandardResponse<void>> {
    return this.batchDelete<void>(ids)
  }

  /**
   * 复制爬虫配置
   * @param id 配置ID
   * @param params 复制时的修改参数
   */
  async duplicateCrawlerConfig(id: number, params?: Partial<CreateCrawlerParams>): Promise<StandardResponse<CrawlerConfig>> {
    return this.duplicate<CrawlerConfig>(id, params)
  }

  /**
   * 测试爬虫配置
   * @param id 配置ID
   * @param options 测试选项
   */
  async testCrawlerConfig(id: number, options?: {
    maxPages?: number
    timeout?: number
    validateOnly?: boolean
  }): Promise<StandardResponse<CrawlerTestResult>> {
    return apiAdapter.post<CrawlerTestResult>(`${this.baseUrl}/${id}/test`, options)
  }

  /**
   * 运行爬虫配置
   * @param id 配置ID
   * @param options 运行选项
   */
  async runCrawlerConfig(id: number, options?: {
    maxPages?: number
    timeout?: number
    outputFormat?: 'json' | 'csv' | 'xml'
  }): Promise<StandardResponse<{ runId: number }>> {
    return apiAdapter.post<{ runId: number }>(`${this.baseUrl}/${id}/run`, options)
  }

  /**
   * 停止爬虫运行
   * @param id 配置ID
   * @param runId 运行ID
   */
  async stopCrawlerRun(id: number, runId: number): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/${id}/runs/${runId}/stop`)
  }

  /**
   * 获取爬虫运行结果
   * @param id 配置ID
   * @param runId 运行ID
   */
  async getCrawlerRunResult(id: number, runId: number): Promise<StandardResponse<CrawlerRunResult>> {
    return apiAdapter.get<CrawlerRunResult>(`${this.baseUrl}/${id}/runs/${runId}`)
  }

  /**
   * 获取爬虫运行历史
   * @param id 配置ID
   * @param params 查询参数
   */
  async getCrawlerRunHistory(id: number, params?: {
    page?: number
    pageSize?: number
    status?: 'running' | 'completed' | 'failed' | 'cancelled'
    startDate?: string
    endDate?: string
  }): Promise<StandardResponse<{
    list: CrawlerRunResult[]
    total: number
    page: number
    pageSize: number
  }>> {
    const queryParams = params ? new URLSearchParams(params as any).toString() : ''
    return apiAdapter.get(`${this.baseUrl}/${id}/runs${queryParams ? '?' + queryParams : ''}`)
  }

  /**
   * 启用/禁用爬虫配置
   * @param id 配置ID
   * @param enabled 是否启用
   */
  async toggleCrawlerConfig(id: number, enabled: boolean): Promise<StandardResponse<void>> {
    return this.toggleStatus<void>(id, enabled ? 'active' : 'inactive')
  }

  /**
   * 验证爬虫配置
   * @param params 配置参数
   */
  async validateCrawlerConfig(params: CreateCrawlerParams): Promise<StandardResponse<{
    valid: boolean
    errors?: string[]
    warnings?: string[]
  }>> {
    return this.validate(params)
  }

  /**
   * 获取爬虫配置模板
   */
  async getCrawlerTemplates(): Promise<StandardResponse<Array<{
    id: number
    name: string
    description: string
    type: CrawlerType
    config: Partial<CreateCrawlerParams>
  }>>> {
    return apiAdapter.get(`${this.baseUrl}/templates`)
  }

  /**
   * 从模板创建爬虫配置
   * @param templateId 模板ID
   * @param params 配置参数
   */
  async createFromTemplate(
    templateId: number,
    params: Pick<CreateCrawlerParams, 'name' | 'targetUrl'>
  ): Promise<StandardResponse<CrawlerConfig>> {
    return apiAdapter.post<CrawlerConfig>(`${this.baseUrl}/templates/${templateId}/create`, params)
  }

  /**
   * 导出爬虫配置
   * @param ids 配置ID数组
   * @param format 导出格式
   */
  async exportCrawlerConfigs(
    ids: number[],
    format: 'json' | 'yaml' = 'json'
  ): Promise<StandardResponse<Blob>> {
    return this.export({ ids, format }, format as any)
  }

  /**
   * 导入爬虫配置
   * @param file 导入文件
   * @param options 导入选项
   */
  async importCrawlerConfigs(
    file: File,
    options?: {
      overwrite?: boolean
      validateOnly?: boolean
    }
  ): Promise<StandardResponse<{
    imported: number
    skipped: number
    errors: string[]
  }>> {
    return this.import(file, options)
  }

  /**
   * 获取爬虫统计数据
   * @param params 统计参数
   */
  async getCrawlerStats(params?: {
    startDate?: string
    endDate?: string
    type?: CrawlerType
  }): Promise<StandardResponse<{
    total: number
    active: number
    inactive: number
    totalRuns: number
    successRuns: number
    failedRuns: number
    successRate: number
    avgExecutionTime: number
    totalDataExtracted: number
  }>> {
    return this.getStats(params)
  }

  /**
   * 获取网站分析结果
   * @param url 网站URL
   */
  async analyzeWebsite(url: string): Promise<StandardResponse<{
    title: string
    description?: string
    keywords?: string[]
    structure: {
      headings: string[]
      links: string[]
      images: string[]
      forms: string[]
    }
    suggestedRules: ExtractionRule[]
    performance: {
      loadTime: number
      pageSize: number
      resourceCount: number
    }
  }>> {
    return apiAdapter.post(`${this.baseUrl}/analyze`, { url })
  }

  /**
   * 预览提取结果
   * @param params 配置参数
   * @param url 测试URL
   */
  async previewExtraction(
    params: Pick<CreateCrawlerParams, 'extractionRules' | 'filterRules' | 'transformRules'>,
    url: string
  ): Promise<StandardResponse<{
    data: Record<string, any>[]
    errors: string[]
    warnings: string[]
  }>> {
    return apiAdapter.post(`${this.baseUrl}/preview`, { ...params, url })
  }

  /**
   * 获取爬虫性能指标
   * @param id 配置ID
   * @param timeRange 时间范围
   */
  async getCrawlerMetrics(id: number, timeRange?: {
    startDate: string
    endDate: string
  }): Promise<StandardResponse<{
    executionTimes: number[]
    successRates: number[]
    dataVolumes: number[]
    errorRates: number[]
    timestamps: string[]
  }>> {
    const params = timeRange ? new URLSearchParams(timeRange).toString() : ''
    return apiAdapter.get(`${this.baseUrl}/${id}/metrics${params ? '?' + params : ''}`)
  }

  /**
   * 创建爬虫配置（表单数据格式）
   * @param formData 表单数据
   */
  async createCrawlerFormConfig(formData: Record<string, any>): Promise<StandardResponse<any>> {
    return apiAdapter.post<any>(`${this.baseUrl}/configs`, formData)
  }

  /**
   * 更新爬虫配置（表单数据格式）
   * @param id 配置ID
   * @param formData 表单数据
   */
  async updateCrawlerFormConfig(id: number, formData: Record<string, any>): Promise<StandardResponse<any>> {
    return apiAdapter.put<any>(`${this.baseUrl}/configs/${id}`, formData)
  }
}

// 创建并导出API服务实例
const crawlerApi = new CrawlerApiService()

export default crawlerApi