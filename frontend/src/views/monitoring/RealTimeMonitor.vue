<template>
  <div class="real-time-monitor">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">实时监控</h1>
        <p class="page-description">实时监控系统状态、任务执行和资源使用情况</p>
      </div>
      <div class="header-right">
        <div class="status-indicator">
          <div class="status-dot" :class="systemStatus"></div>
          <span class="status-text">{{ getStatusText(systemStatus) }}</span>
        </div>
        <el-button-group>
          <el-button :type="isMonitoring ? 'danger' : 'primary'" @click="toggleMonitoring">
            <el-icon><VideoPlay v-if="!isMonitoring" /><VideoPause v-else /></el-icon>
            {{ isMonitoring ? '停止监控' : '开始监控' }}
          </el-button>
          <el-button @click="exportSnapshot" :loading="exporting">
            <el-icon><Camera /></el-icon>
            快照
          </el-button>
          <el-button @click="openSettings">
            <el-icon><Setting /></el-icon>
            设置
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 实时状态卡片 -->
    <div class="status-cards-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="status-card active-tasks">
            <div class="card-header">
              <div class="card-icon">
                <el-icon><Operation /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">活跃任务</div>
                <div class="card-value">{{ realTimeData.activeTasks }}</div>
              </div>
            </div>
            <div class="card-trend">
              <span class="trend-value" :class="realTimeData.tasksTrend">
                <el-icon><TrendCharts /></el-icon>
                {{ realTimeData.tasksChange }}
              </span>
              <span class="trend-label">较上分钟</span>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="status-card online-users">
            <div class="card-header">
              <div class="card-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">在线用户</div>
                <div class="card-value">{{ realTimeData.onlineUsers }}</div>
              </div>
            </div>
            <div class="card-trend">
              <span class="trend-value" :class="realTimeData.usersTrend">
                <el-icon><TrendCharts /></el-icon>
                {{ realTimeData.usersChange }}
              </span>
              <span class="trend-label">较上分钟</span>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="status-card system-load">
            <div class="card-header">
              <div class="card-icon">
                <el-icon><Odometer /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">系统负载</div>
                <div class="card-value">{{ realTimeData.systemLoad }}</div>
              </div>
            </div>
            <div class="card-trend">
              <span class="trend-value" :class="realTimeData.loadTrend">
                <el-icon><TrendCharts /></el-icon>
                {{ realTimeData.loadChange }}
              </span>
              <span class="trend-label">较上分钟</span>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="status-card error-count">
            <div class="card-header">
              <div class="card-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">错误计数</div>
                <div class="card-value">{{ realTimeData.errorCount }}</div>
              </div>
            </div>
            <div class="card-trend">
              <span class="trend-value" :class="realTimeData.errorsTrend">
                <el-icon><TrendCharts /></el-icon>
                {{ realTimeData.errorsChange }}
              </span>
              <span class="trend-label">较上分钟</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 实时图表 -->
    <div class="charts-section">
      <el-row :gutter="16">
        <!-- 实时资源监控 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>实时资源监控</span>
                <div class="chart-controls">
                  <el-switch
                    v-model="autoScale"
                    active-text="自动缩放"
                    inactive-text="固定范围"
                    size="small"
                  />
                  <el-select v-model="resourceMetric" size="small" style="width: 100px; margin-left: 12px;">
                    <el-option label="CPU" value="cpu" />
                    <el-option label="内存" value="memory" />
                    <el-option label="磁盘" value="disk" />
                    <el-option label="网络" value="network" />
                  </el-select>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="realTimeResourceChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 任务执行监控 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>任务执行监控</span>
                <div class="chart-controls">
                  <el-radio-group v-model="taskViewMode" size="small">
                    <el-radio-button label="timeline">时间线</el-radio-button>
                    <el-radio-button label="status">状态分布</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="taskExecutionChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="16" style="margin-top: 16px;">
        <!-- 网络流量监控 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>网络流量监控</span>
                <div class="chart-controls">
                  <el-checkbox-group v-model="networkSeries" size="small">
                    <el-checkbox label="inbound">入站</el-checkbox>
                    <el-checkbox label="outbound">出站</el-checkbox>
                  </el-checkbox-group>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="networkTrafficChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 响应时间监控 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>响应时间监控</span>
                <div class="chart-controls">
                  <el-select v-model="responseTimeService" size="small" style="width: 120px;">
                    <el-option label="全部服务" value="all" />
                    <el-option label="API服务" value="api" />
                    <el-option label="数据库" value="database" />
                    <el-option label="缓存" value="cache" />
                  </el-select>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="responseTimeChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 实时活动日志 -->
    <div class="activity-log-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>实时活动日志</span>
            <div class="log-controls">
              <el-switch
                v-model="autoScroll"
                active-text="自动滚动"
                inactive-text="停止滚动"
                size="small"
              />
              <el-select v-model="logLevel" size="small" style="width: 100px; margin-left: 12px;">
                <el-option label="全部" value="all" />
                <el-option label="INFO" value="info" />
                <el-option label="WARN" value="warn" />
                <el-option label="ERROR" value="error" />
              </el-select>
              <el-button size="small" @click="clearActivityLog" style="margin-left: 12px;">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="activity-log" ref="activityLogRef">
          <div v-if="filteredActivityLog.length === 0" class="empty-log">
            <el-empty description="暂无活动日志" />
          </div>
          
          <div v-else class="log-list">
            <div
              v-for="log in filteredActivityLog"
              :key="log.id"
              class="log-item"
              :class="log.level"
            >
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
              <div class="log-level">
                <el-tag :type="getLogLevelType(log.level)" size="small">
                  {{ log.level }}
                </el-tag>
              </div>
              <div class="log-service">{{ log.service }}</div>
              <div class="log-message">{{ log.message }}</div>
              <div class="log-actions">
                <el-button size="small" text @click="viewLogDetail(log)">
                  <el-icon><View /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 系统警报 -->
    <div class="alerts-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>系统警报</span>
            <div class="alert-controls">
              <el-badge :value="unreadAlerts" :hidden="unreadAlerts === 0">
                <el-button size="small" @click="markAllAlertsRead">
                  <el-icon><Bell /></el-icon>
                  全部已读
                </el-button>
              </el-badge>
              <el-button size="small" @click="configureAlerts" style="margin-left: 12px;">
                <el-icon><Setting /></el-icon>
                配置
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="alerts-list">
          <div v-if="alerts.length === 0" class="empty-alerts">
            <el-empty description="暂无系统警报" />
          </div>
          
          <div v-else>
            <div
              v-for="alert in alerts"
              :key="alert.id"
              class="alert-item"
              :class="{ 'unread': !alert.read, [alert.severity]: true }"
            >
              <div class="alert-icon">
                <el-icon>
                  <Warning v-if="alert.severity === 'warning'" />
                  <CircleCloseFilled v-else-if="alert.severity === 'critical'" />
                  <InfoFilled v-else />
                </el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-meta">
                  <span class="alert-time">{{ formatTime(alert.timestamp) }}</span>
                  <span class="alert-source">{{ alert.source }}</span>
                </div>
              </div>
              <div class="alert-actions">
                <el-button size="small" text @click="acknowledgeAlert(alert)">
                  <el-icon><Check /></el-icon>
                  确认
                </el-button>
                <el-button size="small" text @click="dismissAlert(alert)">
                  <el-icon><Close /></el-icon>
                  忽略
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 监控设置对话框 -->
    <el-dialog v-model="settingsVisible" title="监控设置" width="600px">
      <el-form :model="monitorSettings" label-width="120px">
        <el-form-item label="刷新间隔">
          <el-select v-model="monitorSettings.refreshInterval" style="width: 200px;">
            <el-option label="1秒" :value="1" />
            <el-option label="2秒" :value="2" />
            <el-option label="5秒" :value="5" />
            <el-option label="10秒" :value="10" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="数据保留时间">
          <el-select v-model="monitorSettings.dataRetention" style="width: 200px;">
            <el-option label="5分钟" :value="5" />
            <el-option label="10分钟" :value="10" />
            <el-option label="30分钟" :value="30" />
            <el-option label="1小时" :value="60" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="警报阈值">
          <div class="threshold-settings">
            <div class="threshold-item">
              <span>CPU使用率:</span>
              <el-input-number v-model="monitorSettings.thresholds.cpu" :min="0" :max="100" size="small" />
              <span>%</span>
            </div>
            <div class="threshold-item">
              <span>内存使用率:</span>
              <el-input-number v-model="monitorSettings.thresholds.memory" :min="0" :max="100" size="small" />
              <span>%</span>
            </div>
            <div class="threshold-item">
              <span>响应时间:</span>
              <el-input-number v-model="monitorSettings.thresholds.responseTime" :min="0" size="small" />
              <span>ms</span>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="通知设置">
          <el-checkbox-group v-model="monitorSettings.notifications">
            <el-checkbox label="email">邮件通知</el-checkbox>
            <el-checkbox label="sms">短信通知</el-checkbox>
            <el-checkbox label="webhook">Webhook</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="settingsVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  VideoPlay,
  VideoPause,
  Camera,
  Setting,
  Operation,
  User,
  Odometer,
  Warning,
  TrendCharts,
  Delete,
  View,
  Bell,
  Check,
  Close,
  CircleCloseFilled,
  InfoFilled
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

