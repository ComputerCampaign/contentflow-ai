<template>
  <div class="performance-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">性能监控</h1>
        <p class="page-description">实时监控系统性能指标和资源使用情况</p>
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
          <el-button @click="resetMetrics" type="danger" plain>
            <el-icon><Delete /></el-icon>
            重置指标
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 时间范围选择 -->
    <div class="time-range-section">
      <el-card>
        <div class="time-range-controls">
          <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
            <el-radio-button label="1h">最近1小时</el-radio-button>
            <el-radio-button label="6h">最近6小时</el-radio-button>
            <el-radio-button label="24h">最近24小时</el-radio-button>
            <el-radio-button label="7d">最近7天</el-radio-button>
            <el-radio-button label="30d">最近30天</el-radio-button>
          </el-radio-group>
          
          <div class="custom-range">
            <el-date-picker
              v-model="customTimeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="handleCustomRangeChange"
            />
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 关键指标卡片 -->
    <div class="metrics-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon cpu">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">CPU使用率</div>
                <div class="metric-value">{{ metrics.cpu.current }}%</div>
              </div>
            </div>
            <div class="metric-trend">
              <div class="trend-chart" ref="cpuTrendRef"></div>
              <div class="trend-info">
                <span class="trend-label">平均: {{ metrics.cpu.average }}%</span>
                <span class="trend-change" :class="{ positive: metrics.cpu.change > 0, negative: metrics.cpu.change < 0 }">
                  {{ metrics.cpu.change > 0 ? '+' : '' }}{{ metrics.cpu.change }}%
                </span>
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon memory">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">内存使用率</div>
                <div class="metric-value">{{ metrics.memory.current }}%</div>
              </div>
            </div>
            <div class="metric-trend">
              <div class="trend-chart" ref="memoryTrendRef"></div>
              <div class="trend-info">
                <span class="trend-label">平均: {{ metrics.memory.average }}%</span>
                <span class="trend-change" :class="{ positive: metrics.memory.change > 0, negative: metrics.memory.change < 0 }">
                  {{ metrics.memory.change > 0 ? '+' : '' }}{{ metrics.memory.change }}%
                </span>
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon disk">
                <el-icon><FolderOpened /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">磁盘使用率</div>
                <div class="metric-value">{{ metrics.disk.current }}%</div>
              </div>
            </div>
            <div class="metric-trend">
              <div class="trend-chart" ref="diskTrendRef"></div>
              <div class="trend-info">
                <span class="trend-label">平均: {{ metrics.disk.average }}%</span>
                <span class="trend-change" :class="{ positive: metrics.disk.change > 0, negative: metrics.disk.change < 0 }">
                  {{ metrics.disk.change > 0 ? '+' : '' }}{{ metrics.disk.change }}%
                </span>
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon network">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-title">网络吞吐量</div>
                <div class="metric-value">{{ metrics.network.current }} MB/s</div>
              </div>
            </div>
            <div class="metric-trend">
              <div class="trend-chart" ref="networkTrendRef"></div>
              <div class="trend-info">
                <span class="trend-label">平均: {{ metrics.network.average }} MB/s</span>
                <span class="trend-change" :class="{ positive: metrics.network.change > 0, negative: metrics.network.change < 0 }">
                  {{ metrics.network.change > 0 ? '+' : '' }}{{ metrics.network.change }} MB/s
                </span>
              </div>
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
            <div class="chart-container" ref="resourceChartRef"></div>
          </el-card>
        </el-col>
        
        <!-- 响应时间分布 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>响应时间分布</span>
                <div class="chart-controls">
                  <el-select v-model="responseTimeService" size="small" style="width: 120px;">
                    <el-option label="全部服务" value="all" />
                    <el-option label="Web服务" value="web" />
                    <el-option label="API服务" value="api" />
                    <el-option label="数据库" value="database" />
                  </el-select>
                </div>
              </div>
            </template>
            <div class="chart-container" ref="responseTimeChartRef"></div>
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
                  <el-radio-group v-model="errorRateType" size="small">
                    <el-radio-button label="count">错误数量</el-radio-button>
                    <el-radio-button label="rate">错误率</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container" ref="errorRateChartRef"></div>
          </el-card>
        </el-col>
        
        <!-- 吞吐量统计 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>吞吐量统计</span>
                <div class="chart-controls">
                  <el-radio-group v-model="throughputMetric" size="small">
                    <el-radio-button label="requests">请求数</el-radio-button>
                    <el-radio-button label="tasks">任务数</el-radio-button>
                    <el-radio-button label="data">数据量</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container" ref="throughputChartRef"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 性能详情表格 -->
    <div class="details-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>性能详情</span>
            <div class="header-actions">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索服务或指标"
                clearable
                size="small"
                style="width: 200px;"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <el-table :data="filteredPerformanceData" stripe>
          <el-table-column prop="service" label="服务" width="120">
            <template #default="{ row }">
              <el-tag :type="getServiceType(row.service)" size="small">
                {{ row.service }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="endpoint" label="端点" min-width="200" />
          
          <el-table-column prop="avgResponseTime" label="平均响应时间" width="120" align="right">
            <template #default="{ row }">
              <span :class="getResponseTimeClass(row.avgResponseTime)">
                {{ row.avgResponseTime }}ms
              </span>
            </template>
          </el-table-column>
          
          <el-table-column prop="p95ResponseTime" label="P95响应时间" width="120" align="right">
            <template #default="{ row }">
              <span :class="getResponseTimeClass(row.p95ResponseTime)">
                {{ row.p95ResponseTime }}ms
              </span>
            </template>
          </el-table-column>
          
          <el-table-column prop="requestCount" label="请求数" width="100" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.requestCount) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="errorRate" label="错误率" width="100" align="right">
            <template #default="{ row }">
              <span :class="getErrorRateClass(row.errorRate)">
                {{ row.errorRate }}%
              </span>
            </template>
          </el-table-column>
          
          <el-table-column prop="throughput" label="吞吐量" width="120" align="right">
            <template #default="{ row }">
              {{ row.throughput }} req/s
            </template>
          </el-table-column>
          
          <el-table-column prop="cpuUsage" label="CPU使用" width="100" align="right">
            <template #default="{ row }">
              <el-progress
                :percentage="row.cpuUsage"
                :color="getProgressColor(row.cpuUsage)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="usage-text">{{ row.cpuUsage }}%</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="memoryUsage" label="内存使用" width="100" align="right">
            <template #default="{ row }">
              <el-progress
                :percentage="row.memoryUsage"
                :color="getProgressColor(row.memoryUsage)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="usage-text">{{ row.memoryUsage }}%</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text @click="viewServiceDetails(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button size="small" text @click="analyzeService(row)">
                <el-icon><DataAnalysis /></el-icon>
                分析
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 服务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`${selectedService?.service} 服务详情`"
      width="80%"
      :before-close="handleDetailClose"
    >
      <div v-if="selectedService" class="service-detail">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="服务名称">
                {{ selectedService.service }}
              </el-descriptions-item>
              <el-descriptions-item label="端点">
                {{ selectedService.endpoint }}
              </el-descriptions-item>
              <el-descriptions-item label="平均响应时间">
                {{ selectedService.avgResponseTime }}ms
              </el-descriptions-item>
              <el-descriptions-item label="P95响应时间">
                {{ selectedService.p95ResponseTime }}ms
              </el-descriptions-item>
              <el-descriptions-item label="请求总数">
                {{ formatNumber(selectedService.requestCount) }}
              </el-descriptions-item>
              <el-descriptions-item label="错误率">
                {{ selectedService.errorRate }}%
              </el-descriptions-item>
              <el-descriptions-item label="吞吐量">
                {{ selectedService.throughput }} req/s
              </el-descriptions-item>
              <el-descriptions-item label="CPU使用率">
                {{ selectedService.cpuUsage }}%
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="性能趋势" name="trend">
            <div class="trend-charts">
              <div class="chart-container" ref="serviceTrendChartRef"></div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="错误分析" name="errors">
            <div class="error-analysis">
              <div class="chart-container" ref="serviceErrorChartRef"></div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportServiceReport">导出报告</el-button>
          <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Download,
  Delete,
  Search,
  Monitor,
  Cpu,
  FolderOpened,
  Connection,
  View,
  DataAnalysis
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface MetricData {
  current: number
  average: number
  change: number
}

interface SystemMetrics {
  cpu: MetricData
  memory: MetricData
  disk: MetricData
  network: MetricData
}

interface PerformanceData {
  id: string
  service: string
  endpoint: string
  avgResponseTime: number
  p95ResponseTime: number
  requestCount: number
  errorRate: number
  throughput: number
  cpuUsage: number
  memoryUsage: number
}

interface Pagination {
  page: number
  size: number
  total: number
}

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const autoRefresh = ref(false)
const timeRange = ref('1h')
const customTimeRange = ref<[string, string] | null>(null)
const searchKeyword = ref('')
const detailDialogVisible = ref(false)
const activeTab = ref('basic')

// 图表控制
const resourceChartSeries = ref(['cpu', 'memory', 'disk', 'network'])
const responseTimeService = ref('all')
const errorRateType = ref('rate')
const throughputMetric = ref('requests')

// 数据
const metrics = ref<SystemMetrics>({
  cpu: { current: 45, average: 42, change: 3 },
  memory: { current: 68, average: 65, change: 3 },
  disk: { current: 23, average: 25, change: -2 },
  network: { current: 12.5, average: 10.8, change: 1.7 }
})

const performanceData = ref<PerformanceData[]>([])
const selectedService = ref<PerformanceData | null>(null)

const pagination = ref<Pagination>({
  page: 1,
  size: 20,
  total: 0
})

// 图表实例
const cpuTrendRef = ref<HTMLElement>()
const memoryTrendRef = ref<HTMLElement>()
const diskTrendRef = ref<HTMLElement>()
const networkTrendRef = ref<HTMLElement>()
const resourceChartRef = ref<HTMLElement>()
const responseTimeChartRef = ref<HTMLElement>()
const errorRateChartRef = ref<HTMLElement>()
const throughputChartRef = ref<HTMLElement>()
const serviceTrendChartRef = ref<HTMLElement>()
const serviceErrorChartRef = ref<HTMLElement>()

let cpuTrendChart: echarts.ECharts | null = null
let memoryTrendChart: echarts.ECharts | null = null
let diskTrendChart: echarts.ECharts | null = null
let networkTrendChart: echarts.ECharts | null = null
let resourceChart: echarts.ECharts | null = null
let responseTimeChart: echarts.ECharts | null = null
let errorRateChart: echarts.ECharts | null = null
let throughputChart: echarts.ECharts | null = null
let serviceTrendChart: echarts.ECharts | null = null
let serviceErrorChart: echarts.ECharts | null = null

// 定时器
let refreshTimer: number | null = null

// 计算属性
const filteredPerformanceData = computed(() => {
  if (!searchKeyword.value) {
    return performanceData.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return performanceData.value.filter(item => 
    item.service.toLowerCase().includes(keyword) ||
    item.endpoint.toLowerCase().includes(keyword)
  )
})

// 方法
const generateMockPerformanceData = (): PerformanceData[] => {
  const services = ['web', 'api', 'database', 'queue', 'crawler']
  const endpoints = [
    '/api/users',
    '/api/tasks',
    '/api/crawlers',
    '/api/auth/login',
    '/api/dashboard',
    '/health',
    '/metrics',
    '/api/logs'
  ]
  
  const data: PerformanceData[] = []
  
  for (let i = 0; i < 50; i++) {
    const service = services[Math.floor(Math.random() * services.length)]
    const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)]
    
    data.push({
      id: `perf_${i}`,
      service,
      endpoint,
      avgResponseTime: Math.floor(Math.random() * 500) + 50,
      p95ResponseTime: Math.floor(Math.random() * 1000) + 200,
      requestCount: Math.floor(Math.random() * 10000) + 1000,
      errorRate: Math.random() * 5,
      throughput: Math.floor(Math.random() * 100) + 10,
      cpuUsage: Math.floor(Math.random() * 80) + 10,
      memoryUsage: Math.floor(Math.random() * 70) + 20
    })
  }
  
  return data
}

