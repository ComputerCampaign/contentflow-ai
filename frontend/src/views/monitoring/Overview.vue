<template>
  <div class="monitoring-overview">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统监控</h1>
        <p class="page-description">实时监控系统运行状态和性能指标</p>
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
      <div class="status-card">
        <div class="card-icon cpu">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">CPU使用率</div>
          <div class="card-value">{{ systemStats.cpu }}%</div>
          <div class="card-trend" :class="{ up: systemStats.cpuTrend > 0, down: systemStats.cpuTrend < 0 }">
            <el-icon><ArrowUp v-if="systemStats.cpuTrend > 0" /><ArrowDown v-else /></el-icon>
            {{ Math.abs(systemStats.cpuTrend) }}%
          </div>
        </div>
      </div>
      
      <div class="status-card">
        <div class="card-icon memory">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">内存使用率</div>
          <div class="card-value">{{ systemStats.memory }}%</div>
          <div class="card-trend" :class="{ up: systemStats.memoryTrend > 0, down: systemStats.memoryTrend < 0 }">
            <el-icon><ArrowUp v-if="systemStats.memoryTrend > 0" /><ArrowDown v-else /></el-icon>
            {{ Math.abs(systemStats.memoryTrend) }}%
          </div>
        </div>
      </div>
      
      <div class="status-card">
        <div class="card-icon disk">
          <el-icon><FolderOpened /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">磁盘使用率</div>
          <div class="card-value">{{ systemStats.disk }}%</div>
          <div class="card-trend" :class="{ up: systemStats.diskTrend > 0, down: systemStats.diskTrend < 0 }">
            <el-icon><ArrowUp v-if="systemStats.diskTrend > 0" /><ArrowDown v-else /></el-icon>
            {{ Math.abs(systemStats.diskTrend) }}%
          </div>
        </div>
      </div>
      
      <div class="status-card">
        <div class="card-icon network">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">网络流量</div>
          <div class="card-value">{{ systemStats.network }} MB/s</div>
          <div class="card-trend" :class="{ up: systemStats.networkTrend > 0, down: systemStats.networkTrend < 0 }">
            <el-icon><ArrowUp v-if="systemStats.networkTrend > 0" /><ArrowDown v-else /></el-icon>
            {{ Math.abs(systemStats.networkTrend) }} MB/s
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="24">
        <el-col :span="12">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">系统资源使用趋势</h3>
              <el-select v-model="resourceTimeRange" size="small" style="width: 120px;">
                <el-option label="1小时" value="1h" />
                <el-option label="6小时" value="6h" />
                <el-option label="24小时" value="24h" />
                <el-option label="7天" value="7d" />
              </el-select>
            </div>
            <div class="chart-content">
              <div ref="resourceChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">任务执行统计</h3>
              <el-select v-model="taskTimeRange" size="small" style="width: 120px;">
                <el-option label="今天" value="today" />
                <el-option label="本周" value="week" />
                <el-option label="本月" value="month" />
              </el-select>
            </div>
            <div class="chart-content">
              <div ref="taskChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="24" style="margin-top: 24px;">
        <el-col :span="24">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">实时任务监控</h3>
              <div class="chart-actions">
                <el-tag v-if="realTimeData.activeConnections > 0" type="success" size="small">
                  {{ realTimeData.activeConnections }} 个活跃连接
                </el-tag>
                <el-tag v-else type="info" size="small">无活跃连接</el-tag>
              </div>
            </div>
            <div class="chart-content">
              <div ref="realTimeChartRef" class="chart" style="height: 400px;"></div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 服务状态 -->
    <div class="services-section">
      <div class="section-header">
        <h2 class="section-title">服务状态</h2>
      </div>
      
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
              <span class="metric-label">响应时间</span>
              <span class="metric-value">{{ service.responseTime }}ms</span>
            </div>
            <div class="metric">
              <span class="metric-label">错误率</span>
              <span class="metric-value">{{ service.errorRate }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">QPS</span>
              <span class="metric-value">{{ service.qps }}</span>
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
    </div>
    
    <!-- 告警信息 -->
    <div class="alerts-section">
      <div class="section-header">
        <h2 class="section-title">系统告警</h2>
        <el-button size="small" @click="clearAllAlerts" :disabled="alerts.length === 0">
          清除所有告警
        </el-button>
      </div>
      
      <div v-if="alerts.length === 0" class="no-alerts">
        <el-empty description="暂无告警信息" />
      </div>
      
      <div v-else class="alerts-list">
        <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.level">
          <div class="alert-icon">
            <el-icon>
              <Warning v-if="alert.level === 'warning'" />
              <CircleClose v-else-if="alert.level === 'error'" />
              <InfoFilled v-else />
            </el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
          </div>
          <div class="alert-actions">
            <el-button size="small" @click="dismissAlert(alert.id)">
              忽略
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Monitor,
  Cpu,
  FolderOpened,
  Connection,
  ArrowUp,
  ArrowDown,
  Warning,
  CircleClose,
  InfoFilled
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface SystemStats {
  cpu: number
  cpuTrend: number
  memory: number
  memoryTrend: number
  disk: number
  diskTrend: number
  network: number
  networkTrend: number
}

interface Service {
  name: string
  description: string
  status: 'running' | 'stopped' | 'error'
  responseTime: number
  errorRate: number
  qps: number
}

interface Alert {
  id: string
  level: 'info' | 'warning' | 'error'
  title: string
  message: string
  timestamp: number
}

interface RealTimeData {
  activeConnections: number
  requestsPerSecond: number
  averageResponseTime: number
}

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(false)
const resourceTimeRange = ref('1h')
const taskTimeRange = ref('today')

const systemStats = ref<SystemStats>({
  cpu: 45,
  cpuTrend: 2.3,
  memory: 68,
  memoryTrend: -1.2,
  disk: 32,
  diskTrend: 0.5,
  network: 12.5,
  networkTrend: 3.8
})

const services = ref<Service[]>([
  {
    name: 'Web服务器',
    description: 'Nginx Web服务器',
    status: 'running',
    responseTime: 45,
    errorRate: 0.1,
    qps: 120
  },
  {
    name: '数据库',
    description: 'PostgreSQL数据库',
    status: 'running',
    responseTime: 12,
    errorRate: 0.0,
    qps: 85
  },
  {
    name: 'Redis缓存',
    description: 'Redis缓存服务',
    status: 'running',
    responseTime: 2,
    errorRate: 0.0,
    qps: 200
  },
  {
    name: '任务队列',
    description: 'Celery任务队列',
    status: 'running',
    responseTime: 150,
    errorRate: 2.1,
    qps: 15
  }
])

const alerts = ref<Alert[]>([
  {
    id: '1',
    level: 'warning',
    title: 'CPU使用率过高',
    message: 'CPU使用率已达到85%，建议检查系统负载',
    timestamp: Date.now() - 300000
  },
  {
    id: '2',
    level: 'error',
    title: '磁盘空间不足',
    message: '系统磁盘剩余空间不足10%，请及时清理',
    timestamp: Date.now() - 600000
  }
])

const realTimeData = ref<RealTimeData>({
  activeConnections: 25,
  requestsPerSecond: 45,
  averageResponseTime: 120
})

// 图表引用
const resourceChartRef = ref<HTMLElement>()
const taskChartRef = ref<HTMLElement>()
const realTimeChartRef = ref<HTMLElement>()

// 图表实例
let resourceChart: echarts.ECharts | null = null
let taskChart: echarts.ECharts | null = null
let realTimeChart: echarts.ECharts | null = null

// 定时器
let refreshTimer: number | null = null

// 方法
const getServiceStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'success'
    case 'stopped':
      return 'info'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

const getServiceStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中'
    case 'stopped':
      return '已停止'
    case 'error':
      return '错误'
    default:
      return '未知'
  }
}

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString()
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      refreshData()
    }, 5000)
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
    
    // 更新系统统计数据
    systemStats.value = {
      cpu: Math.floor(Math.random() * 100),
      cpuTrend: (Math.random() - 0.5) * 10,
      memory: Math.floor(Math.random() * 100),
      memoryTrend: (Math.random() - 0.5) * 10,
      disk: Math.floor(Math.random() * 100),
      diskTrend: (Math.random() - 0.5) * 5,
      network: Math.floor(Math.random() * 50),
      networkTrend: (Math.random() - 0.5) * 20
    }
    
    // 更新实时数据
    realTimeData.value = {
      activeConnections: Math.floor(Math.random() * 50),
      requestsPerSecond: Math.floor(Math.random() * 100),
      averageResponseTime: Math.floor(Math.random() * 200) + 50
    }
    
    // 更新图表
    updateCharts()
    
    if (!autoRefresh.value) {
      ElMessage.success('数据刷新成功')
    }
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  nextTick(() => {
    // 初始化资源使用趋势图表
    if (resourceChartRef.value) {
      resourceChart = echarts.init(resourceChartRef.value)
      const option = {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['CPU', '内存', '磁盘']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: Array.from({ length: 24 }, (_, i) => `${i}:00`)
        },
        yAxis: {
          type: 'value',
          max: 100
        },
        series: [
          {
            name: 'CPU',
            type: 'line',
            data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
          },
          {
            name: '内存',
            type: 'line',
            data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
          },
          {
            name: '磁盘',
            type: 'line',
            data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
          }
        ]
      }
      resourceChart.setOption(option)
    }
    
    // 初始化任务执行统计图表
    if (taskChartRef.value) {
      taskChart = echarts.init(taskChartRef.value)
      const option = {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '任务状态',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 1048, name: '成功' },
              { value: 735, name: '运行中' },
              { value: 580, name: '等待中' },
              { value: 484, name: '失败' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      taskChart.setOption(option)
    }
    
    // 初始化实时监控图表
    if (realTimeChartRef.value) {
      realTimeChart = echarts.init(realTimeChartRef.value)
      const option = {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['请求数/秒', '响应时间(ms)', '活跃连接数']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: Array.from({ length: 60 }, (_, i) => `${i}s`)
        },
        yAxis: [
          {
            type: 'value',
            name: '请求数/连接数'
          },
          {
            type: 'value',
            name: '响应时间(ms)'
          }
        ],
        series: [
          {
            name: '请求数/秒',
            type: 'line',
            data: Array.from({ length: 60 }, () => Math.floor(Math.random() * 100))
          },
          {
            name: '活跃连接数',
            type: 'line',
            data: Array.from({ length: 60 }, () => Math.floor(Math.random() * 50))
          },
          {
            name: '响应时间(ms)',
            type: 'line',
            yAxisIndex: 1,
            data: Array.from({ length: 60 }, () => Math.floor(Math.random() * 200) + 50)
          }
        ]
      }
      realTimeChart.setOption(option)
    }
  })
}

