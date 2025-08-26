import { BaseApiService } from './base'
import apiAdapter, { type StandardResponse } from '@/utils/api-adapter'

// 任务状态枚举
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused'

// 任务类型枚举
export type TaskType = 'crawl' | 'web_scraping' | 'crawler' | 'publish' | 'content_generation' | 'sync' | 'backup' | 'cleanup'

// 任务优先级枚举 (数字类型)
export type TaskPriority = 1 | 2 | 3 | 4 | 5

// 任务信息接口
export interface Task {
  id: string
  name: string
  description?: string
  type: TaskType
  status: TaskStatus
  priority: TaskPriority
  crawlerConfigId?: number
  crawlerConfig?: {
    id: number
    name: string
    targetUrl: string
  }
  scheduledAt?: string
  startedAt?: string
  completedAt?: string
  progress: number
  totalItems?: number
  processedItems?: number
  failedItems?: number
  successItems?: number
  errorMessage?: string
  config: Record<string, any>
  result?: Record<string, any>
  logs?: TaskLog[]
  userId: number
  createdAt: string
  updatedAt: string
  // 执行配置
  mode?: 'immediate' | 'scheduled' | 'manual'
  scheduledTime?: string
  retryCount?: number
  timeout?: number
  concurrency?: number
  delay?: number
  enableNotification?: boolean
  notificationEmail?: string
}

// 任务日志接口
export interface TaskLog {
  id: number
  taskId: string
  level: 'info' | 'warn' | 'error' | 'debug'
  message: string
  data?: Record<string, any>
  createdAt: string
}

// 创建任务参数
export interface CreateTaskParams {
  name: string
  description?: string
  type: TaskType
  priority?: TaskPriority
  crawlerConfigId?: string
  scheduledAt?: string
  config?: Record<string, any>
  // 文本生成任务专用字段
  sourceTaskId?: string
  aiModelConfigId?: string
  aiModelConfigName?: string // AI模型配置名称
  prompt?: string
  maxLength?: number
  enableNotification?: boolean
  notificationEmail?: string
}

// 更新任务参数
export interface UpdateTaskParams {
  name?: string
  description?: string
  priority?: TaskPriority
  scheduledAt?: string
  config?: Record<string, any>
  // 文本生成任务专用字段
  sourceTaskId?: string
  aiModelConfigId?: string
  aiModelConfigName?: string // AI模型配置名称
  prompt?: string
  maxLength?: number
  enableNotification?: boolean
  notificationEmail?: string
  status?: TaskStatus
  type?: TaskType
}

// 任务查询参数
export interface TaskQueryParams {
  page?: number
  pageSize?: number
  status?: TaskStatus
  type?: TaskType
  priority?: TaskPriority
  crawlerConfigId?: number
  startDate?: string
  endDate?: string
  keyword?: string
  sortBy?: 'createdAt' | 'updatedAt' | 'scheduledAt' | 'priority'
  sortOrder?: 'asc' | 'desc'
  task_type?: string
}

// 任务统计数据
export interface TaskStats {
  total: number
  pending: number
  running: number
  completed: number
  failed: number
  cancelled: number
  paused: number
  todayCreated: number
  todayCompleted: number
  successRate: number
  avgExecutionTime: number
}

// 任务执行结果
export interface TaskResult {
  taskId: string
  status: TaskStatus
  progress: number
  totalItems?: number
  processedItems?: number
  failedItems?: number
  successItems?: number
  errorMessage?: string
  result?: Record<string, any>
  executionTime?: number
  memoryUsage?: number
  cpuUsage?: number
}

/**
 * 任务管理API服务
 */
class TaskApiService extends BaseApiService {
  constructor() {
    super('/tasks')
  }

  /**
   * 获取任务列表
   * @param params 查询参数
   */
  async getTasks(params?: TaskQueryParams): Promise<StandardResponse<{
    tasks: Task[]
    pagination: {
      page: number
      per_page: number
      total: number
    }
  }>> {
    return this.getPagedList<Task>(params)
  }

  /**
   * 获取任务详情
   * @param id 任务ID
   */
  async getTask(id: string): Promise<StandardResponse<Task>> {
    return this.getById<Task>(id)
  }