const getServiceType = (service: string) => {
  switch (service) {
    case 'web':
      return 'primary'
    case 'api':
      return 'success'
    case 'database':
      return 'warning'
    case 'queue':
      return 'info'
    case 'crawler':
      return 'danger'
    default:
      return 'default'
  }
}

const getResponseTimeClass = (time: number) => {
  if (time < 100) return 'response-time-good'
  if (time < 300) return 'response-time-normal'
  return 'response-time-slow'
}

const getErrorRateClass = (rate: number) => {
  if (rate < 1) return 'error-rate-good'
  if (rate < 3) return 'error-rate-normal'
  return 'error-rate-high'
}

const getProgressColor = (value: number) => {
  if (value < 50) return '#67c23a'
  if (value < 80) return '#e6a23c'
  return '#f56c6c'
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const initTrendCharts = () => {
  nextTick(() => {
    // CPU趋势图
    if (cpuTrendRef.value) {
      cpuTrendChart = echarts.init(cpuTrendRef.value)
      cpuTrendChart.setOption({
        grid: { top: 5, right: 5, bottom: 5, left: 5 },
        xAxis: { type: 'category', show: false, data: Array.from({ length: 20 }, (_, i) => i) },
        yAxis: { type: 'value', show: false, min: 0, max: 100 },
        series: [{
          type: 'line',
          data: Array.from({ length: 20 }, () => Math.floor(Math.random() * 40) + 30),
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#409eff', width: 2 },
          areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
        }]
      })
    }
    
    // 内存趋势图
    if (memoryTrendRef.value) {
      memoryTrendChart = echarts.init(memoryTrendRef.value)
      memoryTrendChart.setOption({
        grid: { top: 5, right: 5, bottom: 5, left: 5 },
        xAxis: { type: 'category', show: false, data: Array.from({ length: 20 }, (_, i) => i) },
        yAxis: { type: 'value', show: false, min: 0, max: 100 },
        series: [{
          type: 'line',
          data: Array.from({ length: 20 }, () => Math.floor(Math.random() * 30) + 50),
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#67c23a', width: 2 },
          areaStyle: { color: 'rgba(103, 194, 58, 0.1)' }
        }]
      })
    }
    
    // 磁盘趋势图
    if (diskTrendRef.value) {
      diskTrendChart = echarts.init(diskTrendRef.value)
      diskTrendChart.setOption({
        grid: { top: 5, right: 5, bottom: 5, left: 5 },
        xAxis: { type: 'category', show: false, data: Array.from({ length: 20 }, (_, i) => i) },
        yAxis: { type: 'value', show: false, min: 0, max: 100 },
        series: [{
          type: 'line',
          data: Array.from({ length: 20 }, () => Math.floor(Math.random() * 20) + 15),
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#e6a23c', width: 2 },
          areaStyle: { color: 'rgba(230, 162, 60, 0.1)' }
        }]
      })
    }
    
    // 网络趋势图
    if (networkTrendRef.value) {
      networkTrendChart = echarts.init(networkTrendRef.value)
      networkTrendChart.setOption({
        grid: { top: 5, right: 5, bottom: 5, left: 5 },
        xAxis: { type: 'category', show: false, data: Array.from({ length: 20 }, (_, i) => i) },
        yAxis: { type: 'value', show: false, min: 0, max: 50 },
        series: [{
          type: 'line',
          data: Array.from({ length: 20 }, () => Math.floor(Math.random() * 20) + 5),
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#f56c6c', width: 2 },
          areaStyle: { color: 'rgba(245, 108, 108, 0.1)' }
        }]
      })
    }
  })
}

const initMainCharts = () => {
  nextTick(() => {
    // 系统资源使用趋势图
    if (resourceChartRef.value) {
      resourceChart = echarts.init(resourceChartRef.value)
      updateResourceChart()
    }
    
    // 响应时间分布图
    if (responseTimeChartRef.value) {
      responseTimeChart = echarts.init(responseTimeChartRef.value)
      updateResponseTimeChart()
    }
    
    // 错误率统计图
    if (errorRateChartRef.value) {
      errorRateChart = echarts.init(errorRateChartRef.value)
      updateErrorRateChart()
    }
    
    // 吞吐量统计图
    if (throughputChartRef.value) {
      throughputChart = echarts.init(throughputChartRef.value)
      updateThroughputChart()
    }
  })
}

const updateResourceChart = () => {
  if (!resourceChart) return
  
  const timeData = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date().getHours() - 23 + i
    return `${hour < 0 ? hour + 24 : hour}:00`
  })
  
  const series = []
  
  if (resourceChartSeries.value.includes('cpu')) {
    series.push({
      name: 'CPU',
      type: 'line',
      data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 40) + 30),
      smooth: true,
      lineStyle: { color: '#409eff' }
    })
  }
  
  if (resourceChartSeries.value.includes('memory')) {
    series.push({
      name: '内存',
      type: 'line',
      data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 30) + 50),
      smooth: true,
      lineStyle: { color: '#67c23a' }
    })
  }
  
  if (resourceChartSeries.value.includes('disk')) {
    series.push({
      name: '磁盘',
      type: 'line',
      data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 20) + 15),
      smooth: true,
      lineStyle: { color: '#e6a23c' }
    })
  }
  
  if (resourceChartSeries.value.includes('network')) {
    series.push({
      name: '网络',
      type: 'line',
      data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 20) + 5),
      smooth: true,
      lineStyle: { color: '#f56c6c' }
    })
  }
  
  resourceChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: series.map(s => s.name)
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: timeData
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series
  })
}

