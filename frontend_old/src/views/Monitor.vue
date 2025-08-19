<template>
  <div class="monitor-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>系统监控</h1>
        <p>实时监控系统运行状态和性能指标</p>
      </div>
      <div class="header-right">
        <el-button @click="refreshData">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': refreshing }"></i>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 系统状态卡片 -->
    <div class="status-grid">
      <div class="status-card">
        <div class="status-header">
          <h3>系统状态</h3>
          <el-tag :type="systemStatus.type" size="large">
            {{ systemStatus.text }}
          </el-tag>
        </div>
        <div class="status-info">
          <p>运行时间: {{ systemStatus.uptime }}</p>
          <p>最后更新: {{ formatTime(systemStatus.lastUpdate) }}</p>
        </div>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <h3>活跃任务</h3>
          <span class="status-number">{{ activeTasks }}</span>
        </div>
        <div class="status-info">
          <p>运行中: {{ runningTasks }}</p>
          <p>等待中: {{ pendingTasks }}</p>
        </div>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <h3>错误统计</h3>
          <span class="status-number error">{{ errorCount }}</span>
        </div>
        <div class="status-info">
          <p>今日错误: {{ todayErrors }}</p>
          <p>错误率: {{ errorRate }}%</p>
        </div>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <h3>数据库连接</h3>
          <el-tag :type="dbStatus.type" size="large">
            {{ dbStatus.text }}
          </el-tag>
        </div>
        <div class="status-info">
          <p>连接数: {{ dbStatus.connections }}</p>
          <p>响应时间: {{ dbStatus.responseTime }}ms</p>
        </div>
      </div>
    </div>

    <!-- 性能监控图表 -->
    <div class="charts-grid">
      <!-- CPU使用率 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>CPU 使用率</h3>
          <span class="current-value">{{ cpuUsage }}%</span>
        </div>
        <div class="chart-container">
          <canvas ref="cpuChartRef"></canvas>
        </div>
      </div>
      
      <!-- 内存使用率 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>内存使用率</h3>
          <span class="current-value">{{ memoryUsage }}%</span>
        </div>
        <div class="chart-container">
          <canvas ref="memoryChartRef"></canvas>
        </div>
      </div>
      
      <!-- 网络流量 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>网络流量</h3>
          <span class="current-value">{{ networkSpeed }} MB/s</span>
        </div>
        <div class="chart-container">
          <canvas ref="networkChartRef"></canvas>
        </div>
      </div>
      
      <!-- 磁盘使用率 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>磁盘使用率</h3>
          <span class="current-value">{{ diskUsage }}%</span>
        </div>
        <div class="chart-container">
          <canvas ref="diskChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- 日志监控 -->
    <div class="logs-section">
      <div class="section-header">
        <h2>系统日志</h2>
        <div class="log-filters">
          <el-select v-model="logLevel" placeholder="日志级别" style="width: 120px">
            <el-option label="全部" value=""></el-option>
            <el-option label="错误" value="error"></el-option>
            <el-option label="警告" value="warning"></el-option>
            <el-option label="信息" value="info"></el-option>
          </el-select>
          <el-button @click="clearLogs" type="danger" plain>
            <i class="fas fa-trash"></i>
            清空日志
          </el-button>
        </div>
      </div>
      
      <div class="logs-container">
        <div
          v-for="log in filteredLogs"
          :key="log.id"
          class="log-item"
          :class="log.level"
        >
          <div class="log-time">{{ formatTime(log.timestamp) }}</div>
          <div class="log-level">
            <el-tag :type="getLogLevelType(log.level)" size="small">
              {{ log.level.toUpperCase() }}
            </el-tag>
          </div>
          <div class="log-message">{{ log.message }}</div>
          <div class="log-source">{{ log.source }}</div>
        </div>
      </div>
    </div>

    <!-- 服务状态 -->
    <div class="services-section">
      <h2>服务状态</h2>
      <div class="services-grid">
        <div
          v-for="service in services"
          :key="service.name"
          class="service-card"
        >
          <div class="service-header">
            <h4>{{ service.name }}</h4>
            <el-tag :type="service.status === 'running' ? 'success' : 'danger'">
              {{ service.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </div>
          <div class="service-info">
            <p>端口: {{ service.port }}</p>
            <p>CPU: {{ service.cpu }}%</p>
            <p>内存: {{ service.memory }}MB</p>
            <p>运行时间: {{ service.uptime }}</p>
          </div>
          <div class="service-actions">
            <el-button
              size="small"
              :type="service.status === 'running' ? 'warning' : 'success'"
              @click="toggleService(service)"
            >
              {{ service.status === 'running' ? '停止' : '启动' }}
            </el-button>
            <el-button size="small" @click="restartService(service)">
              重启
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import Chart from 'chart.js/auto'

const refreshing = ref(false)
const logLevel = ref('')

// 图表引用
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const networkChartRef = ref(null)
const diskChartRef = ref(null)

// 图表实例
let cpuChart = null
let memoryChart = null
let networkChart = null
let diskChart = null

// 定时器
let updateTimer = null

// 系统状态
const systemStatus = ref({
  type: 'success',
  text: '正常运行',
  uptime: '15天 8小时 32分钟',
  lastUpdate: new Date()
})

const dbStatus = ref({
  type: 'success',
  text: '连接正常',
  connections: 25,
  responseTime: 12
})

// 任务统计
const activeTasks = ref(12)
const runningTasks = ref(8)
const pendingTasks = ref(4)
const errorCount = ref(3)
const todayErrors = ref(15)
const errorRate = ref(2.1)

// 性能指标
const cpuUsage = ref(45)
const memoryUsage = ref(68)
const networkSpeed = ref(12.5)
const diskUsage = ref(72)

// 日志数据
const logs = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 60000),
    level: 'info',
    message: '爬虫任务 "技术博客采集" 执行完成',
    source: 'CrawlerService'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 120000),
    level: 'warning',
    message: 'CPU使用率超过80%，建议检查系统负载',
    source: 'SystemMonitor'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 180000),
    level: 'error',
    message: '数据库连接超时，正在重试...',
    source: 'DatabaseService'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 240000),
    level: 'info',
    message: '内容生成任务启动',
    source: 'ContentService'
  }
])