const updateCharts = () => {
  // 更新图表数据
  if (resourceChart) {
    resourceChart.setOption({
      series: [
        {
          data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
        },
        {
          data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
        },
        {
          data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
        }
      ]
    })
  }
  
  if (realTimeChart) {
    realTimeChart.setOption({
      series: [
        {
          data: Array.from({ length: 60 }, () => Math.floor(Math.random() * 100))
        },
        {
          data: Array.from({ length: 60 }, () => Math.floor(Math.random() * 50))
        },
        {
          data: Array.from({ length: 60 }, () => Math.floor(Math.random() * 200) + 50)
        }
      ]
    })
  }
}

const viewServiceDetails = (service: Service) => {
  ElMessage.info(`查看 ${service.name} 详情`)
}

const toggleService = async (service: Service) => {
  try {
    const action = service.status === 'running' ? '停止' : '启动'
    await ElMessageBox.confirm(
      `确定要${action}服务 "${service.name}" 吗？`,
      `确认${action}`,
      {
        type: 'warning'
      }
    )
    
    service.status = service.status === 'running' ? 'stopped' : 'running'
    ElMessage.success(`${service.name} ${action}成功`)
  } catch (error) {
    // 用户取消操作
  }
}

const dismissAlert = (alertId: string) => {
  const index = alerts.value.findIndex(alert => alert.id === alertId)
  if (index > -1) {
    alerts.value.splice(index, 1)
    ElMessage.success('告警已忽略')
  }
}