const updateResponseTimeChart = () => {
  if (!responseTimeChart) return
  
  responseTimeChart.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '响应时间分布',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: '< 100ms' },
        { value: 735, name: '100-300ms' },
        { value: 580, name: '300-500ms' },
        { value: 484, name: '500ms-1s' },
        { value: 300, name: '> 1s' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

const updateErrorRateChart = () => {
  if (!errorRateChart) return
  
  const timeData = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date().getHours() - 23 + i
    return `${hour < 0 ? hour + 24 : hour}:00`
  })
  
  errorRateChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['4xx错误', '5xx错误']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: timeData
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: errorRateType.value === 'rate' ? '{value}%' : '{value}'
      }
    },
    series: [
      {
        name: '4xx错误',
        type: 'bar',
        stack: 'error',
        data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 50)),
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '5xx错误',
        type: 'bar',
        stack: 'error',
        data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 20)),
        itemStyle: { color: '#f56c6c' }
      }
    ]
  })
}

const updateThroughputChart = () => {
  if (!throughputChart) return
  
  const timeData = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date().getHours() - 23 + i
    return `${hour < 0 ? hour + 24 : hour}:00`
  })
  
  throughputChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: timeData
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: throughputMetric.value === 'requests' ? '请求数' : throughputMetric.value === 'tasks' ? '任务数' : '数据量',
      type: 'line',
      data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 1000) + 500),
      smooth: true,
      lineStyle: { color: '#409eff' },
      areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
    }]
  })
}

