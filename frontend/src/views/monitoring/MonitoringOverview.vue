<template>
  <div class="monitoring-overview">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统监控概览</h1>
        <p class="page-description">实时监控系统运行状态和关键性能指标</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button :type="autoRefresh ? 'primary' : 'default'" @click="toggleAutoRefresh">
            <el-icon><Refresh /></el-icon>
            {{ autoRefresh ? '停止刷新' : '自动刷新' }}
          </el-button>
          <el-button @click="refreshData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            手动刷新
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 系统状态卡片 -->
    <div class="status-cards">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="status-card">
            <div class="card-icon system">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-title">系统状态</div>
              <div class="card-value">
                <el-tag :type="systemStatus.type" size="large">
                  {{ systemStatus.text }}
                </el-tag>
              </div>
              <div class="card-info">运行时间: {{ systemStatus.uptime }}</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="status-card">
            <div class="card-icon tasks">
              <el-icon><Operation /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-title">活跃任务</div>
              <div class="card-value">{{ activeTasks }}</div>
              <div class="card-info">运行中: {{ runningTasks }} | 等待中: {{ pendingTasks }}</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="status-card">
            <div class="card-icon errors">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-title">错误统计</div>
              <div class="card-value error">{{ errorCount }}</div>
              <div class="card-info">今日错误: {{ todayErrors }} | 错误率: {{ errorRate }}%</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="status-card">
            <div class="card-icon database">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-title">数据库连接</div>
              <div class="card-value">
                <el-tag :type="dbStatus.type" size="large">
                  {{ dbStatus.text }}
                </el-tag>
              </div>
              <div class="card-info">连接数: {{ dbStatus.connections }} | 响应: {{ dbStatus.responseTime }}ms</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 性能指标图表 -->
    <div class="charts-section">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>系统资源使用率</span>
                <el-select v-model="resourceTimeRange" size="small" style="width: 120px;">
                  <el-option label="1小时" value="1h" />
                  <el-option label="6小时" value="6h" />
                  <el-option label="24小时" value="24h" />
                </el-select>
              </div>
            </template>
            <div class="chart-container" ref="resourceChartRef" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>任务执行统计</span>
                <el-select v-model="taskTimeRange" size="small" style="width: 120px;">
                  <el-option label="今天" value="today" />
                  <el-option label="本周" value="week" />
                  <el-option label="本月" value="month" />
                </el-select>
              </div>
            </template>
            <div class="chart-container" ref="taskChartRef" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 服务状态 -->
    <div class="services-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>服务状态</span>
            <el-button size="small" @click="refreshServices">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <div class="services-grid">
          <div v-for="service in services" :key="service.name" class="service-card">
            <div class="service-header">
              <div class="service-info">
                <div class="service-name">{{ service.name }}</div>
                <div class="service-description">{{ service.description }}</div>
              </div>
              <div class="service-status">
                <el-tag :type="getServiceStatusType(service.status)" size="small">
                  {{ getServiceStatusText(service.status) }}
                </el-tag>
              </div>
            </div>
            
            <div class="service-metrics">
              <div class="metric">
                <span class="metric-label">CPU</span>
                <span class="metric-value">{{ service.cpu }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">内存</span>
                <span class="metric-value">{{ service.memory }}MB</span>
              </div>
              <div class="metric">
                <span class="metric-label">响应时间</span>
                <span class="metric-value">{{ service.responseTime }}ms</span>
              </div>
            </div>
            
            <div class="service-actions">
              <el-button size="small" @click="viewServiceDetails(service)">
                查看详情
              </el-button>
              <el-button 
                size="small" 
                :type="service.status === 'running' ? 'danger' : 'success'"
                @click="toggleService(service)"
              >
                {{ service.status === 'running' ? '停止' : '启动' }}
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 最近告警 -->
    <div class="alerts-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>最近告警</span>
            <el-button size="small" @click="viewAllAlerts">
              查看全部
            </el-button>
          </div>
        </template>
        
        <div v-if="recentAlerts.length === 0" class="no-alerts">
          <el-empty description="暂无告警信息" />
        </div>
        
        <div v-else class="alerts-list">
          <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.level">
            <div class="alert-icon">
              <el-icon><Warning v-if="alert.level === 'warning'" /><CircleCloseFilled v-else /></el-icon>
            </div>
            <div class="alert-content">
              <div class="alert-title">{{ alert.title }}</div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
            </div>
            <div class="alert-actions">
              <el-button size="small" text @click="dismissAlert(alert)">
                忽略
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Monitor, 
  Operation, 
  Warning, 
  Connection, 
  Refresh, 
  CircleCloseFilled 
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(false)
const resourceTimeRange = ref('1h')
const taskTimeRange = ref('today')

// 图表引用
const resourceChartRef = ref()
const taskChartRef = ref()

// 系统状态
const systemStatus = ref({
  type: 'success',
  text: '正常运行',
  uptime: '15天 8小时 32分钟'
})

// 任务统计
const activeTasks = ref(24)
const runningTasks = ref(8)
const pendingTasks = ref(16)

// 错误统计
const errorCount = ref(3)
const todayErrors = ref(1)
const errorRate = ref(0.2)

// 数据库状态
const dbStatus = ref({
  type: 'success',
  text: '连接正常',
  connections: 15,
  responseTime: 45
})

// 服务列表
const services = ref([
  {
    name: 'Web服务器',
    description: 'Nginx Web服务器',
    status: 'running',
    cpu: 12.5,
    memory: 256,
    responseTime: 45
  },
  {
    name: 'API服务',
    description: 'Node.js API服务',
    status: 'running',
    cpu: 8.3,
    memory: 512,
    responseTime: 32
  },
  {
    name: '数据库',
    description: 'PostgreSQL数据库',
    status: 'running',
    cpu: 15.2,
    memory: 1024,
    responseTime: 28
  },
  {
    name: '任务队列',
    description: 'Redis任务队列',
    status: 'running',
    cpu: 3.1,
    memory: 128,
    responseTime: 12
  }
])

// 最近告警
const recentAlerts = ref([
  {
    id: 1,
    level: 'warning',
    title: 'CPU使用率过高',
    message: 'Web服务器CPU使用率达到85%，建议检查负载情况',
    timestamp: new Date(Date.now() - 30 * 60 * 1000)
  },
  {
    id: 2,
    level: 'error',
    title: '任务执行失败',
    message: '爬虫任务 "新闻采集" 执行失败，错误代码: 500',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
  }
])

// 自动刷新定时器
let refreshTimer = null

// 方法
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    refreshTimer = setInterval(refreshData, 30000) // 30秒刷新一次
    ElMessage.success('已开启自动刷新')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已停止自动刷新')
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新数据
    updateSystemStats()
    
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const updateSystemStats = () => {
  // 模拟数据更新
  activeTasks.value = Math.floor(Math.random() * 50) + 10
  runningTasks.value = Math.floor(activeTasks.value * 0.3)
  pendingTasks.value = activeTasks.value - runningTasks.value
  errorCount.value = Math.floor(Math.random() * 10)
}

const refreshServices = async () => {
  try {
    // 模拟刷新服务状态
    services.value.forEach(service => {
      service.cpu = Math.random() * 20
      service.memory = Math.floor(Math.random() * 500) + 100
      service.responseTime = Math.floor(Math.random() * 100) + 10
    })
    ElMessage.success('服务状态刷新成功')
  } catch (error) {
    ElMessage.error('服务状态刷新失败')
  }
}

const getServiceStatusType = (status) => {
  return status === 'running' ? 'success' : 'danger'
}

const getServiceStatusText = (status) => {
  return status === 'running' ? '运行中' : '已停止'
}

const viewServiceDetails = (service) => {
  ElMessage.info(`查看 ${service.name} 详情`)
}

const toggleService = (service) => {
  const action = service.status === 'running' ? '停止' : '启动'
  ElMessage.info(`${action} ${service.name}`)
}

const viewAllAlerts = () => {
  ElMessage.info('跳转到告警页面')
}

const dismissAlert = (alert) => {
  const index = recentAlerts.value.findIndex(a => a.id === alert.id)
  if (index > -1) {
    recentAlerts.value.splice(index, 1)
    ElMessage.success('告警已忽略')
  }
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 生命周期
onMounted(() => {
  refreshData()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.monitoring-overview {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1f2937;
}

.page-description {
  color: #6b7280;
  margin: 0;
}

.status-cards {
  margin-bottom: 24px;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.card-icon.system {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-icon.tasks {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon.errors {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.card-icon.database {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.card-value.error {
  color: #ef4444;
}

.card-info {
  font-size: 12px;
  color: #9ca3af;
}

.charts-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
}

.services-section {
  margin-bottom: 24px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.service-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #f9fafb;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.service-name {
  font-weight: 600;
  color: #1f2937;
}

.service-description {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.service-metrics {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-label {
  font-size: 12px;
  color: #6b7280;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.service-actions {
  display: flex;
  gap: 8px;
}

.alerts-section .no-alerts {
  text-align: center;
  padding: 40px;
}

.alerts-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item.warning .alert-icon {
  color: #f59e0b;
}

.alert-item.error .alert-icon {
  color: #ef4444;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.alert-message {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 4px;
}

.alert-time {
  color: #9ca3af;
  font-size: 12px;
}

.alert-actions {
  display: flex;
  align-items: center;
}
</style>