import request from '@/utils/request'

// 仪表板统计数据接口（匹配后端返回格式）
export interface DashboardStats {
  total_tasks: number
  active_crawlers: number
  completed_tasks: number
  failed_tasks: number
  success_rate: number
  avg_duration: number
}

// 任务执行趋势数据接口（匹配后端返回格式）
export interface TaskTrendData {
  dates: string[]
  success: number[]
  failed: number[]
}

// 爬虫状态数据接口（匹配后端返回格式）
export interface CrawlerInfo {
  id: string
  name: string
  status: string
  last_run: string
  success_rate: number
  total_requests: number
}

export interface CrawlerStatusData {
  crawlers: CrawlerInfo[]
}

// 系统资源监控数据接口（匹配后端返回格式）
export interface SystemResourceData {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_io: {
    bytes_recv: number
    bytes_sent: number
  }
  active_connections: number
}

// 系统资源历史数据（前端使用格式）
export interface ResourceHistoryData {
  timestamps: string[]
  cpu: number[]
  memory: number[]
  disk: number[]
  network_io: number[]
}

// 最近活动数据
export interface RecentActivity {
  id: string
  type: 'task' | 'content' | 'system' | 'error'
  title: string
  description: string
  time: string
  status: 'success' | 'error' | 'warning' | 'info'
}

// 快速操作数据
export interface QuickAction {
  name: string
  title: string
  description: string
  icon: string
  route?: string
}

// 仪表板API
export const dashboardApi = {
  // 获取仪表板统计数据
  async getStats(): Promise<DashboardStats> {
    const response = await request.get('/dashboard/stats')
    return response.data
  },

  // 获取任务执行趋势数据
  async getTaskTrend(period: '7d' | '30d' | '90d' = '7d'): Promise<TaskTrendData> {
    const response = await request.get('/dashboard/task-trend', {
      params: { period }
    })
    return response.data
  },

  // 获取爬虫状态分布数据
  async getCrawlerStatus(): Promise<CrawlerInfo[]> {
    const response = await request.get('/dashboard/crawler-status')
    return response.data
  },

  // 获取系统资源监控数据
  async getSystemResources(): Promise<SystemResourceData> {
    const response = await request.get('/dashboard/system-resources')
    return response.data
  },

  // 获取系统资源历史数据
  async getResourceHistory(period: '1h' | '6h' | '24h' = '1h'): Promise<ResourceHistoryData> {
    const response = await request.get('/dashboard/resource-history', {
      params: { period }
    })
    return response.data
  },

  // 获取最近活动数据
  async getRecentActivities(limit: number = 10): Promise<RecentActivity[]> {
    const response = await request.get('/dashboard/recent-activities', {
      params: { limit }
    })
    return response.data
  },

  // 获取快速操作配置
  async getQuickActions(): Promise<QuickAction[]> {
    const response = await request.get('/dashboard/quick-actions')
    return response.data
  },

  // 刷新活动数据
  async refreshActivities(): Promise<RecentActivity[]> {
    const response = await request.post('/dashboard/refresh-activities')
    return response.data
  }
}

export default dashboardApi