const handleTimeRangeChange = () => {
  customTimeRange.value = null
  loadPerformanceData()
}

const handleCustomRangeChange = () => {
  if (customTimeRange.value) {
    timeRange.value = 'custom'
    loadPerformanceData()
  }
}

const loadPerformanceData = async () => {
  loading.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    performanceData.value = generateMockPerformanceData()
    pagination.value.total = performanceData.value.length
    
    // 更新图表
    updateResourceChart()
    updateResponseTimeChart()
    updateErrorRateChart()
    updateThroughputChart()
  } catch (error) {
    ElMessage.error('加载性能数据失败')
  } finally {
    loading.value = false
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      loadPerformanceData()
    }, 30000)
    ElMessage.success('已开启自动刷新')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已停止自动刷新')
  }
}

const exportReport = async () => {
  exporting.value = true
  
  try {
    // 模拟导出过程
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
      '确定要重置所有性能指标吗？此操作不可撤销。',
      '确认重置',
      {
        type: 'warning'
      }
    )
    
    // 重置指标数据
    metrics.value = {
      cpu: { current: 0, average: 0, change: 0 },
      memory: { current: 0, average: 0, change: 0 },
      disk: { current: 0, average: 0, change: 0 },
      network: { current: 0, average: 0, change: 0 }
    }
    
    ElMessage.success('性能指标已重置')
  } catch (error) {
    // 用户取消操作
  }
}