// 响应式数据
const isMonitoring = ref(false)
const exporting = ref(false)
const settingsVisible = ref(false)
const systemStatus = ref('healthy') // healthy, warning, critical

// 图表配置
const autoScale = ref(true)
const resourceMetric = ref('cpu')
const taskViewMode = ref('timeline')
const networkSeries = ref(['inbound', 'outbound'])
const responseTimeService = ref('all')

// 日志配置
const autoScroll = ref(true)
const logLevel = ref('all')

// 实时数据
const realTimeData = ref({
  activeTasks: 24,
  tasksChange: '+3',
  tasksTrend: 'up',
  onlineUsers: 156,
  usersChange: '+12',
  usersTrend: 'up',
  systemLoad: 2.34,
  loadChange: '+0.15',
  loadTrend: 'up',
  errorCount: 3,
  errorsChange: '-2',
  errorsTrend: 'down'
})

// 活动日志
const activityLog = ref([
  {
    id: 1,
    timestamp: new Date(),
    level: 'INFO',
    service: 'API',
    message: '用户 admin 登录成功'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 30000),
    level: 'WARN',
    service: 'Database',
    message: '数据库连接池使用率达到 80%'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 60000),
    level: 'INFO',
    service: 'Crawler',
    message: '爬虫任务 task_001 执行完成'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 90000),
    level: 'ERROR',
    service: 'Queue',
    message: '消息队列处理失败，任务 ID: 12345'
  }
])