  /**
   * 创建任务
   * @param params 创建参数
   */
  async createTask(params: CreateTaskParams): Promise<StandardResponse<Task>> {
    // 根据任务类型选择正确的端点和参数格式
    let endpoint = ''
    let requestData: any = {}
    
    switch (params.type) {
      case 'crawl':
      case 'web_scraping':
      case 'crawler':
        endpoint = '/tasks/crawler'
        // 转换为后端期望的格式
        requestData = {
          name: params.name,
          url: params.config?.url || '',
          crawler_config_id: params.crawlerConfigId,
          description: params.description,
          priority: params.priority || 5,
          config: params.config || {}
        }
        break
      case 'publish':
      case 'content_generation':
        endpoint = '/tasks/content-generation'
        // 转换为后端期望的格式
        requestData = {
          name: params.name,
          source_task_id: params.sourceTaskId,
          ai_model_config_name: params.aiModelConfigName, // 必须是模型配置的名称
          description: params.description,
          priority: params.priority || 2,
          config: {
            prompt: params.prompt,
            max_length: params.maxLength || 1000,
            enable_notification: params.enableNotification || false,
            notification_email: params.notificationEmail || '',
            ...params.config
          }
        }
        break
      default:
        throw new Error(`不支持的任务类型: ${params.type}`)
    }
    
    return apiAdapter.post<Task>(endpoint, requestData)
  }

  /**
   * 更新任务
   * @param id 任务ID
   * @param params 更新参数
   */
  async updateTask(id: string, params: UpdateTaskParams): Promise<StandardResponse<Task>> {
    return this.update<Task>(id, params)
  }

  /**
   * 删除任务
   * @param id 任务ID
   */
  async deleteTask(id: string): Promise<StandardResponse<void>> {
    return this.delete<void>(id)
  }

  /**
   * 批量删除任务
   * @param ids 任务ID数组
   */
  async batchDeleteTasks(ids: string[]): Promise<StandardResponse<void>> {
    return this.batchDelete<void>(ids)
  }

  /**
   * 执行任务
   * @param id 任务ID
   */
  async executeTask(id: string): Promise<StandardResponse<TaskResult>> {
    return apiAdapter.post<TaskResult>(`${this.baseUrl}/${id}/execute`)
  }

