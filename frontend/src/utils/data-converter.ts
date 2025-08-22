/**
 * Dashboard数据转换器
 * 用于将后端返回的数据格式转换为前端期望的格式
 */

import type { 
  DashboardStats, 
  TaskTrendData, 
  CrawlerStatusData, 
  SystemResourceData,
  ResourceHistoryData,
  RecentActivity,
  QuickAction
} from '@/api/dashboard'

export class DashboardDataConverter {
  /**
   * 转换统计数据
   * 后端返回: { active_crawlers, completed_tasks, failed_tasks, success_rate, avg_duration }
   * 前端期望: { totalTasks, activeCrawlers, todayGenerated, systemLoad, ...trends }
   */
  static convertStats(backendData: any): DashboardStats {
    // 添加空值检查
    if (!backendData) {
      return {
        totalTasks: 0,
        activeCrawlers: 0,
        todayGenerated: 0,
        systemLoad: 0,
        taskTrend: {
          period: '7天',
          change: '0%',
          trend: 'up' as const
        },
        crawlerTrend: {
          period: '7天',
          change: '0%',
          trend: 'up' as const
        },
        contentTrend: {
          period: '7天',
          change: '0%',
          trend: 'up' as const
        },
        systemTrend: {
          period: '7天',
          change: '0%',
          trend: 'up' as const
        }
      }
    }

    // 根据后端实际返回的数据格式进行转换
    const totalTasks = (backendData.total_tasks || 0)
    const completedTasks = (backendData.completed_tasks || 0)
    const failedTasks = (backendData.failed_tasks || 0)
    const activeCrawlers = (backendData.active_crawlers || 0)
    const successRate = (backendData.success_rate || 0)
    const avgDuration = (backendData.avg_duration || 0)
    
    const systemLoad = Math.round(successRate) // 直接使用成功率作为系统负载
    const todayGenerated = Math.round(completedTasks * 0.8) // 假设今日生成内容为完成任务的80%
    
    // 计算趋势数据
    const taskTrendValue = DashboardDataConverter.calculateTrend(completedTasks, failedTasks)
    const crawlerTrendValue = DashboardDataConverter.calculateTrend(activeCrawlers, 0)
    const contentTrendValue = DashboardDataConverter.calculateTrend(todayGenerated, 0)
    const systemTrendValue = DashboardDataConverter.calculateTrend(systemLoad, 0)
    
    return {
      totalTasks,
      activeCrawlers,
      todayGenerated,
      systemLoad,
      taskTrend: {
        period: '7天',
        change: `${taskTrendValue}%`,
        trend: taskTrendValue >= 0 ? 'up' : 'down'
      },
      crawlerTrend: {
        period: '7天',
        change: `${crawlerTrendValue}%`,
        trend: crawlerTrendValue >= 0 ? 'up' : 'down'
      },
      contentTrend: {
        period: '7天',
        change: `${contentTrendValue}%`,
        trend: contentTrendValue >= 0 ? 'up' : 'down'
      },
      systemTrend: {
        period: '7天',
        change: `${systemTrendValue}%`,
        trend: systemTrendValue >= 0 ? 'up' : 'down'
      }
    }
  }

  /**
   * 转换爬虫状态数据
   */
  static convertCrawlerStatus(backendData: any): CrawlerStatusData {
    if (!backendData) {
      return {
        running: 0,
        idle: 0,
        error: 0,
        maintenance: 0
      }
    }

    // 根据后端实际返回的数据格式进行转换
    return {
      running: backendData.running || 0,
      idle: backendData.idle || 0,
      error: backendData.error || 0,
      maintenance: backendData.maintenance || 0
    }
  }

  /**
   * 转换任务趋势数据
   */
  static convertTaskTrend(backendData: any): TaskTrendData {
    if (!backendData) {
      return {
        labels: [],
        completedTasks: [],
        failedTasks: []
      }
    }

    // 根据后端实际返回的数据格式进行转换
    return {
      labels: backendData.labels || [],
      completedTasks: backendData.completed_tasks || [],
      failedTasks: backendData.failed_tasks || []
    }
  }

  /**
   * 转换系统资源数据
   */
  static convertSystemResources(backendData: any): SystemResourceData {
    if (!backendData) {
      return {
        cpu: 0,
        memory: 0,
        disk: 0,
        network: 0
      }
    }

    // 根据后端实际返回的数据格式进行转换
    return {
      cpu: Math.round(backendData.cpu || 0),
      memory: Math.round(backendData.memory || 0),
      disk: Math.round(backendData.disk || 0),
      network: Math.round(backendData.network || 0)
    }
  }

  /**
   * 转换系统资源历史数据
   */
  static convertResourceHistory(backendData: any): ResourceHistoryData {
    if (!backendData || typeof backendData !== 'object') {
      return {
        timestamps: [],
        cpu: [],
        memory: [],
        disk: [],
        network: []
      }
    }

    // 根据后端实际返回的数据格式进行转换
    return {
      timestamps: backendData.timestamps || [],
      cpu: backendData.cpu || [],
      memory: backendData.memory || [],
      disk: backendData.disk || [],
      network: backendData.network || []
    }
  }

  /**
   * 转换最近活动数据
   */
  static convertRecentActivities(backendData: any): RecentActivity[] {
    if (!Array.isArray(backendData)) {
      return []
    }

    return backendData.map((activity: any) => ({
      id: activity.id || String(Math.random()),
      type: activity.type || 'info',
      title: activity.title || '未知活动',
      description: activity.description || '',
      time: activity.time || new Date().toISOString(),
      status: activity.status || 'info'
    }))
  }

  /**
   * 转换快速操作数据
   */
  static convertQuickActions(backendData: any): QuickAction[] {
    if (!Array.isArray(backendData)) {
      return []
    }

    return backendData.map((action: any) => ({
      name: action.name || '',
      title: action.title || '',
      description: action.description || '',
      icon: action.icon || 'default',
      route: action.route
    }))
  }

  // 辅助方法
  private static parsePercentage(value: any): number {
    if (typeof value === 'number') {
      return Math.round(value)
    }
    if (typeof value === 'string') {
      const num = parseFloat(value.replace('%', ''))
      return isNaN(num) ? 0 : Math.round(num)
    }
    return 0
  }

  private static calculateTrendChange(completed: number = 0, failed: number = 0): string {
    const total = completed + failed
    if (total === 0) return '0%'
    const successRate = (completed / total) * 100
    return successRate > 50 ? `+${Math.round(successRate - 50)}%` : `-${Math.round(50 - successRate)}%`
  }

  private static calculateTrendDirection(successRate: number = 0): 'up' | 'down' {
    return successRate > 50 ? 'up' : 'down'
  }

  private static calculateCrawlerTrendChange(activeCrawlers: number = 0): string {
    // 简单的趋势计算，实际应该基于历史数据
    return activeCrawlers > 0 ? `+${activeCrawlers}` : '0'
  }

  private static calculateContentTrendChange(todayGenerated: number = 0): string {
    // 简单的趋势计算
    return todayGenerated > 0 ? `+${todayGenerated}` : '0'
  }

  private static calculateSystemTrendChange(systemLoad: number = 0): string {
    // 系统负载趋势（负载低表示性能好）
    return systemLoad < 50 ? '+良好' : '-需优化'
  }

  /**
   * 计算趋势百分比
   * @param current 当前值
   * @param previous 之前的值
   * @returns 趋势百分比
   */
  private static calculateTrend(current: number, previous: number): number {
    if (previous === 0) {
      return current > 0 ? 100 : 0
    }
    return Math.round(((current - previous) / previous) * 100)
  }
}

export default DashboardDataConverter