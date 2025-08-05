<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="stat in stats"
        :key="stat.title"
        class="stat-card"
        :class="stat.type"
      >
        <div class="stat-icon">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-change" :class="stat.trend">
            <i :class="getTrendIcon(stat.trend)"></i>
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
          <el-select v-model="taskTrendPeriod" size="small" style="width: 120px">
            <el-option label="最近7天" value="7d"></el-option>
            <el-option label="最近30天" value="30d"></el-option>
            <el-option label="最近90天" value="90d"></el-option>
          </el-select>
        </div>
        <div class="chart-container">
          <canvas ref="taskTrendChart"></canvas>
        </div>
      </div>

      <!-- 爬虫状态分布 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>爬虫状态分布</h3>
        </div>
        <div class="chart-container">
          <canvas ref="crawlerStatusChart"></canvas>
        </div>
      </div>

      <!-- 内容生成统计 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>内容生成统计</h3>
        </div>
        <div class="chart-container">
          <canvas ref="contentStatsChart"></canvas>
        </div>
      </div>

      <!-- 系统资源监控 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>系统资源监控</h3>
          <div class="resource-indicators">
            <div class="indicator">
              <span class="label">CPU</span>
              <el-progress
                :percentage="systemResources.cpu"
                :color="getResourceColor(systemResources.cpu)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="value">{{ systemResources.cpu }}%</span>
            </div>
            <div class="indicator">
              <span class="label">内存</span>
              <el-progress
                :percentage="systemResources.memory"
                :color="getResourceColor(systemResources.memory)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="value">{{ systemResources.memory }}%</span>
            </div>
            <div class="indicator">
              <span class="label">磁盘</span>
              <el-progress
                :percentage="systemResources.disk"
                :color="getResourceColor(systemResources.disk)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="value">{{ systemResources.disk }}%</span>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="resourceChart"></canvas>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="activity-section">
      <div class="section-header">
        <h3>最近活动</h3>
        <el-button type="text" @click="refreshActivities">
          <i class="fas fa-sync-alt"></i>
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
            <i :class="getActivityIcon(activity.type)"></i>
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
            <i :class="action.icon"></i>
          </div>
          <div class="action-title">{{ action.title }}</div>
          <div class="action-description">{{ action.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

// 注册 Chart.js 组件
Chart.register(...registerables)

const router = useRouter()

// 响应式数据
const taskTrendPeriod = ref('7d')
const systemResources = ref({
  cpu: 45,
  memory: 68,
  disk: 32
})

// 统计数据
const stats = ref([
  {
    title: '总任务数',
    value: '1,234',
    change: '+12.5%',
    trend: 'up',
    icon: 'fas fa-tasks',
    type: 'primary'
  },
  {
    title: '活跃爬虫',
    value: '23',
    change: '+5.2%',
    trend: 'up',
    icon: 'fas fa-spider',
    type: 'success'
  },
  {
    title: '今日生成',
    value: '89',
    change: '-2.1%',
    trend: 'down',
    icon: 'fas fa-file-alt',
    type: 'warning'
  },
  {
    title: '系统负载',
    value: '45%',
    change: '+8.3%',
    trend: 'up',
    icon: 'fas fa-server',
    type: 'info'
  }
])

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    type: 'task',
    title: '爬虫任务完成',
    description: '技术博客采集任务已成功完成，共采集 156 篇文章',
    time: new Date(),
    status: 'success'
  },
  {
    id: 2,
    type: 'content',
    title: 'AI 内容生成',
    description: '基于采集内容生成了 23 篇原创文章',
    time: new Date(Date.now() - 1800000),
    status: 'success'
  },
  {
    id: 3,
    type: 'system',
    title: '系统更新',
    description: '爬虫引擎已更新到 v2.1.0',
    time: new Date(Date.now() - 3600000),
    status: 'info'
  },
  {
    id: 4,
    type: 'error',
    title: '任务异常',
    description: '新闻采集任务遇到网络超时问题',
    time: new Date(Date.now() - 7200000),
    status: 'error'
  }
])

// 快速操作
const quickActions = ref([
  {
    name: 'new-task',
    title: '创建任务',
    description: '快速创建新的爬虫任务',
    icon: 'fas fa-plus-circle'
  },
  {
    name: 'generate-content',
    title: '生成内容',
    description: '使用 AI 生成原创内容',
    icon: 'fas fa-magic'
  },
  {
    name: 'view-logs',
    title: '查看日志',
    description: '查看系统运行日志',
    icon: 'fas fa-list-alt'
  },
  {
    name: 'system-status',
    title: '系统状态',
    description: '查看详细系统状态',
    icon: 'fas fa-heartbeat'
  }
])

// Chart 实例
const taskTrendChart = ref(null)
const crawlerStatusChart = ref(null)
const contentStatsChart = ref(null)
const resourceChart = ref(null)

let charts = {}

// 方法
const getTrendIcon = (trend) => {
  return trend === 'up' ? 'fas fa-arrow-up' : 'fas fa-arrow-down'
}

const getResourceColor = (percentage) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getActivityIcon = (type) => {
  const icons = {
    task: 'fas fa-tasks',
    content: 'fas fa-file-alt',
    system: 'fas fa-cog',
    error: 'fas fa-exclamation-triangle'
  }
  return icons[type] || 'fas fa-info-circle'
}

