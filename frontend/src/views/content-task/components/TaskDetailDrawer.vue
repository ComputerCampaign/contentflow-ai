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
      
      <!-- 任务结果 -->
      <div class="detail-section">
        <h3 class="section-title">
          任务结果
          <el-button
            size="small"
            :icon="Refresh"
            @click="refreshResults"
            :loading="resultsLoading"
          >
            刷新
          </el-button>
        </h3>
        <div class="results-container">
          <div v-if="!taskResults" class="empty-results">
            暂无结果数据
          </div>
          <div v-else>
            <!-- 爬虫任务结果 -->
            <div v-if="task.type === 'crawler'" class="crawler-results">
              <el-row :gutter="16" class="result-stats">
                <el-col :span="6">
                  <el-statistic title="处理项数" :value="taskResults?.execution_stats?.items_processed || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="成功项数" :value="taskResults?.execution_stats?.items_success || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="失败项数" :value="taskResults?.execution_stats?.items_failed || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="执行时长" :value="taskResults?.execution_stats?.duration || 0" suffix="秒" />
                </el-col>
              </el-row>
              
              <div v-if="taskResults.results && taskResults.results.length > 0" class="crawler-data">
                <h4>抓取结果</h4>
                <el-table :data="taskResults.results" stripe max-height="400">
                  <el-table-column prop="url" label="URL" width="300" show-overflow-tooltip />
                  <el-table-column prop="title" label="标题" show-overflow-tooltip />
                  <el-table-column prop="content" label="内容" show-overflow-tooltip>
                    <template #default="{ row }">
                      <span>{{ row.content ? row.content.substring(0, 100) + '...' : '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="extracted_data" label="提取数据" width="200">
                    <template #default="{ row }">
                      <el-tag v-if="row.extracted_data" size="small">有数据</el-tag>
                      <span v-else>-</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
            
            <!-- 内容生成任务结果 -->
            <div v-else-if="task.type === 'content_generation'" class="content-results">
              <el-row :gutter="16" class="result-stats">
                <el-col :span="6">
                  <el-statistic title="处理项数" :value="taskResults?.execution_stats?.items_processed || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="成功项数" :value="taskResults?.execution_stats?.items_success || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="失败项数" :value="taskResults?.execution_stats?.items_failed || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="执行时长" :value="taskResults?.execution_stats?.duration || 0" suffix="秒" />
                </el-col>
              </el-row>
              
              <div v-if="taskResults.results && taskResults.results.length > 0" class="content-data">
                <h4>生成内容</h4>
                <div class="content-list">
                  <div v-for="(result, index) in taskResults.results" :key="index" class="content-item">
                    <div class="content-header">
                      <span class="content-index">#{{ index + 1 }}</span>
                      <el-tag size="small" type="success">已生成</el-tag>
                    </div>
                    <div class="content-body">
                      {{ result.content || result.generated_content || '内容为空' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 组合任务结果 -->
            <div v-else-if="task.type === 'combined'" class="combined-results">
              <el-row :gutter="16" class="result-stats">
                <el-col :span="6">
                  <el-statistic title="处理项数" :value="taskResults?.execution_stats?.items_processed || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="成功项数" :value="taskResults?.execution_stats?.items_success || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="失败项数" :value="taskResults?.execution_stats?.items_failed || 0" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="执行时长" :value="taskResults?.execution_stats?.duration || 0" suffix="秒" />
                </el-col>
              </el-row>
              
              <div class="combined-data">
                <h4>执行结果</h4>
                <el-alert
                  title="组合任务包含多个子任务，请查看各子任务的详细结果"
                  type="info"
                  :closable="false"
                />
              </div>
            </div>
          </div>
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
          type="info"
          @click="handleGenerateCommand"
          :loading="commandLoading"
        >
          生成Shell命令
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

  <!-- 命令显示对话框 -->
  <el-dialog
    v-model="commandDialogVisible"
    title="任务执行命令"
    width="60%"
    :before-close="() => commandDialogVisible = false"
  >
    <div class="command-container">
      <el-input
        v-model="generatedCommand"
        type="textarea"
        :rows="6"
        readonly
        placeholder="生成的命令将显示在这里..."
        class="command-input"
      />
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="commandDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="copyCommand">
          <el-icon><DocumentCopy /></el-icon>
          复制命令
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  VideoPlay,
  VideoPause,
  Download,
  CircleClose,
  Monitor,
  DocumentCopy
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import taskApi from '@/api/task'

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
const taskResults = ref<any>(null)
const resultsLoading = ref(false)
const commandLoading = ref(false)
const commandDialogVisible = ref(false)
const generatedCommand = ref('')

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

// 生成Shell命令
const handleGenerateCommand = async () => {
  if (!props.task) return
  
  try {
    commandLoading.value = true
    const response = await taskApi.getTaskCommand(props.task.id)
    if (response.success) {
      generatedCommand.value = response.data.command
      commandDialogVisible.value = true
    } else {
      ElMessage.error(response.message || '获取命令失败')
    }
  } catch (error) {
    console.error('获取任务命令失败:', error)
    ElMessage.error('获取命令失败，请稍后重试')
  } finally {
    commandLoading.value = false
  }
}

// 复制命令到剪贴板
const copyCommand = async () => {
  try {
    await navigator.clipboard.writeText(generatedCommand.value)
    ElMessage.success('命令已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

const refreshResults = async () => {
  if (!props.task?.id) return
  
  console.log('开始获取任务结果，任务ID:', props.task.id)
  resultsLoading.value = true
  try {
    await taskStore.fetchTaskResults(props.task.id, { page: 1, pageSize: 100 })
    taskResults.value = taskStore.taskResults || null
    
    // 添加调试信息
    console.log('获取到的taskResults:', taskResults.value)
    console.log('任务类型:', taskResults.value?.task_type)
    console.log('是否有结果:', !!taskResults.value?.results)
    console.log('结果数量:', taskResults.value?.results?.length || 0)
    console.log('是否有执行统计:', !!taskResults.value?.execution_stats)
    console.log('执行统计:', taskResults.value?.execution_stats)
  } catch (error) {
    console.error('获取任务结果失败:', error)
    ElMessage.error('获取结果失败')
  } finally {
    resultsLoading.value = false
  }
}

// 监听任务变化，自动刷新结果
watch(
  () => props.task?.id,
  (newId) => {
    if (newId && visible.value) {
      refreshResults()
    }
  },
  { immediate: true }
)

// 监听抽屉显示状态
watch(
  visible,
  (newVisible) => {
    if (newVisible && props.task?.id) {
      refreshResults()
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
  
  .results-container {
    .empty-results {
      padding: 40px;
      text-align: center;
      color: var(--el-text-color-placeholder);
    }
    
    .result-stats {
      margin-bottom: 24px;
    }
    
    .crawler-results {
      .crawler-data {
        margin-top: 16px;
        
        h4 {
          margin: 0 0 12px 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }
    }
    
    .content-results {
      .content-data {
        margin-top: 16px;
        
        h4 {
          margin: 0 0 12px 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
        
        .content-list {
          .content-item {
            margin-bottom: 16px;
            padding: 16px;
            border: 1px solid var(--el-border-color);
            border-radius: 8px;
            background: var(--el-fill-color-lighter);
            
            .content-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 12px;
              
              .content-index {
                font-weight: 600;
                color: var(--el-text-color-primary);
              }
            }
            
            .content-body {
              line-height: 1.6;
              color: var(--el-text-color-regular);
              white-space: pre-wrap;
              word-break: break-word;
            }
          }
        }
      }
    }
    
    .combined-results {
      .combined-data {
        margin-top: 16px;
        
        h4 {
          margin: 0 0 12px 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--el-text-color-primary);
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

.command-container {
  margin: 16px 0;
}

.command-input {
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>