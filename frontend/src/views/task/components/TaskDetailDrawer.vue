<template>
  <el-drawer
    v-model="visible"
    title="任务详情"
    size="60%"
    direction="rtl"
    :before-close="handleClose"
  >
    <div v-if="task" class="task-detail">
      <!-- 基本信息 -->
      <div class="detail-section">
        <h3 class="section-title">基本信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">
            {{ task.name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(task.status)" size="small">
              {{ getStatusText(task.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(task.priority)" size="small">
              {{ getPriorityText(task.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">
            <el-progress
              :percentage="task.progress || 0"
              :status="task.status === 'failed' ? 'exception' : undefined"
            />
          </el-descriptions-item>
          <el-descriptions-item label="爬虫配置">
            {{ task.crawlerConfig?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(task.createdAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatTime(task.startedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ formatTime(task.completedAt) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 任务描述 -->
      <div v-if="task.description" class="detail-section">
        <h3 class="section-title">任务描述</h3>
        <div class="description-content">
          {{ task.description }}
        </div>
      </div>
      
      <!-- 执行统计 -->
      <div class="detail-section">
        <h3 class="section-title">执行统计</h3>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-statistic title="总页面数" :value="task.totalPages || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已处理" :value="task.processedPages || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="成功数" :value="task.successPages || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败数" :value="task.failedPages || 0" />
          </el-col>
        </el-row>
      </div>
      
      <!-- 配置参数 -->
      <div v-if="task.config" class="detail-section">
        <h3 class="section-title">配置参数</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="最大页面数">
            {{ task.config.maxPages || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="并发数">
            {{ task.config.concurrency || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="延迟时间">
            {{ task.config.delay || '-' }}ms
          </el-descriptions-item>
          <el-descriptions-item label="超时时间">
            {{ task.config.timeout || '-' }}ms
          </el-descriptions-item>
          <el-descriptions-item label="重试次数">
            {{ task.config.retries || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="输出格式">
            {{ task.config.outputFormat || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 执行日志 -->
      <div class="detail-section">
        <h3 class="section-title">
          执行日志
          <el-button
            size="small"
            :icon="Refresh"
            @click="refreshLogs"
            :loading="logsLoading"
          >
            刷新
          </el-button>
        </h3>
        <div class="logs-container">
          <el-scrollbar height="300px">
            <div v-if="logs.length === 0" class="empty-logs">
              暂无日志
            </div>
            <div v-else class="logs-content">
              <div
                v-for="log in logs"
                :key="log.id"
                class="log-item"
                :class="`log-${log.level}`"
              >
                <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                <span class="log-level">{{ log.level.toUpperCase() }}</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </el-scrollbar>
        </div>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="task.error" class="detail-section">
        <h3 class="section-title">错误信息</h3>
        <el-alert
          :title="task.error.message"
          type="error"
          :description="task.error.stack"
          show-icon
          :closable="false"
        />
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          v-if="task?.status === 'pending' || task?.status === 'paused'"
          type="primary"
          :icon="VideoPlay"
          @click="handleStart"
        >
          启动
        </el-button>
        <el-button
          v-if="task?.status === 'running'"
          type="warning"
          :icon="VideoPause"
          @click="handlePause"
        >
          暂停
        </el-button>
        <el-button
          v-if="task?.status === 'running' || task?.status === 'paused'"
          type="danger"
          :icon="CircleClose"
          @click="handleStop"
        >
          停止
        </el-button>
        <el-button
          :icon="Download"
          @click="handleExport"
        >
          导出结果
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  VideoPlay,
  VideoPause,
  Download,
  CircleClose
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'

interface Props {
  modelValue: boolean
  task: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'refresh'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 状态管理
const taskStore = useTaskStore()

// 响应式数据
const logs = ref<any[]>([])
const logsLoading = ref(false)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

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

// 事件处理方法
const handleClose = () => {
  visible.value = false
}

const handleStart = async () => {
  try {
    await taskStore.startTask(props.task.id)
    ElMessage.success('任务启动成功')
    emit('refresh')
  } catch (error) {
    ElMessage.error('任务启动失败')
  }
}

const handlePause = async () => {
  try {
    await taskStore.pauseTask(props.task.id)
    ElMessage.success('任务暂停成功')
    emit('refresh')
  } catch (error) {
    ElMessage.error('任务暂停失败')
  }
}

const handleStop = async () => {
  try {
    await taskStore.stopTask(props.task.id)
    ElMessage.success('任务停止成功')
    emit('refresh')
  } catch (error) {
    ElMessage.error('任务停止失败')
  }
}

const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中')
}

const refreshLogs = async () => {
  if (!props.task?.id) return
  
  logsLoading.value = true
  try {
    await taskStore.fetchTaskLogs(props.task.id, { page: 1, pageSize: 100 })
    logs.value = taskStore.taskLogs || []
  } catch (error) {
    ElMessage.error('获取日志失败')
  } finally {
    logsLoading.value = false
  }
}

// 监听任务变化，自动刷新日志
watch(
  () => props.task?.id,
  (newId) => {
    if (newId && visible.value) {
      refreshLogs()
    }
  },
  { immediate: true }
)

// 监听抽屉显示状态
watch(
  visible,
  (newVisible) => {
    if (newVisible && props.task?.id) {
      refreshLogs()
    }
  }
)
</script>

<style lang="scss" scoped>
.task-detail {
  .detail-section {
    margin-bottom: 24px;
    
    .section-title {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .description-content {
    padding: 12px;
    background: var(--el-fill-color-lighter);
    border-radius: 4px;
    line-height: 1.6;
  }
  
  .logs-container {
    border: 1px solid var(--el-border-color);
    border-radius: 4px;
    
    .empty-logs {
      padding: 40px;
      text-align: center;
      color: var(--el-text-color-placeholder);
    }
    
    .logs-content {
      .log-item {
        padding: 8px 12px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
        display: flex;
        gap: 12px;
        
        &:last-child {
          border-bottom: none;
        }
        
        .log-time {
          color: var(--el-text-color-secondary);
          min-width: 140px;
        }
        
        .log-level {
          min-width: 50px;
          font-weight: 600;
        }
        
        .log-message {
          flex: 1;
        }
        
        &.log-error {
          background: var(--el-color-error-light-9);
          
          .log-level {
            color: var(--el-color-error);
          }
        }
        
        &.log-warn {
          background: var(--el-color-warning-light-9);
          
          .log-level {
            color: var(--el-color-warning);
          }
        }
        
        &.log-info {
          .log-level {
            color: var(--el-color-info);
          }
        }
        
        &.log-debug {
          .log-level {
            color: var(--el-text-color-secondary);
          }
        }
      }
    }
  }
}

.drawer-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>