const getStatusText = (status) => {
  const texts = {
    success: '成功',
    error: '失败',
    warning: '警告',
    info: '信息'
  }
  return texts[status] || '未知'
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

const refreshActivities = () => {
  ElMessage.success('活动列表已刷新')
  // 这里可以添加实际的刷新逻辑
}

const handleQuickAction = (action) => {
  switch (action.name) {
    case 'new-task':
      router.push('/tasks')
      break
    case 'generate-content':
      router.push('/content')
      break
    case 'view-logs':
      router.push('/monitoring')
      break
    case 'system-status':
      router.push('/monitoring')
      break
    default:
      ElMessage.info(`执行操作: ${action.title}`)
  }
}

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // 任务执行趋势图
  if (taskTrendChart.value) {
    charts.taskTrend = new Chart(taskTrendChart.value, {
      type: 'line',
      data: {
        labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        datasets: [{
          label: '完成任务',
          data: [12, 19, 15, 25, 22, 18, 24],
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        }, {
          label: '失败任务',
          data: [2, 3, 1, 4, 2, 1, 3],
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
  if (crawlerStatusChart.value) {
    charts.crawlerStatus = new Chart(crawlerStatusChart.value, {
      type: 'doughnut',
      data: {
        labels: ['运行中', '空闲', '错误', '维护'],
        datasets: [{
          data: [15, 8, 2, 3],
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
  
  // 内容生成统计图
  if (contentStatsChart.value) {
    charts.contentStats = new Chart(contentStatsChart.value, {
      type: 'bar',
      data: {
        labels: ['文章', '新闻', '博客', '评论', '摘要'],
        datasets: [{
          label: '生成数量',
          data: [45, 32, 28, 67, 23],
          backgroundColor: [
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#f5576c',
            '#4facfe'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
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
  
  // 系统资源监控图
  if (resourceChart.value) {
    charts.resource = new Chart(resourceChart.value, {
      type: 'line',
      data: {
        labels: Array.from({ length: 20 }, (_, i) => `${i + 1}min`),
        datasets: [{
          label: 'CPU 使用率',
          data: generateRandomData(20, 30, 70),
          borderColor: '#409eff',
          backgroundColor: 'rgba(64, 158, 255, 0.1)',
          tension: 0.4
        }, {
          label: '内存使用率',
          data: generateRandomData(20, 50, 80),
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

// 生成随机数据
const generateRandomData = (count, min, max) => {
  return Array.from({ length: count }, () => 
    Math.floor(Math.random() * (max - min + 1)) + min
  )
}

// 更新系统资源数据
const updateSystemResources = () => {
  systemResources.value = {
    cpu: Math.floor(Math.random() * 30) + 30,
    memory: Math.floor(Math.random() * 40) + 40,
    disk: Math.floor(Math.random() * 20) + 25
  }
}

// 定时器
let resourceTimer = null

// 生命周期
onMounted(() => {
  initCharts()
  
  // 定时更新系统资源数据
  resourceTimer = setInterval(updateSystemResources, 5000)
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
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  &.primary {
    border-left-color: var(--primary-color);
  }
  
  &.success {
    border-left-color: var(--success-color);
  }
  
  &.warning {
    border-left-color: var(--warning-color);
  }
  
  &.info {
    border-left-color: var(--info-color);
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    
    i {
      font-size: 24px;
      color: white;
    }
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    
    .stat-title {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .stat-change {
      font-size: 12px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
      
      &.up {
        color: var(--success-color);
      }
      
      &.down {
        color: var(--danger-color);
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
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
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
        color: var(--text-secondary);
        margin-bottom: 4px;
        display: block;
      }
      
      .value {
        font-size: 12px;
        font-weight: 500;
        color: var(--text-primary);
        margin-left: 8px;
      }
    }
  }
}

// 活动区域
.activity-section {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
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
      color: var(--text-primary);
    }
  }
}

.activity-list {
  .activity-item {
    display: flex;
    align-items: flex-start;
    padding: 16px 0;
    border-bottom: 1px solid var(--border-light);
    
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
      
      &.task {
        background: rgba(64, 158, 255, 0.1);
        color: var(--primary-color);
      }
      
      &.content {
        background: rgba(103, 194, 58, 0.1);
        color: var(--success-color);
      }
      
      &.system {
        background: rgba(230, 162, 60, 0.1);
        color: var(--warning-color);
      }
      
      &.error {
        background: rgba(245, 108, 108, 0.1);
        color: var(--danger-color);
      }
    }
    
    .activity-content {
      flex: 1;
      
      .activity-title {
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .activity-description {
        color: var(--text-regular);
        font-size: 13px;
        line-height: 1.4;
        margin-bottom: 8px;
      }
      
      .activity-time {
        color: var(--text-secondary);
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
        color: var(--success-color);
      }
      
      &.error {
        background: rgba(245, 108, 108, 0.1);
        color: var(--danger-color);
      }
      
      &.warning {
        background: rgba(230, 162, 60, 0.1);
        color: var(--warning-color);
      }
      
      &.info {
        background: rgba(64, 158, 255, 0.1);
        color: var(--info-color);
      }
    }
  }
}

// 快速操作
.quick-actions {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
  
  h3 {
    margin: 0 0 20px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-card {
  padding: 20px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-light);
  }
  
  .action-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    
    i {
      font-size: 20px;
      color: white;
    }
  }
  
  .action-title {
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;
  }
  
  .action-description {
    font-size: 12px;
    color: var(--text-secondary);
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
      
      i {
        font-size: 20px;
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