// 系统警报
const alerts = ref([
  {
    id: 1,
    title: 'CPU使用率过高',
    message: 'CPU使用率已达到 85%，建议检查系统负载',
    severity: 'warning',
    source: '系统监控',
    timestamp: new Date(Date.now() - 300000),
    read: false
  },
  {
    id: 2,
    title: '磁盘空间不足',
    message: '磁盘 /var/log 使用率已达到 90%',
    severity: 'critical',
    source: '存储监控',
    timestamp: new Date(Date.now() - 600000),
    read: false
  }
])

// 监控设置
const monitorSettings = ref({
  refreshInterval: 2,
  dataRetention: 10,
  thresholds: {
    cpu: 80,
    memory: 85,
    responseTime: 1000
  },
  notifications: ['email']
})

// 引用
const activityLogRef = ref()
const realTimeResourceChartRef = ref()
const taskExecutionChartRef = ref()
const networkTrafficChartRef = ref()
const responseTimeChartRef = ref()

// 定时器
let monitorTimer = null
let logUpdateTimer = null

// 计算属性
const filteredActivityLog = computed(() => {
  if (logLevel.value === 'all') return activityLog.value
  return activityLog.value.filter(log => log.level.toLowerCase() === logLevel.value)
})

const unreadAlerts = computed(() => {
  return alerts.value.filter(alert => !alert.read).length
})