const clearAllAlerts = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有告警信息吗？',
      '确认清除',
      {
        type: 'warning'
      }
    )
    
    alerts.value = []
    ElMessage.success('所有告警已清除')
  } catch (error) {
    // 用户取消操作
  }
}

// 生命周期
onMounted(() => {
  initCharts()
  refreshData()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 销毁图表实例
  if (resourceChart) {
    resourceChart.dispose()
  }
  if (taskChart) {
    taskChart.dispose()
  }
  if (realTimeChart) {
    realTimeChart.dispose()
  }
})
</script>

<style lang="scss" scoped>
.monitoring-overview {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    
    .header-left {
      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 8px 0;
      }
      
      .page-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 0;
      }
    }
  }
  
  .status-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
    
    .status-card {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 12px;
      padding: 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.3s ease;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .card-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        
        &.cpu {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        &.memory {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        &.disk {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        &.network {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }
      
      .card-content {
        flex: 1;
        
        .card-title {
          font-size: 14px;
          color: var(--el-text-color-secondary);
          margin-bottom: 8px;
        }
        
        .card-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          margin-bottom: 4px;
        }
        
        .card-trend {
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 4px;
          
          &.up {
            color: var(--el-color-danger);
          }
          
          &.down {
            color: var(--el-color-success);
          }
        }
      }
    }
  }
  
  .charts-section {
    margin-bottom: 32px;
    
    .chart-card {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 12px;
      overflow: hidden;
      
      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        background: var(--el-fill-color-lighter);
        
        .chart-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          margin: 0;
        }
        
        .chart-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }
      }
      
      .chart-content {
        padding: 20px;
        
        .chart {
          width: 100%;
        }
      }
    }
  }
  
  .services-section {
    margin-bottom: 32px;
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .section-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0;
      }
    }
    
    .services-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      
      .service-card {
        background: var(--el-bg-color);
        border: 1px solid var(--el-border-color-light);
        border-radius: 12px;
        padding: 20px;
        
        .service-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 16px;
          
          .service-info {
            .service-name {
              font-size: 16px;
              font-weight: 600;
              color: var(--el-text-color-primary);
              margin-bottom: 4px;
            }
            
            .service-description {
              font-size: 12px;
              color: var(--el-text-color-secondary);
            }
          }
        }
        
        .service-metrics {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 16px;
          
          .metric {
            text-align: center;
            
            .metric-label {
              display: block;
              font-size: 12px;
              color: var(--el-text-color-secondary);
              margin-bottom: 4px;
            }
            
            .metric-value {
              font-size: 14px;
              font-weight: 600;
              color: var(--el-text-color-primary);
            }
          }
        }
        
        .service-actions {
          display: flex;
          gap: 8px;
        }
      }
    }
  }
  
  .alerts-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .section-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0;
      }
    }
    
    .no-alerts {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 12px;
      padding: 40px;
    }
    
    .alerts-list {
      .alert-item {
        background: var(--el-bg-color);
        border: 1px solid var(--el-border-color-light);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        
        &.warning {
          border-left: 4px solid var(--el-color-warning);
        }
        
        &.error {
          border-left: 4px solid var(--el-color-danger);
        }
        
        &.info {
          border-left: 4px solid var(--el-color-info);
        }
        
        .alert-icon {
          font-size: 20px;
          margin-top: 2px;
          
          .warning & {
            color: var(--el-color-warning);
          }
          
          .error & {
            color: var(--el-color-danger);
          }
          
          .info & {
            color: var(--el-color-info);
          }
        }
        
        .alert-content {
          flex: 1;
          
          .alert-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }
          
          .alert-message {
            font-size: 13px;
            color: var(--el-text-color-regular);
            margin-bottom: 8px;
          }
          
          .alert-time {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
        
        .alert-actions {
          margin-top: 2px;
        }
      }
    }
  }
}
</style>