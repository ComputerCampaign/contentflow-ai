<template>
  <div class="logs-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统日志</h1>
        <p class="page-description">查看和分析系统运行日志</p>
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
              <div class="stat-icon warn">
                <el-icon><Warning /></el-icon>
              </div>
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
          
          <div v-else class="logs-list">
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
                  </el-button>
                  <el-button size="small" text @click="viewLogDetails(log)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </div>
              </div>
              
              <div class="log-content">
                <div class="log-message" v-html="highlightKeyword(log.message)"></div>
                <div v-if="log.stack" class="log-stack">
                  <el-collapse>
                    <el-collapse-item title="查看堆栈信息">
                      <pre class="stack-trace">{{ log.stack }}</pre>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[20, 50, 100, 200]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="80%"
      :before-close="handleDetailClose"
    >
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志级别">
            <el-tag :type="getLevelType(selectedLog.level)">
              {{ selectedLog.level.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="服务名称">
            {{ selectedLog.service }}
          </el-descriptions-item>
          <el-descriptions-item label="时间戳">
            {{ formatTimestamp(selectedLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="请求ID">
            {{ selectedLog.requestId || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="用户ID">
            {{ selectedLog.userId || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">
            {{ selectedLog.ip || 'N/A' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-section">
          <h4>日志消息</h4>
          <div class="message-content">
            {{ selectedLog.message }}
          </div>
        </div>
        
        <div v-if="selectedLog.stack" class="detail-section">
          <h4>堆栈信息</h4>
          <pre class="stack-content">{{ selectedLog.stack }}</pre>
        </div>
        
        <div v-if="selectedLog.context" class="detail-section">
          <h4>上下文信息</h4>
          <pre class="context-content">{{ JSON.stringify(selectedLog.context, null, 2) }}</pre>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="copyLogDetail">复制详情</el-button>
          <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
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

interface LogEntry {
  id: string
  level: 'debug' | 'info' | 'warn' | 'error' | 'fatal'
  service: string
  message: string
  timestamp: number
  stack?: string
  requestId?: string
  userId?: string
  ip?: string
  context?: any
}

interface LogFilters {
  level: string
  service: string
  timeRange: [string, string] | null
  keyword: string
}

interface LogStats {
  debug: number
  info: number
  warn: number
  error: number
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
const showTimestamp = ref(true)
const wrapText = ref(false)
const detailDialogVisible = ref(false)

const filters = ref<LogFilters>({
  level: '',
  service: '',
  timeRange: null,
  keyword: ''
})

const stats = ref<LogStats>({
  debug: 1245,
  info: 3567,
  warn: 89,
  error: 23
})

const pagination = ref<Pagination>({
  page: 1,
  size: 50,
  total: 4924
})

const logs = ref<LogEntry[]>([])
const selectedLog = ref<LogEntry | null>(null)

// 定时器
let refreshTimer: number | null = null

// 计算属性
const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    if (filters.value.level && log.level !== filters.value.level) {
      return false
    }
    if (filters.value.service && log.service !== filters.value.service) {
      return false
    }
    if (filters.value.keyword && !log.message.toLowerCase().includes(filters.value.keyword.toLowerCase())) {
      return false
    }
    return true
  })
})

// 方法
const getLevelType = (level: string) => {
  switch (level) {
    case 'debug':
      return 'info'
    case 'info':
      return 'success'
    case 'warn':
      return 'warning'
    case 'error':
    case 'fatal':
      return 'danger'
    default:
      return 'info'
  }
}

const formatTimestamp = (timestamp: number) => {
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const highlightKeyword = (text: string) => {
  if (!filters.value.keyword) {
    return text
  }
  
  const keyword = filters.value.keyword
  const regex = new RegExp(`(${keyword})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

const generateMockLogs = (): LogEntry[] => {
  const services = ['web', 'api', 'database', 'queue', 'crawler']
  const levels: LogEntry['level'][] = ['debug', 'info', 'warn', 'error']
  const messages = [
    '用户登录成功',
    '数据库连接建立',
    '任务执行完成',
    '爬虫任务启动',
    '内存使用率过高',
    '网络连接超时',
    '数据解析失败',
    '缓存更新成功',
    '文件上传完成',
    'API请求处理'
  ]
  
  const mockLogs: LogEntry[] = []
  
  for (let i = 0; i < pagination.value.size; i++) {
    const level = levels[Math.floor(Math.random() * levels.length)]
    const service = services[Math.floor(Math.random() * services.length)]
    const message = messages[Math.floor(Math.random() * messages.length)]
    
    mockLogs.push({
      id: `log_${Date.now()}_${i}`,
      level,
      service,
      message: `${message} - ${Math.random().toString(36).substring(7)}`,
      timestamp: Date.now() - Math.floor(Math.random() * 86400000),
      requestId: `req_${Math.random().toString(36).substring(7)}`,
      userId: Math.random() > 0.5 ? `user_${Math.floor(Math.random() * 1000)}` : undefined,
      ip: `192.168.1.${Math.floor(Math.random() * 255)}`,
      stack: level === 'error' ? `Error: ${message}\n    at Function.handler (/app/src/handler.js:123:45)\n    at Router.route (/app/src/router.js:67:12)` : undefined,
      context: {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        referer: 'https://example.com',
        method: 'GET'
      }
    })
  }
  
  return mockLogs.sort((a, b) => b.timestamp - a.timestamp)
}

const searchLogs = async () => {
  loading.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    logs.value = generateMockLogs()
    
    ElMessage.success('日志搜索完成')
  } catch (error) {
    ElMessage.error('日志搜索失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    level: '',
    service: '',
    timeRange: null,
    keyword: ''
  }
  searchLogs()
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      searchLogs()
    }, 10000)
    ElMessage.success('已开启自动刷新')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已停止自动刷新')
  }
}

const exportLogs = async () => {
  exporting.value = true
  
  try {
    // 模拟导出过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 创建CSV内容
    const csvContent = [
      ['时间', '级别', '服务', '消息', '请求ID', '用户ID', 'IP地址'].join(','),
      ...logs.value.map(log => [
        formatTimestamp(log.timestamp),
        log.level.toUpperCase(),
        log.service,
        `"${log.message}"`,
        log.requestId || '',
        log.userId || '',
        log.ip || ''
      ].join(','))
    ].join('\n')
    
    // 创建下载链接
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `logs_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
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
      '确定要清空所有日志吗？此操作不可撤销。',
      '确认清空',
      {
        type: 'warning'
      }
    )
    
    logs.value = []
    pagination.value.total = 0
    
    ElMessage.success('日志已清空')
  } catch (error) {
    // 用户取消操作
  }
}

const copyLog = async (log: LogEntry) => {
  try {
    const logText = `[${formatTimestamp(log.timestamp)}] [${log.level.toUpperCase()}] [${log.service}] ${log.message}`
    await navigator.clipboard.writeText(logText)
    ElMessage.success('日志已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const viewLogDetails = (log: LogEntry) => {
  selectedLog.value = log
  detailDialogVisible.value = true
}

const copyLogDetail = async () => {
  if (!selectedLog.value) return
  
  try {
    const logDetail = {
      timestamp: formatTimestamp(selectedLog.value.timestamp),
      level: selectedLog.value.level.toUpperCase(),
      service: selectedLog.value.service,
      message: selectedLog.value.message,
      requestId: selectedLog.value.requestId,
      userId: selectedLog.value.userId,
      ip: selectedLog.value.ip,
      stack: selectedLog.value.stack,
      context: selectedLog.value.context
    }
    
    await navigator.clipboard.writeText(JSON.stringify(logDetail, null, 2))
    ElMessage.success('日志详情已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleDetailClose = () => {
  detailDialogVisible.value = false
  selectedLog.value = null
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  searchLogs()
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
  searchLogs()
}

// 生命周期
onMounted(() => {
  searchLogs()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style lang="scss" scoped>
.logs-container {
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
  
  .filters-section {
    margin-bottom: 24px;
    
    :deep(.el-card__body) {
      padding: 20px;
    }
    
    :deep(.el-form--inline .el-form-item) {
      margin-right: 16px;
      margin-bottom: 16px;
    }
  }
  
  .stats-section {
    margin-bottom: 24px;
    
    .stat-card {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      
      .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: white;
        
        &.debug {
          background: var(--el-color-info);
        }
        
        &.info {
          background: var(--el-color-success);
        }
        
        &.warn {
          background: var(--el-color-warning);
        }
        
        &.error {
          background: var(--el-color-danger);
        }
      }
      
      .stat-content {
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
  
  .logs-section {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-actions {
        display: flex;
        align-items: center;
      }
    }
    
    .logs-content {
      min-height: 400px;
      
      &.wrap-text {
        .log-message {
          white-space: pre-wrap;
          word-break: break-word;
        }
      }
      
      .loading-container,
      .empty-container {
        padding: 40px 0;
      }
      
      .logs-list {
        .log-item {
          border: 1px solid var(--el-border-color-lighter);
          border-radius: 8px;
          margin-bottom: 12px;
          overflow: hidden;
          
          &.debug {
            border-left: 4px solid var(--el-color-info);
          }
          
          &.info {
            border-left: 4px solid var(--el-color-success);
          }
          
          &.warn {
            border-left: 4px solid var(--el-color-warning);
          }
          
          &.error,
          &.fatal {
            border-left: 4px solid var(--el-color-danger);
          }
          
          .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: var(--el-fill-color-lighter);
            border-bottom: 1px solid var(--el-border-color-lighter);
            
            .log-meta {
              display: flex;
              align-items: center;
              gap: 12px;
              
              .log-service {
                font-size: 12px;
                color: var(--el-text-color-secondary);
                background: var(--el-fill-color);
                padding: 2px 8px;
                border-radius: 4px;
              }
              
              .log-timestamp {
                font-size: 12px;
                color: var(--el-text-color-secondary);
                font-family: monospace;
              }
            }
            
            .log-actions {
              display: flex;
              gap: 4px;
            }
          }
          
          .log-content {
            padding: 16px;
            
            .log-message {
              font-family: monospace;
              font-size: 13px;
              line-height: 1.5;
              color: var(--el-text-color-primary);
              white-space: nowrap;
              overflow-x: auto;
              
              :deep(mark) {
                background: var(--el-color-warning-light-7);
                color: var(--el-color-warning-dark-2);
                padding: 2px 4px;
                border-radius: 2px;
              }
            }
            
            .log-stack {
              margin-top: 12px;
              
              .stack-trace {
                font-family: monospace;
                font-size: 12px;
                color: var(--el-text-color-secondary);
                background: var(--el-fill-color-lighter);
                padding: 12px;
                border-radius: 4px;
                overflow-x: auto;
              }
            }
          }
        }
      }
    }
    
    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 24px;
    }
  }
  
  .log-detail {
    .detail-section {
      margin-top: 24px;
      
      h4 {
        font-size: 14px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 12px 0;
      }
      
      .message-content {
        background: var(--el-fill-color-lighter);
        padding: 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-word;
      }
      
      .stack-content,
      .context-content {
        background: var(--el-fill-color-lighter);
        padding: 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        line-height: 1.4;
        overflow-x: auto;
        max-height: 300px;
        overflow-y: auto;
      }
    }
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>