// 服务状态
const services = ref([
  {
    name: '爬虫服务',
    status: 'running',
    port: 8001,
    cpu: 15.2,
    memory: 256,
    uptime: '2天 5小时'
  },
  {
    name: '内容生成服务',
    status: 'running',
    port: 8002,
    cpu: 8.7,
    memory: 512,
    uptime: '1天 12小时'
  },
  {
    name: '文件服务',
    status: 'running',
    port: 8003,
    cpu: 3.1,
    memory: 128,
    uptime: '3天 2小时'
  },
  {
    name: '数据库服务',
    status: 'running',
    port: 5432,
    cpu: 12.5,
    memory: 1024,
    uptime: '15天 8小时'
  }
])

const filteredLogs = computed(() => {
  if (!logLevel.value) return logs.value
  return logs.value.filter(log => log.level === logLevel.value)
})

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm:ss')
}

const getLogLevelType = (level) => {
  const typeMap = {
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return typeMap[level] || 'info'
}

const refreshData = async () => {
  refreshing.value = true
  try {
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新性能指标
    cpuUsage.value = Math.floor(Math.random() * 30) + 30
    memoryUsage.value = Math.floor(Math.random() * 20) + 60
    networkSpeed.value = (Math.random() * 10 + 5).toFixed(1)
    diskUsage.value = Math.floor(Math.random() * 10) + 70
    
    systemStatus.value.lastUpdate = new Date()
    
    ElMessage.success('数据刷新成功')
  } finally {
    refreshing.value = false
  }
}

const clearLogs = () => {
  logs.value = []
  ElMessage.success('日志已清空')
}

const toggleService = (service) => {
  service.status = service.status === 'running' ? 'stopped' : 'running'
  ElMessage.success(`服务 "${service.name}" 已${service.status === 'running' ? '启动' : '停止'}`)
}

const restartService = (service) => {
  ElMessage.success(`服务 "${service.name}" 正在重启...`)
}

// 初始化图表
const initCharts = () => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        display: false
      },
      y: {
        display: false,
        min: 0,
        max: 100
      }
    },
    elements: {
      point: {
        radius: 0
      }
    }
  }

  const generateData = () => {
    const data = []
    for (let i = 0; i < 20; i++) {
      data.push(Math.random() * 100)
    }
    return data
  }

  // CPU图表
  cpuChart = new Chart(cpuChartRef.value, {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [{
        data: generateData(),
        borderColor: '#409EFF',
        backgroundColor: 'rgba(64, 158, 255, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: chartOptions
  })

  // 内存图表
  memoryChart = new Chart(memoryChartRef.value, {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [{
        data: generateData(),
        borderColor: '#67C23A',
        backgroundColor: 'rgba(103, 194, 58, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: chartOptions
  })

  // 网络图表
  networkChart = new Chart(networkChartRef.value, {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [{
        data: generateData(),
        borderColor: '#E6A23C',
        backgroundColor: 'rgba(230, 162, 60, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: chartOptions
  })

  // 磁盘图表
  diskChart = new Chart(diskChartRef.value, {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [{
        data: generateData(),
        borderColor: '#F56C6C',
        backgroundColor: 'rgba(245, 108, 108, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: chartOptions
  })
}

// 更新图表数据
const updateCharts = () => {
  const charts = [cpuChart, memoryChart, networkChart, diskChart]
  
  charts.forEach(chart => {
    if (chart) {
      // 移除第一个数据点，添加新的数据点
      chart.data.datasets[0].data.shift()
      chart.data.datasets[0].data.push(Math.random() * 100)
      chart.update('none')
    }
  })
}

onMounted(() => {
  initCharts()
  
  // 启动定时更新
  updateTimer = setInterval(() => {
    updateCharts()
  }, 2000)
})

onUnmounted(() => {
  // 清理定时器和图表
  if (updateTimer) {
    clearInterval(updateTimer)
  }
  
  const charts = [cpuChart, memoryChart, networkChart, diskChart]
  charts.forEach(chart => {
    if (chart) {
      chart.destroy()
    }
  })
})
</script>

<style lang="scss" scoped>
.monitor-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
    }
  }
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.status-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-light);
  
  .status-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .status-number {
      font-size: 24px;
      font-weight: 600;
      color: var(--primary-color);
      
      &.error {
        color: var(--danger-color);
      }
    }
  }
  
  .status-info {
    p {
      margin: 4px 0;
      font-size: 14px;
      color: var(--text-secondary);
    }
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.chart-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-light);
  
  .chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .current-value {
      font-size: 18px;
      font-weight: 600;
      color: var(--primary-color);
    }
  }
  
  .chart-container {
    height: 120px;
    position: relative;
  }
}

.logs-section, .services-section {
  margin-bottom: 32px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .log-filters {
      display: flex;
      gap: 12px;
    }
  }
}

.logs-container {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
  box-shadow: var(--shadow-light);
}

.log-item {
  display: grid;
  grid-template-columns: 120px 80px 1fr 120px;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
  
  &:last-child {
    border-bottom: none;
  }
  
  .log-time {
    color: var(--text-secondary);
  }
  
  .log-message {
    color: var(--text-primary);
  }
  
  .log-source {
    color: var(--text-secondary);
    text-align: right;
  }
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.service-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-light);
  
  .service-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    
    h4 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
  
  .service-info {
    margin-bottom: 16px;
    
    p {
      margin: 4px 0;
      font-size: 14px;
      color: var(--text-secondary);
    }
  }
  
  .service-actions {
    display: flex;
    gap: 8px;
  }
}
</style>