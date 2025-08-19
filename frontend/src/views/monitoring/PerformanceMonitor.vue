<template>
  <div class="performance-monitor">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">性能监控</h1>
        <p class="page-description">实时监控系统性能指标，分析资源使用情况和性能趋势</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button :type="autoRefresh ? 'primary' : 'default'" @click="toggleAutoRefresh">
            <el-icon><Refresh /></el-icon>
            {{ autoRefresh ? '停止刷新' : '自动刷新' }}
          </el-button>
          <el-button @click="exportReport" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
          <el-button @click="resetMetrics" type="warning" plain>
            <el-icon><RefreshLeft /></el-icon>
            重置指标
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 时间范围选择 -->
    <div class="time-range-section">
      <el-card>
        <div class="time-range-controls">
          <div class="range-buttons">
            <el-button-group>
              <el-button 
                v-for="range in timeRanges" 
                :key="range.value"
                :type="selectedTimeRange === range.value ? 'primary' : 'default'"
                @click="selectTimeRange(range.value)"
                size="small"
              >
                {{ range.label }}
              </el-button>
            </el-button-group>
          </div>
          
          <div class="custom-range">
            <el-date-picker
              v-model="customTimeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="handleCustomRangeChange"
              size="small"
            />
          </div>
          
          <div class="refresh-interval">
            <span class="label">刷新间隔:</span>
            <el-select v-model="refreshInterval" size="small" style="width: 100px;">
              <el-option label="5秒" :value="5" />
              <el-option label="10秒" :value="10" />
              <el-option label="30秒" :value="30" />
              <el-option label="1分钟" :value="60" />
            </el-select>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 关键指标卡片 -->
    <div class="metrics-cards-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="metric-card cpu">
            <div class="metric-header">
              <div class="metric-icon">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">CPU使用率</div>
                <div class="metric-value">{{ metrics.cpu.current }}%</div>
              </div>
            </div>
            <div class="metric-chart">
              <div class="mini-chart" ref="cpuChartRef"></div>
            </div>
            <div class="metric-footer">
              <span class="metric-trend" :class="metrics.cpu.trend">
                <el-icon><ArrowUp v-if="metrics.cpu.trend === 'up'" /><ArrowDown v-else /></el-icon>
                {{ metrics.cpu.change }}%
              </span>
              <span class="metric-label">较上小时</span>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card memory">
            <div class="metric-header">
              <div class="metric-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">内存使用率</div>
                <div class="metric-value">{{ metrics.memory.current }}%</div>
              </div>
            </div>
            <div class="metric-chart">
              <div class="mini-chart" ref="memoryChartRef"></div>
            </div>
            <div class="metric-footer">
              <span class="metric-trend" :class="metrics.memory.trend">
                <el-icon><ArrowUp v-if="metrics.memory.trend === 'up'" /><ArrowDown v-else /></el-icon>
                {{ metrics.memory.change }}%
              </span>
              <span class="metric-label">较上小时</span>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card disk">
            <div class="metric-header">
              <div class="metric-icon">
                <el-icon><FolderOpened /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">磁盘使用率</div>
                <div class="metric-value">{{ metrics.disk.current }}%</div>
              </div>
            </div>
            <div class="metric-chart">
              <div class="mini-chart" ref="diskChartRef"></div>
            </div>
            <div class="metric-footer">
              <span class="metric-trend" :class="metrics.disk.trend">
                <el-icon><ArrowUp v-if="metrics.disk.trend === 'up'" /><ArrowDown v-else /></el-icon>
                {{ metrics.disk.change }}%
              </span>
              <span class="metric-label">较上小时</span>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card network">
            <div class="metric-header">
              <div class="metric-icon">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">网络流量</div>
                <div class="metric-value">{{ metrics.network.current }}MB/s</div>
              </div>
            </div>
            <div class="metric-chart">
              <div class="mini-chart" ref="networkChartRef"></div>
            </div>
            <div class="metric-footer">
              <span class="metric-trend" :class="metrics.network.trend">
                <el-icon><ArrowUp v-if="metrics.network.trend === 'up'" /><ArrowDown v-else /></el-icon>
                {{ metrics.network.change }}MB/s
              </span>
              <span class="metric-label">较上小时</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 详细图表 -->
    <div class="charts-section">
      <el-row :gutter="16">
        <!-- 系统资源使用趋势 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>系统资源使用趋势</span>
                <div class="chart-controls">
                  <el-checkbox-group v-model="resourceChartSeries" size="small">
                    <el-checkbox label="cpu">CPU</el-checkbox>
                    <el-checkbox label="memory">内存</el-checkbox>
                    <el-checkbox label="disk">磁盘</el-checkbox>
                    <el-checkbox label="network">网络</el-checkbox>
                  </el-checkbox-group>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="resourceChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 响应时间分布 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>响应时间分布</span>
                <div class="chart-controls">
                  <el-select v-model="responseTimeMetric" size="small" style="width: 120px;">
                    <el-option label="API请求" value="api" />
                    <el-option label="数据库" value="database" />
                    <el-option label="缓存" value="cache" />
                    <el-option label="文件IO" value="file" />
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
      
      <el-row :gutter="16" style="margin-top: 16px;">
        <!-- 错误率统计 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>错误率统计</span>
                <div class="chart-controls">
                  <el-radio-group v-model="errorChartType" size="small">
                    <el-radio-button label="line">趋势图</el-radio-button>
                    <el-radio-button label="bar">柱状图</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="errorRateChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 吞吐量监控 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>吞吐量监控</span>
                <div class="chart-controls">
                  <el-select v-model="throughputUnit" size="small" style="width: 100px;">
                    <el-option label="请求/秒" value="rps" />
                    <el-option label="任务/分" value="tpm" />
                    <el-option label="事务/秒" value="tps" />
                  </el-select>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div ref="throughputChartRef" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 性能详情表格 -->
    <div class="performance-table-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>性能详情</span>
            <div class="table-controls">
              <el-input
                v-model="tableSearch"
                placeholder="搜索服务或指标"
                size="small"
                style="width: 200px;"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button size="small" @click="refreshTable">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table :data="filteredPerformanceData" stripe>
          <el-table-column prop="service" label="服务" width="150" />
          <el-table-column prop="endpoint" label="端点" min-width="200" />
          <el-table-column prop="avgResponseTime" label="平均响应时间" width="120">
            <template #default="{ row }">
              <span :class="getResponseTimeClass(row.avgResponseTime)">{{ row.avgResponseTime }}ms</span>
            </template>
          </el-table-column>
          <el-table-column prop="p95ResponseTime" label="P95响应时间" width="120">
            <template #default="{ row }">
              <span :class="getResponseTimeClass(row.p95ResponseTime)">{{ row.p95ResponseTime }}ms</span>
            </template>
          </el-table-column>
          <el-table-column prop="throughput" label="吞吐量" width="100">
            <template #default="{ row }">
              {{ row.throughput }}/s
            </template>
          </el-table-column>
          <el-table-column prop="errorRate" label="错误率" width="100">
            <template #default="{ row }">
              <el-tag :type="getErrorRateType(row.errorRate)" size="small">
                {{ row.errorRate }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="cpuUsage" label="CPU使用" width="100">
            <template #default="{ row }">
              <el-progress :percentage="row.cpuUsage" :stroke-width="6" :show-text="false" />
              <span style="margin-left: 8px; font-size: 12px;">{{ row.cpuUsage }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="memoryUsage" label="内存使用" width="100">
            <template #default="{ row }">
              <el-progress :percentage="row.memoryUsage" :stroke-width="6" :show-text="false" />
              <span style="margin-left: 8px; font-size: 12px;">{{ row.memoryUsage }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'healthy' ? 'success' : 'danger'" size="small">
                {{ row.status === 'healthy' ? '健康' : '异常' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text @click="viewServiceDetails(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button size="small" text @click="restartService(row)">
                <el-icon><RefreshLeft /></el-icon>
                重启
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <!-- 服务详情对话框 -->
    <el-dialog v-model="serviceDetailVisible" title="服务性能详情" width="900px">
      <div v-if="selectedService" class="service-detail">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="服务名称">{{ selectedService.service }}</el-descriptions-item>
          <el-descriptions-item label="端点">{{ selectedService.endpoint }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedService.status === 'healthy' ? 'success' : 'danger'">
              {{ selectedService.status === 'healthy' ? '健康' : '异常' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="平均响应时间">{{ selectedService.avgResponseTime }}ms</el-descriptions-item>
          <el-descriptions-item label="P95响应时间">{{ selectedService.p95ResponseTime }}ms</el-descriptions-item>
          <el-descriptions-item label="P99响应时间">{{ selectedService.p99ResponseTime || 'N/A' }}ms</el-descriptions-item>
          <el-descriptions-item label="吞吐量">{{ selectedService.throughput }}/s</el-descriptions-item>
          <el-descriptions-item label="错误率">{{ selectedService.errorRate }}%</el-descriptions-item>
          <el-descriptions-item label="并发连接数">{{ selectedService.connections || 'N/A' }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="service-charts" style="margin-top: 20px;">
          <el-row :gutter="16">
            <el-col :span="12">
              <h4>响应时间趋势</h4>
              <div ref="serviceResponseChartRef" style="height: 200px;"></div>
            </el-col>
            <el-col :span="12">
              <h4>资源使用情况</h4>
              <div ref="serviceResourceChartRef" style="height: 200px;"></div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Download, 
  RefreshLeft,
  Cpu,
  Monitor,
  FolderOpened,
  Connection,
  ArrowUp,
  ArrowDown,
  Search,
  View
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const autoRefresh = ref(false)
const serviceDetailVisible = ref(false)
const selectedService = ref(null)

// 时间范围
const timeRanges = [
  { label: '最近1小时', value: '1h' },
  { label: '最近6小时', value: '6h' },
  { label: '最近24小时', value: '24h' },
  { label: '最近7天', value: '7d' },
  { label: '最近30天', value: '30d' }
]

const selectedTimeRange = ref('1h')
const customTimeRange = ref([])
const refreshInterval = ref(10)

// 图表配置
const resourceChartSeries = ref(['cpu', 'memory', 'disk', 'network'])
const responseTimeMetric = ref('api')
const errorChartType = ref('line')
const throughputUnit = ref('rps')

// 表格搜索
const tableSearch = ref('')

// 关键指标
const metrics = ref({
  cpu: {
    current: 68.5,
    change: 2.3,
    trend: 'up'
  },
  memory: {
    current: 72.1,
    change: -1.8,
    trend: 'down'
  },
  disk: {
    current: 45.2,
    change: 0.5,
    trend: 'up'
  },
  network: {
    current: 12.8,
    change: 3.2,
    trend: 'up'
  }
})

// 性能数据
const performanceData = ref([
  {
    service: 'Web服务器',
    endpoint: '/api/v1/tasks',
    avgResponseTime: 145,
    p95ResponseTime: 280,
    p99ResponseTime: 450,
    throughput: 1250,
    errorRate: 0.8,
    cpuUsage: 65,
    memoryUsage: 70,
    connections: 150,
    status: 'healthy'
  },
  {
    service: 'API网关',
    endpoint: '/api/v1/crawlers',
    avgResponseTime: 89,
    p95ResponseTime: 180,
    p99ResponseTime: 320,
    throughput: 2100,
    errorRate: 0.3,
    cpuUsage: 45,
    memoryUsage: 55,
    connections: 280,
    status: 'healthy'
  },
  {
    service: '数据库',
    endpoint: 'PostgreSQL',
    avgResponseTime: 25,
    p95ResponseTime: 65,
    p99ResponseTime: 120,
    throughput: 3500,
    errorRate: 0.1,
    cpuUsage: 35,
    memoryUsage: 80,
    connections: 45,
    status: 'healthy'
  },
  {
    service: '缓存服务',
    endpoint: 'Redis',
    avgResponseTime: 8,
    p95ResponseTime: 15,
    p99ResponseTime: 25,
    throughput: 8900,
    errorRate: 0.05,
    cpuUsage: 20,
    memoryUsage: 65,
    connections: 120,
    status: 'healthy'
  },
  {
    service: '消息队列',
    endpoint: 'RabbitMQ',
    avgResponseTime: 320,
    p95ResponseTime: 650,
    p99ResponseTime: 1200,
    throughput: 450,
    errorRate: 2.1,
    cpuUsage: 85,
    memoryUsage: 90,
    connections: 25,
    status: 'warning'
  }
])

// 引用
const cpuChartRef = ref()
const memoryChartRef = ref()
const diskChartRef = ref()
const networkChartRef = ref()
const resourceChartRef = ref()
const responseTimeChartRef = ref()
const errorRateChartRef = ref()
const throughputChartRef = ref()
const serviceResponseChartRef = ref()
const serviceResourceChartRef = ref()

// 定时器
let refreshTimer = null

// 计算属性
const filteredPerformanceData = computed(() => {
  if (!tableSearch.value) return performanceData.value
  return performanceData.value.filter(item => 
    item.service.toLowerCase().includes(tableSearch.value.toLowerCase()) ||
    item.endpoint.toLowerCase().includes(tableSearch.value.toLowerCase())
  )
})

// 方法
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    refreshTimer = setInterval(fetchMetrics, refreshInterval.value * 1000)
    ElMessage.success('已开启自动刷新')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已停止自动刷新')
  }
}

const selectTimeRange = (range) => {
  selectedTimeRange.value = range
  customTimeRange.value = []
  fetchMetrics()
}

const handleCustomRangeChange = (range) => {
  if (range && range.length === 2) {
    selectedTimeRange.value = 'custom'
    fetchMetrics()
  }
}

const fetchMetrics = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新指标数据
    updateMetrics()
    
    // 更新图表
    await nextTick()
    updateCharts()
  } catch (error) {
    ElMessage.error('获取性能数据失败')
  } finally {
    loading.value = false
  }
}

const updateMetrics = () => {
  // 模拟指标数据更新
  metrics.value.cpu.current = Math.round((Math.random() * 30 + 50) * 10) / 10
  metrics.value.memory.current = Math.round((Math.random() * 40 + 40) * 10) / 10
  metrics.value.disk.current = Math.round((Math.random() * 20 + 35) * 10) / 10
  metrics.value.network.current = Math.round((Math.random() * 20 + 5) * 10) / 10
}

const updateCharts = () => {
  // 这里应该使用实际的图表库（如ECharts）来更新图表
  // 由于示例中没有引入图表库，这里只是占位
  console.log('更新图表数据')
}

const exportReport = async () => {
  exporting.value = true
  try {
    // 模拟导出
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('性能报告导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const resetMetrics = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有性能指标吗？这将清除历史数据。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('性能指标已重置')
    fetchMetrics()
  } catch {
    // 用户取消
  }
}

const refreshTable = () => {
  fetchMetrics()
}

const getResponseTimeClass = (time) => {
  if (time < 100) return 'response-time-good'
  if (time < 300) return 'response-time-warning'
  return 'response-time-danger'
}

const getErrorRateType = (rate) => {
  if (rate < 1) return 'success'
  if (rate < 5) return 'warning'
  return 'danger'
}

const viewServiceDetails = (service) => {
  selectedService.value = service
  serviceDetailVisible.value = true
  
  // 更新服务详情图表
  nextTick(() => {
    updateServiceCharts()
  })
}

const updateServiceCharts = () => {
  // 更新服务详情图表
  console.log('更新服务详情图表')
}

const restartService = async (service) => {
  try {
    await ElMessageBox.confirm(
      `确定要重启服务 "${service.service}" 吗？`,
      '确认重启',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success(`服务 "${service.service}" 重启成功`)
  } catch {
    // 用户取消
  }
}

// 生命周期
onMounted(() => {
  fetchMetrics()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.performance-monitor {
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

.time-range-section {
  margin-bottom: 24px;
}

.time-range-controls {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.refresh-interval {
  display: flex;
  align-items: center;
  gap: 8px;
}

.refresh-interval .label {
  font-size: 14px;
  color: #6b7280;
}

.metrics-cards-section {
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid;
}

.metric-card.cpu {
  border-left-color: #3b82f6;
}

.metric-card.memory {
  border-left-color: #10b981;
}

.metric-card.disk {
  border-left-color: #f59e0b;
}

.metric-card.network {
  border-left-color: #8b5cf6;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.cpu .metric-icon {
  background: #3b82f6;
}

.memory .metric-icon {
  background: #10b981;
}

.disk .metric-icon {
  background: #f59e0b;
}

.network .metric-icon {
  background: #8b5cf6;
}

.metric-info {
  flex: 1;
}

.metric-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.metric-chart {
  height: 60px;
  margin-bottom: 16px;
}

.mini-chart {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #f3f4f6 25%, transparent 25%), 
              linear-gradient(-45deg, #f3f4f6 25%, transparent 25%), 
              linear-gradient(45deg, transparent 75%, #f3f4f6 75%), 
              linear-gradient(-45deg, transparent 75%, #f3f4f6 75%);
  background-size: 10px 10px;
  background-position: 0 0, 0 5px, 5px -5px, -5px 0px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 12px;
}

.mini-chart::before {
  content: '图表区域';
}

.metric-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.metric-trend.up {
  color: #ef4444;
}

.metric-trend.down {
  color: #10b981;
}

.metric-label {
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

.chart-controls {
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
  content: '图表加载中...';
}

.performance-table-section {
  margin-bottom: 24px;
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.response-time-good {
  color: #10b981;
  font-weight: 500;
}

.response-time-warning {
  color: #f59e0b;
  font-weight: 500;
}

.response-time-danger {
  color: #ef4444;
  font-weight: 500;
}

.service-detail {
  max-height: 600px;
  overflow-y: auto;
}

.service-charts h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 16px;
}
</style>