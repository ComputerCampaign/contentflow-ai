<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="stat in statsCards"
        :key="stat.title"
        class="stat-card"
        :class="stat.type"
      >
        <div class="stat-icon">
          <component :is="stat.icon" class="icon" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-change" :class="stat.trend">
            <ArrowUp v-if="stat.trend === 'up'" class="trend-icon" />
            <ArrowDown v-if="stat.trend === 'down'" class="trend-icon" />
            {{ stat.change }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 任务执行趋势 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>任务执行趋势</h3>
          <el-select v-model="taskTrendPeriod" size="small" style="width: 120px" @change="handleTaskTrendChange">
            <el-option label="最近7天" value="7d" />
            <el-option label="最近30天" value="30d" />
            <el-option label="最近90天" value="90d" />
          </el-select>
        </div>
        <div class="chart-container">
          <canvas ref="taskTrendChartRef" />
        </div>
      </div>

      <!-- 爬虫状态分布 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>爬虫状态分布</h3>
        </div>
        <div class="chart-container">
          <canvas ref="crawlerStatusChartRef" />
        </div>
      </div>

      <!-- 系统资源监控 -->
      <div class="chart-card full-width">
        <div class="card-header">
          <h3>系统资源监控</h3>
          <div class="resource-indicators">
            <div class="indicator">
              <span class="label">CPU</span>
              <el-progress
                :percentage="systemResources?.cpu || 0"
                :color="getResourceColor(systemResources?.cpu || 0)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="value">{{ systemResources?.cpu || 0 }}%</span>
            </div>
            <div class="indicator">
              <span class="label">内存</span>
              <el-progress
                :percentage="systemResources?.memory || 0"
                :color="getResourceColor(systemResources?.memory || 0)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="value">{{ systemResources?.memory || 0 }}%</span>
            </div>
            <div class="indicator">
              <span class="label">磁盘</span>
              <el-progress
                :percentage="systemResources?.disk || 0"
                :color="getResourceColor(systemResources?.disk || 0)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="value">{{ systemResources?.disk || 0 }}%</span>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="resourceChartRef" />
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="activity-section">
      <div class="section-header">
        <h3>最近活动</h3>
        <el-button type="text" @click="handleRefreshActivities" :loading="loading.activities">
          <RefreshCw class="refresh-icon" />
          刷新
        </el-button>
      </div>
      
      <div class="activity-list">
        <div
          v-for="activity in recentActivities"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            <component :is="getActivityIcon(activity.type)" class="icon" />
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-description">{{ activity.description }}</div>
            <div class="activity-time">{{ formatTime(activity.time) }}</div>
          </div>
          <div class="activity-status" :class="activity.status">
            {{ getStatusText(activity.status) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h3>快速操作</h3>
      <div class="actions-grid">
        <div
          v-for="action in quickActions"
          :key="action.name"
          class="action-card"
          @click="handleQuickAction(action)"
        >
          <div class="action-icon">
            <component :is="getActionIcon(action.icon)" class="icon" />
          </div>
          <div class="action-title">{{ action.title }}</div>
          <div class="action-description">{{ action.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { useDashboardStore } from '@/stores/dashboard'
import type { QuickAction } from '@/api/dashboard'

// 图标导入
import {
  ArrowUp,
  ArrowDown,
  RefreshCw,
  CheckCircle,
  Activity,
  Settings,
  AlertTriangle,
  Plus,
  FileText,
  BarChart3,
  Server,
  Bug,
  Zap
} from 'lucide-vue-next'

// 注册 Chart.js 组件
Chart.register(...registerables)

const router = useRouter()
const dashboardStore = useDashboardStore()

// 响应式数据
const taskTrendPeriod = ref<'7d' | '30d' | '90d'>('7d')

// Chart 实例引用
const taskTrendChartRef = ref<HTMLCanvasElement>()
const crawlerStatusChartRef = ref<HTMLCanvasElement>()
const resourceChartRef = ref<HTMLCanvasElement>()

// Chart 实例
const charts: Record<string, Chart> = {}

// 从 store 获取数据
const { 
  stats, 
  taskTrend, 
  crawlerStatus, 
  systemResources, 
  resourceHistory, 
  recentActivities, 
  quickActions, 
  loading 
} = storeToRefs(dashboardStore)

// 统计卡片数据
const statsCards = computed(() => {
  if (!stats.value) return []
  
  return [
    {
      title: '总任务数',
      value: stats.value.totalTasks.toLocaleString(),
      change: stats.value.taskTrend.change,
      trend: stats.value.taskTrend.trend,
      icon: CheckCircle,
      type: 'primary'
    },
    {
      title: '活跃爬虫',
      value: stats.value.activeCrawlers.toString(),
      change: stats.value.crawlerTrend.change,
      trend: stats.value.crawlerTrend.trend,
      icon: Bug,
      type: 'success'
    },
    {
      title: '今日生成',
      value: stats.value.todayGenerated.toString(),
      change: stats.value.contentTrend.change,
      trend: stats.value.contentTrend.trend,
      icon: FileText,
      type: 'warning'
    },
    {
      title: '系统负载',
      value: `${stats.value.systemLoad}%`,
      change: stats.value.systemTrend.change,
      trend: stats.value.systemTrend.trend,
      icon: Server,
      type: 'info'
    }
  ]
})

// 方法
const getResourceColor = (percentage: number) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getActivityIcon = (type: string) => {
  const icons = {
    task: CheckCircle,
    content: FileText,
    system: Settings,
    error: AlertTriangle
  }
  return icons[type as keyof typeof icons] || Activity
}

const getActionIcon = (iconName: string) => {
  const icons = {
    'plus-circle': Plus,
    'file-text': FileText,
    'bar-chart': BarChart3,
    'activity': Activity,
    'zap': Zap
  }
  return icons[iconName as keyof typeof icons] || Activity
}

const getStatusText = (status: string) => {
  const texts = {
    success: '成功',
    error: '失败',
    warning: '警告',
    info: '信息'
  }
  return texts[status as keyof typeof texts] || '未知'
}

const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

const handleRefreshActivities = async () => {
  await dashboardStore.refreshActivities()
}

const handleTaskTrendChange = async () => {
  await dashboardStore.fetchTaskTrend(taskTrendPeriod.value)
  updateTaskTrendChart()
}

const handleQuickAction = (action: QuickAction) => {
  if (action.route) {
    router.push(action.route)
  } else {
    switch (action.name) {
      case 'new-task':
        router.push('/tasks/create')
        break
      case 'view-logs':
        router.push('/monitor')
        break
      case 'system-status':
        router.push('/monitor')
        break
      default:
        ElMessage.info(`执行操作: ${action.title}`)
    }
  }
}

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // 任务执行趋势图
  if (taskTrendChartRef.value && taskTrend.value) {
    charts.taskTrend = new Chart(taskTrendChartRef.value, {
      type: 'line',
      data: {
        labels: taskTrend.value.labels,
        datasets: [{
          label: '完成任务',
          data: taskTrend.value.completedTasks,
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        }, {
          label: '失败任务',
          data: taskTrend.value.failedTasks,
          borderColor: '#f56c6c',
          backgroundColor: 'rgba(245, 108, 108, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  }
  
  // 爬虫状态分布图
  if (crawlerStatusChartRef.value && crawlerStatus.value) {
    charts.crawlerStatus = new Chart(crawlerStatusChartRef.value, {
      type: 'doughnut',
      data: {
        labels: ['运行中', '空闲', '错误', '维护'],
        datasets: [{
          data: [
            crawlerStatus.value.running,
            crawlerStatus.value.idle,
            crawlerStatus.value.error,
            crawlerStatus.value.maintenance
          ],
          backgroundColor: [
            '#67c23a',
            '#409eff',
            '#f56c6c',
            '#e6a23c'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    })
  }
  
  // 系统资源监控图
  if (resourceChartRef.value && resourceHistory.value) {
    charts.resource = new Chart(resourceChartRef.value, {
      type: 'line',
      data: {
        labels: resourceHistory.value.timestamps,
        datasets: [{
          label: 'CPU 使用率',
          data: resourceHistory.value.cpu,
          borderColor: '#409eff',
          backgroundColor: 'rgba(64, 158, 255, 0.1)',
          tension: 0.4
        }, {
          label: '内存使用率',
          data: resourceHistory.value.memory,
          borderColor: '#67c23a',
          backgroundColor: 'rgba(103, 194, 58, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    })
  }
}

// 更新任务趋势图表
const updateTaskTrendChart = () => {
  if (charts.taskTrend && taskTrend.value) {
    charts.taskTrend.data.labels = taskTrend.value.labels
    charts.taskTrend.data.datasets[0].data = taskTrend.value.completedTasks
    charts.taskTrend.data.datasets[1].data = taskTrend.value.failedTasks
    charts.taskTrend.update()
  }
}

// 定时器
let resourceTimer: number | null = null

// 生命周期
onMounted(async () => {
  // 初始化仪表板数据
  await dashboardStore.initDashboard()
  
  // 初始化图表
  await initCharts()
  
  // 定时更新系统资源数据
  resourceTimer = setInterval(() => {
    dashboardStore.fetchSystemResources()
  }, 30000) // 30秒更新一次
})

onUnmounted(() => {
  // 销毁图表
  Object.values(charts).forEach(chart => {
    if (chart) {
      chart.destroy()
    }
  })
  
  // 清除定时器
  if (resourceTimer) {
    clearInterval(resourceTimer)
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 0;
}

// 统计卡片网格
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--el-box-shadow);
  }
  
  &.primary {
    border-left-color: var(--el-color-primary);
  }
  
  &.success {
    border-left-color: var(--el-color-success);
  }
  
  &.warning {
    border-left-color: var(--el-color-warning);
  }
  
  &.info {
    border-left-color: var(--el-color-info);
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20px;
    background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
    
    .icon {
      width: 24px;
      height: 24px;
      color: white;
    }
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
    }
    
    .stat-title {
      font-size: 14px;
      color: var(--el-text-color-regular);
      margin-bottom: 8px;
    }
    
    .stat-change {
      font-size: 12px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
      
      .trend-icon {
        width: 12px;
        height: 12px;
      }
      
      &.up {
        color: var(--el-color-success);
      }
      
      &.down {
        color: var(--el-color-danger);
      }
    }
  }
}

// 图表网格
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--el-box-shadow-light);
  
  &.full-width {
    grid-column: 1 / -1;
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }
  
  .chart-container {
    height: 300px;
    position: relative;
  }
  
  .resource-indicators {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
    
    .indicator {
      flex: 1;
      
      .label {
        font-size: 12px;
        color: var(--el-text-color-regular);
        margin-bottom: 4px;
        display: block;
      }
      
      .value {
        font-size: 12px;
        font-weight: 500;
        color: var(--el-text-color-primary);
        margin-left: 8px;
      }
    }
  }
}

// 活动区域
.activity-section {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--el-box-shadow-light);
  margin-bottom: 24px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
    
    .refresh-icon {
      width: 14px;
      height: 14px;
      margin-right: 4px;
    }
  }
}

.activity-list {
  .activity-item {
    display: flex;
    align-items: flex-start;
    padding: 16px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    
    &:last-child {
      border-bottom: none;
    }
    
    .activity-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      
      .icon {
        width: 18px;
        height: 18px;
      }
      
      &.task {
        background: rgba(64, 158, 255, 0.1);
        color: var(--el-color-primary);
      }
      
      &.content {
        background: rgba(103, 194, 58, 0.1);
        color: var(--el-color-success);
      }
      
      &.system {
        background: rgba(230, 162, 60, 0.1);
        color: var(--el-color-warning);
      }
      
      &.error {
        background: rgba(245, 108, 108, 0.1);
        color: var(--el-color-danger);
      }
    }
    
    .activity-content {
      flex: 1;
      
      .activity-title {
        font-weight: 500;
        color: var(--el-text-color-primary);
        margin-bottom: 4px;
      }
      
      .activity-description {
        color: var(--el-text-color-regular);
        font-size: 13px;
        line-height: 1.4;
        margin-bottom: 8px;
      }
      
      .activity-time {
        color: var(--el-text-color-secondary);
        font-size: 12px;
      }
    }
    
    .activity-status {
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      
      &.success {
        background: rgba(103, 194, 58, 0.1);
        color: var(--el-color-success);
      }
      
      &.error {
        background: rgba(245, 108, 108, 0.1);
        color: var(--el-color-danger);
      }
      
      &.warning {
        background: rgba(230, 162, 60, 0.1);
        color: var(--el-color-warning);
      }
      
      &.info {
        background: rgba(64, 158, 255, 0.1);
        color: var(--el-color-info);
      }
    }
  }
}

// 快速操作
.quick-actions {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--el-box-shadow-light);
  
  h3 {
    margin: 0 0 20px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-card {
  padding: 20px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    transform: translateY(-2px);
    box-shadow: var(--el-box-shadow-light);
  }
  
  .action-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    
    .icon {
      width: 20px;
      height: 20px;
      color: white;
    }
  }
  
  .action-title {
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-bottom: 8px;
  }
  
  .action-description {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card {
    .stat-icon {
      width: 48px;
      height: 48px;
      margin-right: 16px;
      
      .icon {
        width: 20px;
        height: 20px;
      }
    }
    
    .stat-content {
      .stat-value {
        font-size: 24px;
      }
    }
  }
}
</style>