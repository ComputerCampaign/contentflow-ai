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
   * 转换仪表板统计数据 - 确保包含所有必需字段
   */
  static convertStats(backendData: any): DashboardStats {
    const defaultStats: DashboardStats = {
      total_tasks: 0,
      active_crawlers: 0,
      completed_tasks: 0,
      failed_tasks: 0,
      success_rate: 0,
      avg_duration: 0
    }

    if (!backendData || typeof backendData !== 'object') {
      return defaultStats
    }

    // 合并数据，确保所有字段都存在且为数字
    return {
      total_tasks: backendData.total_tasks ?? defaultStats.total_tasks,
      active_crawlers: backendData.active_crawlers ?? defaultStats.active_crawlers,
      completed_tasks: backendData.completed_tasks ?? defaultStats.completed_tasks,
      failed_tasks: backendData.failed_tasks ?? defaultStats.failed_tasks,
      success_rate: backendData.success_rate ?? defaultStats.success_rate,
      avg_duration: backendData.avg_duration ?? defaultStats.avg_duration
    }
  }

  /**
   * 转换爬虫状态数据 - 确保包含所有必需字段
   */
  static convertCrawlerStatus(backendData: any): CrawlerStatusData {
    const defaultData: CrawlerStatusData = {
      crawlers: []
    }

    if (!backendData) {
      return defaultData
    }

    // 如果后端直接返回数组，包装成对象
    if (Array.isArray(backendData)) {
      return {
        crawlers: backendData
      }
    }

    // 如果后端返回对象，提取crawlers字段
    if (typeof backendData === 'object') {
      return {
        crawlers: Array.isArray(backendData.crawlers) ? backendData.crawlers : defaultData.crawlers
      }
    }

    return defaultData
  }

  /**
   * 转换任务执行趋势数据 - 确保包含所有必需字段
   */
  static convertTaskTrend(backendData: any): TaskTrendData {
    const defaultData: TaskTrendData = {
      dates: [],
      success: [],
      failed: []
    }

    if (!backendData || typeof backendData !== 'object') {
      return defaultData
    }

    return {
      dates: Array.isArray(backendData.dates) ? backendData.dates : defaultData.dates,
      success: Array.isArray(backendData.success) ? backendData.success : defaultData.success,
      failed: Array.isArray(backendData.failed) ? backendData.failed : defaultData.failed
    }
  }

  /**
   * 转换系统资源数据 - 确保包含所有必需字段
   */
  static convertSystemResources(backendData: any): SystemResourceData {
    const defaultData: SystemResourceData = {
      cpu_usage: 0,
      memory_usage: 0,
      disk_usage: 0,
      network_io: {
        bytes_recv: 0,
        bytes_sent: 0
      },
      active_connections: 0
    }

    if (!backendData) {
      return defaultData
    }

    // 合并数据，确保所有字段都存在且为数字
    return {
      cpu_usage: typeof backendData.cpu_usage === 'number' ? backendData.cpu_usage : defaultData.cpu_usage,
      memory_usage: typeof backendData.memory_usage === 'number' ? backendData.memory_usage : defaultData.memory_usage,
      disk_usage: typeof backendData.disk_usage === 'number' ? backendData.disk_usage : defaultData.disk_usage,
      network_io: {
        bytes_recv: backendData.network_io?.bytes_recv || defaultData.network_io.bytes_recv,
        bytes_sent: backendData.network_io?.bytes_sent || defaultData.network_io.bytes_sent
      },
      active_connections: typeof backendData.active_connections === 'number' ? backendData.active_connections : defaultData.active_connections
    }
  }

  /**
   * 转换系统资源历史数据 - 简化版本
   */
  static convertResourceHistory(backendData: any): ResourceHistoryData {
    if (!backendData || typeof backendData !== 'object') {
      return {
        timestamps: [],
        cpu: [],
        memory: [],
        disk: [],
        network_io: []
      }
    }

    // 后端返回的是对象数组格式，需要转换为分别的数组
    if (Array.isArray(backendData)) {
      const timestamps: string[] = []
      const cpu: number[] = []
      const memory: number[] = []
      const disk: number[] = []
      const network_io: number[] = []
      
      backendData.forEach((item: any) => {
        timestamps.push(item.timestamp || '')
        cpu.push(item.cpu || 0)
        memory.push(item.memory || 0)
        disk.push(item.disk || 0)
        network_io.push(item.network_io || 0)
      })
      
      return {
        timestamps,
        cpu,
        memory,
        disk,
        network_io
      }
    }
    
    // 兼容旧格式
    return {
      timestamps: backendData.timestamps || [],
      cpu: backendData.cpu_usage || backendData.cpu || [],
      memory: backendData.memory_usage || backendData.memory || [],
      disk: backendData.disk_usage || backendData.disk || [],
      network_io: backendData.network_io || []
    }
  }

  /**
   * 转换最近活动数据 - 简化版本
   */
  static convertRecentActivities(backendData: any): RecentActivity[] {
    if (!Array.isArray(backendData)) {
      return []
    }

    // 直接返回后端数据
    return backendData
  }

  /**
   * 转换快速操作数据 - 简化版本
   */
  static convertQuickActions(backendData: any): QuickAction[] {
    if (!Array.isArray(backendData)) {
      return []
    }

    // 直接返回后端数据
    return backendData
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