// 方法
const getStatusText = (status) => {
  const statusMap = {
    healthy: '系统正常',
    warning: '系统警告',
    critical: '系统异常'
  }
  return statusMap[status] || '未知状态'
}

const toggleMonitoring = () => {
  isMonitoring.value = !isMonitoring.value
  
  if (isMonitoring.value) {
    startMonitoring()
    ElMessage.success('实时监控已启动')
  } else {
    stopMonitoring()
    ElMessage.info('实时监控已停止')
  }
}

const startMonitoring = () => {
  // 启动实时数据更新
  monitorTimer = setInterval(updateRealTimeData, monitorSettings.value.refreshInterval * 1000)
  
  // 启动日志更新
  logUpdateTimer = setInterval(updateActivityLog, 5000)
  
  // 更新图表
  updateCharts()
}

const stopMonitoring = () => {
  if (monitorTimer) {
    clearInterval(monitorTimer)
    monitorTimer = null
  }
  
  if (logUpdateTimer) {
    clearInterval(logUpdateTimer)
    logUpdateTimer = null
  }
}

const updateRealTimeData = () => {
  // 模拟实时数据更新
  realTimeData.value.activeTasks = Math.floor(Math.random() * 50) + 10
  realTimeData.value.onlineUsers = Math.floor(Math.random() * 200) + 100
  realTimeData.value.systemLoad = Math.round((Math.random() * 3 + 1) * 100) / 100
  realTimeData.value.errorCount = Math.floor(Math.random() * 10)
  
  // 更新系统状态
  if (realTimeData.value.systemLoad > 3 || realTimeData.value.errorCount > 5) {
    systemStatus.value = 'critical'
  } else if (realTimeData.value.systemLoad > 2 || realTimeData.value.errorCount > 2) {
    systemStatus.value = 'warning'
  } else {
    systemStatus.value = 'healthy'
  }
  
  // 更新图表
  updateCharts()
}

const updateActivityLog = () => {
  // 模拟新日志添加
  const newLog = {
    id: Date.now(),
    timestamp: new Date(),
    level: ['INFO', 'WARN', 'ERROR'][Math.floor(Math.random() * 3)],
    service: ['API', 'Database', 'Crawler', 'Queue'][Math.floor(Math.random() * 4)],
    message: '模拟实时日志消息 ' + Math.random().toString(36).substr(2, 9)
  }
  
  activityLog.value.unshift(newLog)
  
  // 限制日志数量
  if (activityLog.value.length > 100) {
    activityLog.value = activityLog.value.slice(0, 100)
  }
  
  // 自动滚动
  if (autoScroll.value) {
    nextTick(() => {
      if (activityLogRef.value) {
        activityLogRef.value.scrollTop = 0
      }
    })
  }
}

const updateCharts = () => {
  // 这里应该使用实际的图表库来更新图表
  console.log('更新实时图表数据')
}

