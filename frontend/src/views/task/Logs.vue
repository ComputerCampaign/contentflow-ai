<template>
  <div class="task-logs-page">
    <PageHeader title="任务日志" description="查看任务执行详细日志" />
    
    <!-- 过滤器 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="任务">
          <el-select v-model="filters.taskId" placeholder="选择任务" clearable filterable>
            <el-option
              v-for="task in taskList"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日志级别">
          <el-select v-model="filters.level" placeholder="全部级别" clearable>
            <el-option label="调试" value="debug" />
            <el-option label="信息" value="info" />
            <el-option label="警告" value="warn" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索日志内容"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button :icon="Refresh" @click="handleRefresh" :loading="loading">
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 日志列表 -->
    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <span>执行日志</span>
          <div class="header-actions">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="handleAutoRefreshChange"
            />
            <el-button
              type="primary"
              size="small"
              :icon="Download"
              @click="handleExport"
            >
              导出日志
            </el-button>
          </div>
        </div>
      </template>
      
      <div v-loading="loading" class="logs-container">
        <div v-if="logs.length === 0" class="empty-state">
          <el-empty description="暂无日志" />
        </div>
        <div v-else class="log-list">
          <div
            v-for="log in logs"
            :key="log.id"
            class="log-item"
            :class="`log-${log.level}`"
          >
            <div class="log-header">
              <div class="log-meta">
                <el-tag :type="getLevelType(log.level)" size="small">
                  {{ getLevelText(log.level) }}
                </el-tag>
                <span class="log-time">{{ formatTime(log.createdAt) }}</span>
                <span v-if="log.taskName" class="log-task">{{ log.taskName }}</span>
              </div>
              <div class="log-actions">
                <el-button
                  size="small"
                  text
                  @click="handleCopyLog(log)"
                >
                  复制
                </el-button>
              </div>
            </div>
            <div class="log-content">
              <pre>{{ log.message }}</pre>
              <div v-if="log.details" class="log-details">
                <el-collapse>
                  <el-collapse-item title="详细信息">
                    <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div v-if="total > 0" class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :total="total"
            :page-sizes="[20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import PageHeader from '@/components/common/PageHeader.vue'

// 状态管理
const taskStore = useTaskStore()

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(false)
const refreshTimer = ref<number | null>(null)
const taskList = ref<any[]>([])
const logs = ref<any[]>([])
const total = ref(0)

// 过滤器
const filters = reactive({
  taskId: '',
  level: '',
  dateRange: null as [string, string] | null,
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 50
})

// 日志级别相关方法
const getLevelType = (level: string) => {
  const levelMap: Record<string, string> = {
    debug: 'info',
    info: 'success',
    warn: 'warning',
    error: 'danger'
  }
  return levelMap[level] || 'info'
}

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    debug: '调试',
    info: '信息',
    warn: '警告',
    error: '错误'
  }
  return levelMap[level] || level
}

// 工具方法
const formatTime = (time: string | null) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

// 数据加载方法
const loadTaskList = async () => {
  try {
    await taskStore.fetchTasks()
    taskList.value = taskStore.tasks
  } catch (error) {
    console.error('加载任务列表失败:', error)
  }
}

const loadLogs = async () => {
  loading.value = true
  try {
    const queryParams: any = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (filters.taskId) {
      queryParams.taskId = filters.taskId
    }
    if (filters.level) {
      queryParams.level = filters.level
    }
    if (filters.keyword) {
      queryParams.keyword = filters.keyword
    }
    if (filters.dateRange) {
      queryParams.startTime = filters.dateRange[0]
      queryParams.endTime = filters.dateRange[1]
    }
    
    await taskStore.fetchTaskLogs(queryParams.taskId, {
      page: queryParams.page,
      pageSize: queryParams.pageSize
    })
    logs.value = taskStore.taskLogs
    total.value = taskStore.taskLogs.length
  } catch (error) {
    console.error('获取日志失败:', error)
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

// 事件处理方法
const handleRefresh = () => {
  loadLogs()
}

const handleFilter = () => {
  pagination.page = 1
  loadLogs()
}

const handleReset = () => {
  filters.taskId = ''
  filters.level = ''
  filters.dateRange = null
  filters.keyword = ''
  pagination.page = 1
  loadLogs()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  loadLogs()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadLogs()
}

const handleAutoRefreshChange = (value: boolean) => {
  if (value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  
  refreshTimer.value = setInterval(() => {
    loadLogs()
  }, 10000) // 每10秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

const handleCopyLog = async (log: any) => {
  try {
    const logText = `[${formatTime(log.createdAt)}] [${getLevelText(log.level)}] ${log.message}`
    await navigator.clipboard.writeText(logText)
    ElMessage.success('日志已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleExport = async () => {
  try {
    const queryParams: any = {
      export: true
    }
    
    if (filters.taskId) {
      queryParams.taskId = filters.taskId
    }
    if (filters.level) {
      queryParams.level = filters.level
    }
    if (filters.keyword) {
      queryParams.keyword = filters.keyword
    }
    if (filters.dateRange) {
      queryParams.startTime = filters.dateRange[0]
      queryParams.endTime = filters.dateRange[1]
    }
    
    await taskStore.exportTaskLogs(queryParams)
    ElMessage.success('日志导出成功')
  } catch (error) {
    console.error('导出日志失败:', error)
    ElMessage.error('导出日志失败')
  }
}

// 生命周期
onMounted(async () => {
  await loadTaskList()
  await loadLogs()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
.task-logs-page {
  padding: 24px;
  
  .filter-card {
    margin-bottom: 24px;
  }
  
  .logs-card {
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
    
    .logs-container {
      .empty-state {
        padding: 40px 0;
      }
      
      .log-list {
        .log-item {
          border: 1px solid var(--el-border-color);
          border-radius: 8px;
          margin-bottom: 12px;
          overflow: hidden;
          
          &.log-debug {
            border-left: 4px solid var(--el-color-info);
          }
          
          &.log-info {
            border-left: 4px solid var(--el-color-success);
          }
          
          &.log-warn {
            border-left: 4px solid var(--el-color-warning);
          }
          
          &.log-error {
            border-left: 4px solid var(--el-color-danger);
          }
          
          .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background-color: var(--el-fill-color-lighter);
            border-bottom: 1px solid var(--el-border-color);
            
            .log-meta {
              display: flex;
              align-items: center;
              gap: 12px;
              
              .log-time {
                font-size: 12px;
                color: var(--el-text-color-secondary);
                font-family: monospace;
              }
              
              .log-task {
                font-size: 12px;
                color: var(--el-text-color-regular);
                background-color: var(--el-fill-color);
                padding: 2px 8px;
                border-radius: 4px;
              }
            }
          }
          
          .log-content {
            padding: 16px;
            
            pre {
              margin: 0;
              font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
              font-size: 13px;
              line-height: 1.5;
              color: var(--el-text-color-primary);
              white-space: pre-wrap;
              word-break: break-all;
            }
            
            .log-details {
              margin-top: 12px;
              
              :deep(.el-collapse-item__header) {
                font-size: 12px;
                padding-left: 0;
              }
              
              :deep(.el-collapse-item__content) {
                padding-bottom: 0;
                
                pre {
                  background-color: var(--el-fill-color-lighter);
                  padding: 12px;
                  border-radius: 4px;
                  font-size: 12px;
                }
              }
            }
          }
        }
      }
      
      .pagination {
        display: flex;
        justify-content: center;
        margin-top: 24px;
      }
    }
  }
}
</style>