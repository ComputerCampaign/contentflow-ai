<template>
  <div class="task-monitor-page">
    <PageHeader title="任务监控" description="实时监控任务执行状态" />
    
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon running">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.running }}</div>
              <div class="stat-label">运行中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">等待中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon failed">
              <el-icon><Close /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.failed }}</div>
              <div class="stat-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 过滤器 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable>
            <el-option label="运行中" value="running" />
            <el-option label="等待中" value="pending" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filters.priority" placeholder="全部优先级" clearable>
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
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
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button :icon="Refresh" @click="handleRefresh" :loading="loading">
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <div class="header-actions">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="handleAutoRefreshChange"
            />
          </div>
        </div>
      </template>
      
      <div v-loading="loading" class="task-list">
        <div v-if="tasks.length === 0" class="empty-state">
          <el-empty description="暂无任务" />
        </div>
        <div v-else class="task-items">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="task-item"
            :class="`task-${task.status}`"
          >
            <div class="task-header">
              <div class="task-title">
                <h4>{{ task.name }}</h4>
                <el-tag :type="getStatusType(task.status)" size="small">
                  {{ getStatusText(task.status) }}
                </el-tag>
              </div>
              <div class="task-actions">
                <el-button
                  v-if="task.status === 'pending' || task.status === 'paused'"
                  type="primary"
                  size="small"
                  :icon="VideoPlay"
                  @click="handleStart(task)"
                >
                  启动
                </el-button>
                <el-button
                  v-if="task.status === 'running'"
                  type="warning"
                  size="small"
                  :icon="VideoPause"
                  @click="handlePause(task)"
                >
                  暂停
                </el-button>
                <el-button
                  v-if="task.status === 'running' || task.status === 'paused'"
                  type="danger"
                  size="small"
                  :icon="SwitchButton"
                  @click="handleStop(task)"
                >
                  停止
                </el-button>
                <el-button
                  size="small"
                  :icon="View"
                  @click="handleView(task)"
                >
                  详情
                </el-button>
              </div>
            </div>
            
            <div class="task-info">
              <div class="info-item">
                <span class="label">爬虫配置：</span>
                <span class="value">{{ task.crawlerConfig?.name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">优先级：</span>
                <el-tag :type="getPriorityType(task.priority)" size="small">
                  {{ getPriorityText(task.priority) }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">创建时间：</span>
                <span class="value">{{ formatTime(task.createdAt) }}</span>
              </div>
              <div v-if="task.startedAt" class="info-item">
                <span class="label">开始时间：</span>
                <span class="value">{{ formatTime(task.startedAt) }}</span>
              </div>
            </div>
            
            <div class="task-progress">
              <div class="progress-info">
                <span>进度：{{ task.progress || 0 }}%</span>
                <span v-if="task.totalPages">
                  ({{ task.processedPages || 0 }}/{{ task.totalPages }})
                </span>
              </div>
              <el-progress
                :percentage="task.progress || 0"
                :status="task.status === 'failed' ? 'exception' : undefined"
                :stroke-width="8"
              />
            </div>
            
            <div v-if="task.status === 'running'" class="task-stats">
              <div class="stat-item">
                <span class="stat-label">成功：</span>
                <span class="stat-value success">{{ task.successPages || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">失败：</span>
                <span class="stat-value error">{{ task.failedPages || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">速度：</span>
                <span class="stat-value">{{ task.speed || 0 }} 页/分钟</span>
              </div>
              <div v-if="task.estimatedTime" class="stat-item">
                <span class="stat-label">预计完成：</span>
                <span class="stat-value">{{ task.estimatedTime }}</span>
              </div>
            </div>
            
            <div v-if="task.error" class="task-error">
              <el-alert
                :title="task.error.message"
                type="error"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 任务详情抽屉 -->
    <TaskDetailDrawer
      v-model="detailVisible"
      :task="currentTask"
      @refresh="handleRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  SwitchButton,
  View,
  Refresh,
  Clock,
  Check,
  Close
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import PageHeader from '@/components/common/PageHeader.vue'
import TaskDetailDrawer from './components/TaskDetailDrawer.vue'

// 状态管理
const taskStore = useTaskStore()

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(true)
const detailVisible = ref(false)
const currentTask = ref<any>(null)
const refreshTimer = ref<number | null>(null)

// 统计数据
const stats = reactive({
  running: 0,
  pending: 0,
  completed: 0,
  failed: 0
})

// 过滤器
const filters = reactive({
  status: '',
  priority: '',
  dateRange: null as [string, string] | null
})

// 任务列表
const tasks = ref<any[]>([])

// 状态相关方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'info',
    running: 'success',
    paused: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getPriorityType = (priority: string) => {
  const priorityMap: Record<string, string> = {
    low: 'info',
    medium: 'warning',
    high: 'danger'
  }
  return priorityMap[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const priorityMap: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return priorityMap[priority] || priority
}

// 工具方法
const formatTime = (time: string | null) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

// 数据加载方法
const loadTasks = async () => {
  loading.value = true
  try {
    const queryParams: any = {}
    
    if (filters.status) {
      queryParams.status = filters.status
    }
    if (filters.priority) {
      queryParams.priority = filters.priority
    }
    if (filters.dateRange) {
      queryParams.startTime = filters.dateRange[0]
      queryParams.endTime = filters.dateRange[1]
    }
    
    await taskStore.fetchTasks(queryParams)
    tasks.value = taskStore.tasks
    
    // 更新统计数据
    updateStats()
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const statusCounts = tasks.value.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  stats.running = statusCounts.running || 0
  stats.pending = statusCounts.pending || 0
  stats.completed = statusCounts.completed || 0
  stats.failed = statusCounts.failed || 0
}

// 事件处理方法
const handleRefresh = () => {
  loadTasks()
}

const handleFilter = () => {
  loadTasks()
}

const handleReset = () => {
  filters.status = ''
  filters.priority = ''
  filters.dateRange = null
  loadTasks()
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
    loadTasks()
  }, 5000) // 每5秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

const handleView = (task: any) => {
  currentTask.value = task
  detailVisible.value = true
}

const handleStart = async (task: any) => {
  try {
    await taskStore.startTask(task.id)
    ElMessage.success('任务启动成功')
    loadTasks()
  } catch (error) {
    ElMessage.error('任务启动失败')
  }
}

const handlePause = async (task: any) => {
  try {
    await taskStore.pauseTask(task.id)
    ElMessage.success('任务暂停成功')
    loadTasks()
  } catch (error) {
    ElMessage.error('任务暂停失败')
  }
}

const handleStop = async (task: any) => {
  try {
    await taskStore.stopTask(task.id)
    ElMessage.success('任务停止成功')
    loadTasks()
  } catch (error) {
    ElMessage.error('任务停止失败')
  }
}

// 生命周期
onMounted(() => {
  loadTasks()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
.task-monitor-page {
  padding: 24px;
  
  .stats-row {
    margin-bottom: 24px;
    
    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;
        
        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: white;
          
          &.running {
            background: var(--el-color-success);
          }
          
          &.pending {
            background: var(--el-color-info);
          }
          
          &.completed {
            background: var(--el-color-primary);
          }
          
          &.failed {
            background: var(--el-color-danger);
          }
        }
        
        .stat-info {
          .stat-value {
            font-size: 24px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            line-height: 1;
          }
          
          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin-top: 4px;
          }
        }
      }
    }
  }
  
  .filter-card {
    margin-bottom: 24px;
  }
  
  .task-list-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .task-list {
      .empty-state {
        padding: 40px 0;
      }
      
      .task-items {
        .task-item {
          border: 1px solid var(--el-border-color);
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 16px;
          transition: all 0.3s;
          
          &:hover {
            box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
          }
          
          &.task-running {
            border-left: 4px solid var(--el-color-success);
          }
          
          &.task-failed {
            border-left: 4px solid var(--el-color-danger);
          }
          
          &.task-completed {
            border-left: 4px solid var(--el-color-primary);
          }
          
          .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            
            .task-title {
              display: flex;
              align-items: center;
              gap: 12px;
              
              h4 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
              }
            }
            
            .task-actions {
              display: flex;
              gap: 8px;
            }
          }
          
          .task-info {
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
            margin-bottom: 16px;
            
            .info-item {
              display: flex;
              align-items: center;
              gap: 4px;
              
              .label {
                color: var(--el-text-color-secondary);
                font-size: 14px;
              }
              
              .value {
                color: var(--el-text-color-primary);
                font-size: 14px;
              }
            }
          }
          
          .task-progress {
            margin-bottom: 16px;
            
            .progress-info {
              display: flex;
              justify-content: space-between;
              margin-bottom: 8px;
              font-size: 14px;
              color: var(--el-text-color-secondary);
            }
          }
          
          .task-stats {
            display: flex;
            gap: 24px;
            margin-bottom: 16px;
            
            .stat-item {
              display: flex;
              align-items: center;
              gap: 4px;
              
              .stat-label {
                color: var(--el-text-color-secondary);
                font-size: 14px;
              }
              
              .stat-value {
                font-size: 14px;
                font-weight: 600;
                
                &.success {
                  color: var(--el-color-success);
                }
                
                &.error {
                  color: var(--el-color-danger);
                }
              }
            }
          }
          
          .task-error {
            margin-top: 16px;
          }
        }
      }
    }
  }
}
</style>