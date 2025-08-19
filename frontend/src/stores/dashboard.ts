import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardApi, type DashboardStats, type TaskTrendData, type CrawlerStatusData, type SystemResourceData, type ResourceHistoryData, type RecentActivity, type QuickAction } from '@/api/dashboard'
import { ElMessage } from 'element-plus'

export const useDashboardStore = defineStore('dashboard', () => {
  // 状态数据
  const stats = ref<DashboardStats | null>(null)
  const taskTrend = ref<TaskTrendData | null>(null)
  const crawlerStatus = ref<CrawlerStatusData | null>(null)
  const systemResources = ref<SystemResourceData | null>(null)
  const resourceHistory = ref<ResourceHistoryData | null>(null)
  const recentActivities = ref<RecentActivity[]>([])
  const quickActions = ref<QuickAction[]>([])
  
  // 加载状态
  const loading = ref({
    stats: false,
    taskTrend: false,
    crawlerStatus: false,
    systemResources: false,
    resourceHistory: false,
    activities: false,
    quickActions: false
  })

  // 计算属性
  const isLoading = computed(() => {
    return Object.values(loading.value).some(status => status)
  })

  const hasData = computed(() => {
    return stats.value !== null
  })

  // 获取仪表板统计数据
  const fetchStats = async () => {
    try {
      loading.value.stats = true
      const response = await dashboardApi.getStats()
      stats.value = response
    } catch (error) {
      console.error('获取统计数据失败:', error)
      ElMessage.error('获取统计数据失败')
    } finally {
      loading.value.stats = false
    }
  }

  // 获取任务执行趋势数据
  const fetchTaskTrend = async (period: '7d' | '30d' | '90d' = '7d') => {
    try {
      loading.value.taskTrend = true
      const response = await dashboardApi.getTaskTrend(period)
      taskTrend.value = response
    } catch (error) {
      console.error('获取任务趋势数据失败:', error)
      ElMessage.error('获取任务趋势数据失败')
    } finally {
      loading.value.taskTrend = false
    }
  }

  // 获取爬虫状态分布数据
  const fetchCrawlerStatus = async () => {
    try {
      loading.value.crawlerStatus = true
      const response = await dashboardApi.getCrawlerStatus()
      crawlerStatus.value = response
    } catch (error) {
      console.error('获取爬虫状态数据失败:', error)
      ElMessage.error('获取爬虫状态数据失败')
    } finally {
      loading.value.crawlerStatus = false
    }
  }

  // 获取系统资源监控数据
  const fetchSystemResources = async () => {
    try {
      loading.value.systemResources = true
      const response = await dashboardApi.getSystemResources()
      systemResources.value = response
    } catch (error) {
      console.error('获取系统资源数据失败:', error)
      ElMessage.error('获取系统资源数据失败')
    } finally {
      loading.value.systemResources = false
    }
  }

  // 获取系统资源历史数据
  const fetchResourceHistory = async (period: '1h' | '6h' | '24h' = '1h') => {
    try {
      loading.value.resourceHistory = true
      const response = await dashboardApi.getResourceHistory(period)
      resourceHistory.value = response
    } catch (error) {
      console.error('获取资源历史数据失败:', error)
      ElMessage.error('获取资源历史数据失败')
    } finally {
      loading.value.resourceHistory = false
    }
  }

  // 获取最近活动数据
  const fetchRecentActivities = async (limit: number = 10) => {
    try {
      loading.value.activities = true
      const response = await dashboardApi.getRecentActivities(limit)
      recentActivities.value = response
    } catch (error) {
      console.error('获取最近活动数据失败:', error)
      ElMessage.error('获取最近活动数据失败')
    } finally {
      loading.value.activities = false
    }
  }

  // 获取快速操作配置
  const fetchQuickActions = async () => {
    try {
      loading.value.quickActions = true
      const response = await dashboardApi.getQuickActions()
      quickActions.value = response
    } catch (error) {
      console.error('获取快速操作配置失败:', error)
      ElMessage.error('获取快速操作配置失败')
    } finally {
      loading.value.quickActions = false
    }
  }

  // 初始化仪表板数据
  const initDashboard = async () => {
    await Promise.all([
      fetchStats(),
      fetchTaskTrend(),
      fetchCrawlerStatus(),
      fetchSystemResources(),
      fetchResourceHistory(),
      fetchRecentActivities(),
      fetchQuickActions()
    ])
  }

  // 刷新仪表板数据
  const refreshDashboard = async () => {
    await Promise.all([
      fetchStats(),
      fetchTaskTrend(),
      fetchCrawlerStatus(),
      fetchSystemResources(),
      fetchResourceHistory(),
      fetchRecentActivities(),
      fetchQuickActions()
    ])
  }

  // 刷新活动数据
  const refreshActivities = async () => {
    await fetchRecentActivities()
  }

  // 重置状态
  const resetState = () => {
    stats.value = null
    taskTrend.value = null
    crawlerStatus.value = null
    systemResources.value = null
    resourceHistory.value = null
    recentActivities.value = []
    quickActions.value = []
    
    // 重置加载状态
    Object.keys(loading.value).forEach(key => {
      loading.value[key as keyof typeof loading.value] = false
    })
  }

  return {
    // 状态
    stats,
    taskTrend,
    crawlerStatus,
    systemResources,
    resourceHistory,
    recentActivities,
    quickActions,
    loading,
    
    // 计算属性
    isLoading,
    hasData,
    
    // 方法
    fetchStats,
    fetchTaskTrend,
    fetchCrawlerStatus,
    fetchSystemResources,
    fetchResourceHistory,
    fetchRecentActivities,
    fetchQuickActions,
    initDashboard,
    refreshDashboard,
    refreshActivities,
    resetState
  }
})

export default useDashboardStore