<template>
  <div class="system-logs">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统日志</h1>
        <p class="page-description">查看和分析系统运行日志，支持实时监控和历史查询</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button :type="autoRefresh ? 'primary' : 'default'" @click="toggleAutoRefresh">
            <el-icon><Refresh /></el-icon>
            {{ autoRefresh ? '停止刷新' : '自动刷新' }}
          </el-button>
          <el-button @click="exportLogs" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
          <el-button @click="clearLogs" type="danger" plain>
            <el-icon><Delete /></el-icon>
            清空日志
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 过滤器 -->
    <div class="filters-section">
      <el-card>
        <el-form :model="filters" inline>
          <el-form-item label="日志级别">
            <el-select v-model="filters.level" placeholder="选择日志级别" clearable style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="DEBUG" value="debug" />
              <el-option label="INFO" value="info" />
              <el-option label="WARN" value="warn" />
              <el-option label="ERROR" value="error" />
              <el-option label="FATAL" value="fatal" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="服务">
            <el-select v-model="filters.service" placeholder="选择服务" clearable style="width: 150px;">
              <el-option label="全部" value="" />
              <el-option label="Web服务器" value="web" />
              <el-option label="API服务" value="api" />
              <el-option label="数据库" value="database" />
              <el-option label="任务队列" value="queue" />
              <el-option label="爬虫引擎" value="crawler" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filters.timeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 350px;"
            />
          </el-form-item>
          
          <el-form-item label="关键词">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索日志内容"
              clearable
              style="width: 200px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="searchLogs" :loading="loading">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon debug">
              <el-icon><InfoFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.debug }}</div>
              <div class="stat-label">DEBUG</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon info">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.info }}</div>
              <div class="stat-label">INFO</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon warn">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.warn }}</div>
              <div class="stat-label">WARN</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon error">
              <el-icon><CircleCloseFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.error }}</div>
              <div class="stat-label">ERROR</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 日志列表 -->
    <div class="logs-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>日志记录 (共 {{ pagination.total }} 条)</span>
            <div class="header-actions">
              <el-switch
                v-model="showTimestamp"
                active-text="显示时间戳"
                inactive-text="隐藏时间戳"
                size="small"
              />
              <el-switch
                v-model="wrapText"
                active-text="自动换行"
                inactive-text="不换行"
                size="small"
                style="margin-left: 16px;"
              />
              <el-switch
                v-model="followTail"
                active-text="跟随最新"
                inactive-text="停止跟随"
                size="small"
                style="margin-left: 16px;"
              />
            </div>
          </div>
        </template>
        
        <div class="logs-content" :class="{ 'wrap-text': wrapText }">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>
          
          <div v-else-if="logs.length === 0" class="empty-container">
            <el-empty description="暂无日志数据" />
          </div>
          
          <div v-else class="logs-list" ref="logsListRef">
            <div
              v-for="log in logs"
              :key="log.id"
              class="log-item"
              :class="log.level"
            >
              <div class="log-header">
                <div class="log-meta">
                  <el-tag :type="getLevelType(log.level)" size="small">
                    {{ log.level.toUpperCase() }}
                  </el-tag>
                  <span class="log-service">{{ log.service }}</span>
                  <span v-if="showTimestamp" class="log-timestamp">
                    {{ formatTimestamp(log.timestamp) }}
                  </span>
                </div>
                <div class="log-actions">
                  <el-button size="small" text @click="copyLog(log)">
                    <el-icon><CopyDocument /></el-icon>
                    复制
                  </el-button>
                  <el-button size="small" text @click="viewLogDetails(log)">
                    <el-icon><View /></el-icon>
                    详情
                  </el-button>
                </div>
              </div>
              
              <div class="log-content">
                <div class="log-message">{{ log.message }}</div>
                <div v-if="log.stack" class="log-stack">
                  <el-collapse>
                    <el-collapse-item title="堆栈信息" name="stack">
                      <pre>{{ log.stack }}</pre>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
              
              <div v-if="log.context" class="log-context">
                <div class="context-title">上下文信息:</div>
                <div class="context-content">
                  <span v-for="(value, key) in log.context" :key="key" class="context-item">
                    <strong>{{ key }}:</strong> {{ value }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 日志详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="日志详情" width="800px">
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="时间">
            {{ formatTimestamp(selectedLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelType(selectedLog.level)">
              {{ selectedLog.level.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="服务">
            {{ selectedLog.service }}
          </el-descriptions-item>
          <el-descriptions-item label="线程ID">
            {{ selectedLog.threadId || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="消息" :span="2">
            <div class="log-message-detail">{{ selectedLog.message }}</div>
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedLog.stack" class="stack-section">
          <h4>堆栈信息</h4>
          <pre class="stack-content">{{ selectedLog.stack }}</pre>
        </div>
        
        <div v-if="selectedLog.context" class="context-section">
          <h4>上下文信息</h4>
          <el-table :data="contextTableData" border>
            <el-table-column prop="key" label="键" width="200" />
            <el-table-column prop="value" label="值" />
          </el-table>
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
  Delete, 
  Search, 
  InfoFilled, 
  SuccessFilled, 
  Warning, 
  CircleCloseFilled,
  CopyDocument,
  View
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const autoRefresh = ref(false)
const showTimestamp = ref(true)
const wrapText = ref(false)
const followTail = ref(false)
const detailDialogVisible = ref(false)
const selectedLog = ref(null)

// 过滤器
const filters = ref({
  level: '',
  service: '',
  timeRange: [],
  keyword: ''
})

// 统计信息
const stats = ref({
  debug: 1245,
  info: 3421,
  warn: 89,
  error: 23
})

// 分页
const pagination = ref({
  page: 1,
  pageSize: 50,
  total: 4778
})

// 日志列表
const logs = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    level: 'info',
    service: 'web',
    message: '用户登录成功',
    context: {
      userId: '12345',
      ip: '192.168.1.100',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
    level: 'warn',
    service: 'api',
    message: 'API请求频率过高，触发限流',
    context: {
      endpoint: '/api/v1/tasks',
      ip: '192.168.1.101',
      requestCount: 150
    }
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    level: 'error',
    service: 'database',
    message: '数据库连接超时',
    stack: 'Error: Connection timeout\n    at Database.connect (/app/db.js:45:12)\n    at async TaskService.create (/app/services/task.js:23:5)',
    context: {
      database: 'postgresql',
      timeout: '30s',
      retryCount: 3
    }
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 20 * 60 * 1000),
    level: 'debug',
    service: 'crawler',
    message: '开始执行爬虫任务',
    context: {
      taskId: 'task_001',
      url: 'https://example.com',
      config: 'news_crawler'
    }
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 25 * 60 * 1000),
    level: 'info',
    service: 'queue',
    message: '任务队列处理完成',
    context: {
      queueName: 'default',
      processedCount: 45,
      failedCount: 2
    }
  }
])

// 引用
const logsListRef = ref()

// 自动刷新定时器
let refreshTimer = null

// 计算属性
const contextTableData = computed(() => {
  if (!selectedLog.value?.context) return []
  return Object.entries(selectedLog.value.context).map(([key, value]) => ({
    key,
    value: typeof value === 'object' ? JSON.stringify(value) : String(value)
  }))
})

// 方法
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    refreshTimer = setInterval(fetchLogs, 5000) // 5秒刷新一次
    ElMessage.success('已开启自动刷新')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已停止自动刷新')
  }
}

const fetchLogs = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 如果开启跟随最新，滚动到底部
    if (followTail.value) {
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

const searchLogs = async () => {
  loading.value = true
  try {
    // 模拟搜索API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('搜索完成')
  } catch (error) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    level: '',
    service: '',
    timeRange: [],
    keyword: ''
  }
  searchLogs()
}

const exportLogs = async () => {
  exporting.value = true
  try {
    // 模拟导出
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('日志导出成功')
  } catch (error) {
    ElMessage.error('日志导出失败')
  } finally {
    exporting.value = false
  }
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟清空操作
    logs.value = []
    pagination.value.total = 0
    ElMessage.success('日志已清空')
  } catch {
    // 用户取消
  }
}

const getLevelType = (level) => {
  const types = {
    debug: 'info',
    info: 'success',
    warn: 'warning',
    error: 'danger',
    fatal: 'danger'
  }
  return types[level] || 'info'
}

const formatTimestamp = (timestamp) => {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss.SSS')
}

const copyLog = async (log) => {
  try {
    const logText = `[${formatTimestamp(log.timestamp)}] [${log.level.toUpperCase()}] [${log.service}] ${log.message}`
    await navigator.clipboard.writeText(logText)
    ElMessage.success('日志已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const viewLogDetails = (log) => {
  selectedLog.value = log
  detailDialogVisible.value = true
}

const handleSizeChange = (size) => {
  pagination.value.pageSize = size
  fetchLogs()
}

const handleCurrentChange = (page) => {
  pagination.value.page = page
  fetchLogs()
}

const scrollToBottom = () => {
  if (logsListRef.value) {
    logsListRef.value.scrollTop = logsListRef.value.scrollHeight
  }
}

// 生命周期
onMounted(() => {
  fetchLogs()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.system-logs {
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

.filters-section {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.stat-icon.debug {
  background: #6b7280;
}

.stat-icon.info {
  background: #10b981;
}

.stat-icon.warn {
  background: #f59e0b;
}

.stat-icon.error {
  background: #ef4444;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

.logs-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logs-content {
  max-height: 600px;
  overflow-y: auto;
}

.logs-content.wrap-text .log-message {
  white-space: pre-wrap;
  word-break: break-all;
}

.loading-container,
.empty-container {
  padding: 40px;
  text-align: center;
}

.logs-list {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.log-item {
  border-bottom: 1px solid #f3f4f6;
  padding: 16px;
  background: white;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.debug {
  border-left: 4px solid #6b7280;
}

.log-item.info {
  border-left: 4px solid #10b981;
}

.log-item.warn {
  border-left: 4px solid #f59e0b;
}

.log-item.error {
  border-left: 4px solid #ef4444;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.log-service {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
}

.log-timestamp {
  font-size: 12px;
  color: #9ca3af;
  font-family: monospace;
}

.log-actions {
  display: flex;
  gap: 8px;
}

.log-content {
  margin-bottom: 8px;
}

.log-message {
  color: #1f2937;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
}

.log-stack {
  margin-top: 8px;
}

.log-stack pre {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #6b7280;
  overflow-x: auto;
}

.log-context {
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.context-title {
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.context-content {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.context-item {
  color: #6b7280;
}

.context-item strong {
  color: #374151;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.log-detail .log-message-detail {
  font-family: monospace;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
}

.stack-section,
.context-section {
  margin-top: 20px;
}

.stack-section h4,
.context-section h4 {
  margin: 0 0 12px 0;
  color: #374151;
}

.stack-content {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #6b7280;
  overflow-x: auto;
  max-height: 300px;
}
</style>