const exportSnapshot = async () => {
  exporting.value = true
  try {
    // 模拟导出快照
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('监控快照导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const openSettings = () => {
  settingsVisible.value = true
}

const saveSettings = () => {
  // 保存设置
  ElMessage.success('设置已保存')
  settingsVisible.value = false
  
  // 如果正在监控，重新启动以应用新设置
  if (isMonitoring.value) {
    stopMonitoring()
    startMonitoring()
  }
}

const clearActivityLog = () => {
  activityLog.value = []
  ElMessage.success('活动日志已清空')
}

const formatTime = (timestamp) => {
  return dayjs(timestamp).format('HH:mm:ss')
}

const getLogLevelType = (level) => {
  const types = {
    INFO: 'success',
    WARN: 'warning',
    ERROR: 'danger'
  }
  return types[level] || 'info'
}

const viewLogDetail = (log) => {
  ElMessage.info(`查看日志详情: ${log.message}`)
}

const markAllAlertsRead = () => {
  alerts.value.forEach(alert => {
    alert.read = true
  })
  ElMessage.success('所有警报已标记为已读')
}

const acknowledgeAlert = (alert) => {
  alert.read = true
  ElMessage.success('警报已确认')
}

const dismissAlert = (alert) => {
  const index = alerts.value.findIndex(a => a.id === alert.id)
  if (index > -1) {
    alerts.value.splice(index, 1)
    ElMessage.success('警报已忽略')
  }
}

const configureAlerts = () => {
  ElMessage.info('打开警报配置页面')
}

// 生命周期
onMounted(() => {
  // 初始化图表
  updateCharts()
})

onUnmounted(() => {
  stopMonitoring()
})
</script>

<style scoped>
.real-time-monitor {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.healthy {
  background: #10b981;
}

.status-dot.warning {
  background: #f59e0b;
}

.status-dot.critical {
  background: #ef4444;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 currentColor;
  }
  70% {
    box-shadow: 0 0 0 10px transparent;
  }
  100% {
    box-shadow: 0 0 0 0 transparent;
  }
}

.status-text {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.status-cards-section {
  margin-bottom: 24px;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid;
}

.status-card.active-tasks {
  border-left-color: #3b82f6;
}

.status-card.online-users {
  border-left-color: #10b981;
}

.status-card.system-load {
  border-left-color: #f59e0b;
}

.status-card.error-count {
  border-left-color: #ef4444;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.active-tasks .card-icon {
  background: #3b82f6;
}

.online-users .card-icon {
  background: #10b981;
}

.system-load .card-icon {
  background: #f59e0b;
}

.error-count .card-icon {
  background: #ef4444;
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.card-trend {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.trend-value {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.trend-value.up {
  color: #ef4444;
}

.trend-value.down {
  color: #10b981;
}

.trend-label {
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

.chart-controls,
.log-controls,
.alert-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-container {
  background: #f9fafb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 14px;
}

.chart-container::before {
  content: '实时图表加载中...';
}

.activity-log-section,
.alerts-section {
  margin-bottom: 24px;
}

.activity-log {
  max-height: 400px;
  overflow-y: auto;
}

.empty-log,
.empty-alerts {
  padding: 40px;
  text-align: center;
}

.log-list {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  background: white;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.INFO {
  border-left: 4px solid #10b981;
}

.log-item.WARN {
  border-left: 4px solid #f59e0b;
}

.log-item.ERROR {
  border-left: 4px solid #ef4444;
}

.log-time {
  font-size: 12px;
  color: #9ca3af;
  font-family: monospace;
  min-width: 80px;
}

.log-level {
  min-width: 60px;
}

.log-service {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  min-width: 80px;
  text-align: center;
}

.log-message {
  flex: 1;
  font-size: 14px;
  color: #1f2937;
}

.log-actions {
  min-width: 40px;
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
  background: white;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item.unread {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
}

.alert-item.warning {
  border-left: 4px solid #f59e0b;
}

.alert-item.critical {
  border-left: 4px solid #ef4444;
}

.alert-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 16px;
  margin-top: 4px;
}

.alert-item.warning .alert-icon {
  background: #fef3c7;
  color: #f59e0b;
}

.alert-item.critical .alert-icon {
  background: #fee2e2;
  color: #ef4444;
}

.alert-item.info .alert-icon {
  background: #dbeafe;
  color: #3b82f6;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.alert-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9ca3af;
}

.alert-actions {
  display: flex;
  gap: 8px;
}

.threshold-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.threshold-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.threshold-item span:first-child {
  min-width: 100px;
  font-size: 14px;
  color: #374151;
}

.threshold-item span:last-child {
  font-size: 14px;
  color: #6b7280;
}
</style>