  /**
   * 暂停任务
   * @param id 任务ID
   */
  async pauseTask(id: string): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/${id}/pause`)
  }

  /**
   * 恢复任务
   * @param id 任务ID
   */
  async resumeTask(id: string): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/${id}/resume`)
  }

  /**
   * 取消任务
   * @param id 任务ID
   */
  async cancelTask(id: string): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/${id}/cancel`)
  }

  /**
   * 重试任务
   * @param id 任务ID
   */
  async retryTask(id: string): Promise<StandardResponse<TaskResult>> {
    return apiAdapter.post<TaskResult>(`${this.baseUrl}/${id}/retry`)
  }

  /**
   * 复制任务
   * @param id 任务ID
   * @param params 复制时的修改参数
   */
  async duplicateTask(id: string, params?: Partial<CreateTaskParams>): Promise<StandardResponse<Task>> {
    return this.duplicate<Task>(id, params)
  }

  /**
   * 批量执行任务
   * @param ids 任务ID数组
   */
  async batchExecuteTasks(ids: string[]): Promise<StandardResponse<TaskResult[]>> {
    return this.batchAction<TaskResult[]>('execute', ids)
  }

  /**
   * 批量暂停任务
   * @param ids 任务ID数组
   */
  async batchPauseTasks(ids: string[]): Promise<StandardResponse<void>> {
    return this.batchAction<void>('pause', ids)
  }

  /**
   * 批量取消任务
   * @param ids 任务ID数组
   */
  async batchCancelTasks(ids: string[]): Promise<StandardResponse<void>> {
    return this.batchAction<void>('cancel', ids)
  }

  /**
   * 获取任务日志
   * @param id 任务ID
   * @param params 查询参数
   */
  async getTaskLogs(id: string, params?: {
    page?: number
    pageSize?: number
    level?: 'info' | 'warn' | 'error' | 'debug'
    startDate?: string
    endDate?: string
  }): Promise<StandardResponse<{
    list: TaskLog[]
    total: number
    page: number
    pageSize: number
  }>> {
    const queryParams = params ? new URLSearchParams(params as any).toString() : ''
    return apiAdapter.get(`${this.baseUrl}/${id}/logs${queryParams ? '?' + queryParams : ''}`)
  }

  /**
   * 获取任务结果
   * @param id 任务ID
   * @param params 查询参数
   */
  async getTaskResults(id: string, params?: {
    page?: number
    pageSize?: number
  }): Promise<StandardResponse<{
    task_type: string
    execution_stats: {
      items_processed: number
      items_success: number
      items_failed: number
      start_time: string
      end_time: string
      duration: number
    }
    results: any[]
    total: number
    page: number
    pageSize: number
  }>> {
    const queryParams = params ? new URLSearchParams(params as any).toString() : ''
    return apiAdapter.get(`${this.baseUrl}/${id}/results${queryParams ? '?' + queryParams : ''}`)
  }

  /**
   * 获取任务统计数据
   * @param params 统计参数
   */
  async getTaskStats(params?: {
    startDate?: string
    endDate?: string
    type?: TaskType
    crawlerConfigId?: number
  }): Promise<StandardResponse<TaskStats>> {
    return this.getStats<TaskStats>(params)
  }

  /**
   * 获取任务执行状态
   * @param id 任务ID
   */
  async getTaskStatus(id: string): Promise<StandardResponse<TaskResult>> {
    return apiAdapter.get<TaskResult>(`${this.baseUrl}/${id}/status`)
  }

  /**
   * 获取正在运行的任务列表
   */
  async getRunningTasks(): Promise<StandardResponse<Task[]>> {
    return apiAdapter.get<Task[]>(`${this.baseUrl}/running`)
  }

  /**
   * 获取任务队列状态
   */
  async getQueueStatus(): Promise<StandardResponse<{
    pending: number
    running: number
    maxConcurrent: number
    queueLength: number
  }>> {
    return apiAdapter.get(`${this.baseUrl}/queue/status`)
  }

  /**
   * 清空任务队列
   */
  async clearQueue(): Promise<StandardResponse<void>> {
    return apiAdapter.post<void>(`${this.baseUrl}/queue/clear`)
  }

  /**
   * 设置任务优先级
   * @param id 任务ID
   * @param priority 优先级
   */
  async setTaskPriority(id: string, priority: TaskPriority): Promise<StandardResponse<void>> {
    return apiAdapter.put<void>(`${this.baseUrl}/${id}/priority`, { priority })
  }

  /**
   * 获取任务模板列表
   */
  async getTaskTemplates(): Promise<StandardResponse<Array<{
    id: number
    name: string
    description: string
    type: TaskType
    config: Record<string, any>
  }>>> {
    return apiAdapter.get(`${this.baseUrl}/templates`)
  }

  /**
   * 从模板创建任务
   * @param templateId 模板ID
   * @param params 任务参数
   */
  async createTaskFromTemplate(
    templateId: string,
    params: Omit<CreateTaskParams, 'type' | 'config'>
  ): Promise<StandardResponse<Task>> {
    return apiAdapter.post<Task>(`${this.baseUrl}/templates/${templateId}/create`, params)
  }

  /**
   * 导出任务数据
   * @param params 导出参数
   */
  async exportTasks(params?: {
    ids?: string[]
    status?: TaskStatus
    type?: TaskType
    startDate?: string
    endDate?: string
    format?: 'csv' | 'excel' | 'json'
  }): Promise<StandardResponse<Blob>> {
    return this.export(params, params?.format)
  }

  /**
   * 获取任务性能指标
   * @param id 任务ID
   */
  async getTaskMetrics(id: string): Promise<StandardResponse<{
    executionTime: number
    memoryUsage: number
    cpuUsage: number
    networkUsage: number
    diskUsage: number
    errorRate: number
    throughput: number
  }>> {
    return apiAdapter.get(`${this.baseUrl}/${id}/metrics`)
  }

  /**
   * 获取任务执行命令
   * @param id 任务ID
   */
  async getTaskCommand(id: string): Promise<StandardResponse<{ command: string }>> {
    return apiAdapter.get(`${this.baseUrl}/${id}/command`)
  }
}

// 创建并导出API服务实例
const taskApi = new TaskApiService()

export default taskApi