const viewServiceDetails = (service: PerformanceData) => {
  selectedService.value = service
  detailDialogVisible.value = true
  
  nextTick(() => {
    initServiceCharts()
  })
}

const analyzeService = (service: PerformanceData) => {
  ElMessage.info(`正在分析 ${service.service} 服务性能...`)
  // 这里可以实现具体的分析逻辑
}

const initServiceCharts = () => {
  // 服务趋势图
  if (serviceTrendChartRef.value) {
    serviceTrendChart = echarts.init(serviceTrendChartRef.value)
    serviceTrendChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['响应时间', 'CPU使用率', '内存使用率']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: Array.from({ length: 24 }, (_, i) => {
          const hour = new Date().getHours() - 23 + i
          return `${hour < 0 ? hour + 24 : hour}:00`
        })
      },
      yAxis: [
        {
          type: 'value',
          name: '响应时间(ms)',
          position: 'left'
        },
        {
          type: 'value',
          name: '使用率(%)',
          position: 'right'
        }
      ],
      series: [
        {
          name: '响应时间',
          type: 'line',
          yAxisIndex: 0,
          data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 200) + 100),
          smooth: true,
          lineStyle: { color: '#409eff' }
        },
        {
          name: 'CPU使用率',
          type: 'line',
          yAxisIndex: 1,
          data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 40) + 30),
          smooth: true,
          lineStyle: { color: '#67c23a' }
        },
        {
          name: '内存使用率',
          type: 'line',
          yAxisIndex: 1,
          data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 30) + 50),
          smooth: true,
          lineStyle: { color: '#e6a23c' }
        }
      ]
    })
  }
  
  // 服务错误分析图
  if (serviceErrorChartRef.value) {
    serviceErrorChart = echarts.init(serviceErrorChartRef.value)
    serviceErrorChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: '错误类型分布',
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 35, name: '超时错误' },
          { value: 20, name: '连接错误' },
          { value: 15, name: '权限错误' },
          { value: 10, name: '参数错误' },
          { value: 20, name: '其他错误' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
}

const exportServiceReport = () => {
  ElMessage.success('服务报告导出成功')
}

const handleDetailClose = () => {
  detailDialogVisible.value = false
  selectedService.value = null
  activeTab.value = 'basic'
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  loadPerformanceData()
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
}

// 生命周期
onMounted(() => {
  loadPerformanceData()
  initTrendCharts()
  initMainCharts()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 销毁图表实例
  cpuTrendChart?.dispose()
  memoryTrendChart?.dispose()
  diskTrendChart?.dispose()
  networkTrendChart?.dispose()
  resourceChart?.dispose()
  responseTimeChart?.dispose()
  errorRateChart?.dispose()
  throughputChart?.dispose()
  serviceTrendChart?.dispose()
  serviceErrorChart?.dispose()
})
</script>

<style lang="scss" scoped>
.performance-container {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
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
  
  .time-range-section {
    margin-bottom: 24px;
    
    .time-range-controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .custom-range {
        margin-left: 16px;
      }
    }
  }
  
  .metrics-section {
    margin-bottom: 24px;
    
    .metric-card {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      padding: 20px;
      height: 140px;
      
      .metric-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
        
        .metric-icon {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: white;
          
          &.cpu {
            background: var(--el-color-primary);
          }
          
          &.memory {
            background: var(--el-color-success);
          }
          
          &.disk {
            background: var(--el-color-warning);
          }
          
          &.network {
            background: var(--el-color-danger);
          }
        }
        
        .metric-info {
          .metric-title {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            margin-bottom: 4px;
          }
          
          .metric-value {
            font-size: 24px;
            font-weight: 600;
            color: var(--el-text-color-primary);
          }
        }
      }
      
      .metric-trend {
        .trend-chart {
          height: 40px;
          margin-bottom: 8px;
        }
        
        .trend-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .trend-label {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
          
          .trend-change {
            font-size: 12px;
            font-weight: 600;
            
            &.positive {
              color: var(--el-color-danger);
            }
            
            &.negative {
              color: var(--el-color-success);
            }
          }
        }
      }
    }
  }
  
  .charts-section {
    margin-bottom: 24px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .chart-controls {
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }
    
    .chart-container {
      height: 300px;
    }
  }
  
  .details-section {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-actions {
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }
    
    .usage-text {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-left: 8px;
    }
    
    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 24px;
    }
  }
  
  .service-detail {
    .trend-charts,
    .error-analysis {
      .chart-container {
        height: 400px;
      }
    }
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

// 响应时间样式
.response-time-good {
  color: var(--el-color-success);
}

.response-time-normal {
  color: var(--el-color-warning);
}

.response-time-slow {
  color: var(--el-color-danger);
}

// 错误率样式
.error-rate-good {
  color: var(--el-color-success);
}

.error-rate-normal {
  color: var(--el-color-warning);
}

.error-rate-high {
  color: var(--el-color-danger);
}
</style>