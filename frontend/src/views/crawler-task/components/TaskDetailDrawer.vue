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
      
      <!-- 爬虫结果 -->
      <div class="detail-section">
        <h3 class="section-title">
          爬虫结果
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
          <div v-else class="crawler-results">
            <!-- 统计信息 -->
            <el-row :gutter="16" class="result-stats">
              <el-col :span="6">
                <el-statistic title="处理项数" :value="taskResults.items_processed || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="成功项数" :value="taskResults.items_success || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="失败项数" :value="taskResults.items_failed || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="执行状态" :value="taskResults.status || '未知'" />
              </el-col>
            </el-row>
            
            <!-- 爬虫结果列表 -->
            <div v-if="taskResults.crawler_results && taskResults.crawler_results.length > 0" class="crawler-data">
              <h4>抓取结果 ({{ taskResults.crawler_results.length }} 条)</h4>
              
              <div v-for="(result, index) in taskResults.crawler_results" :key="result.id" class="result-item">
                <el-card class="result-card" shadow="hover">
                  <template #header>
                    <div class="result-header">
                      <span class="result-index">#{{ index + 1 }}</span>
                      <el-tag size="small" type="success">已抓取</el-tag>
                    </div>
                  </template>
                  
                  <!-- 基本信息 -->
                  <div class="result-basic">
                    <div class="result-title">{{ result.title || '无标题' }}</div>
                    <div class="result-url">
                      <el-link :href="result.url" target="_blank" type="primary">
                        {{ result.url }}
                      </el-link>
                    </div>
                    <div class="result-time">
                      创建时间: {{ formatTime(result.created_at) }}
                    </div>
                  </div>
                  
                  <!-- 提取数据 -->
                  <div v-if="result.extracted_data" class="extracted-data">
                    <el-collapse>
                      <el-collapse-item title="提取数据详情" name="extracted">
                        <!-- 评论 -->
                        <div v-if="result.extracted_data.comments && result.extracted_data.comments.length > 0" class="data-section">
                          <h5>评论 ({{ result.extracted_data.comments_count || result.extracted_data.comments.length }})</h5>
                          <div class="comments-list">
                            <div v-for="(comment, idx) in result.extracted_data.comments.slice(0, 5)" :key="idx" class="comment-item">
                              <div class="comment-text">{{ comment.text }}</div>
                              <div v-if="comment.children && comment.children.length > 0" class="comment-children">
                                <div v-for="(child, cidx) in comment.children" :key="cidx" class="child-comment">
                                  {{ child.text }}
                                </div>
                              </div>
                            </div>
                            <div v-if="result.extracted_data.comments.length > 5" class="more-comments">
                              还有 {{ result.extracted_data.comments.length - 5 }} 条评论...
                            </div>
                          </div>
                        </div>
                        
                        <!-- 图片 -->
                        <div v-if="result.extracted_data.images && result.extracted_data.images.length > 0" class="data-section">
                          <h5>图片 ({{ result.extracted_data.images.length }})</h5>
                          <div class="images-list">
                            <div v-for="(image, idx) in result.extracted_data.images" :key="idx" class="image-item">
                              <el-image
                                :src="image.url"
                                :alt="image.alt"
                                fit="cover"
                                style="width: 100px; height: 100px;"
                                :preview-src-list="[image.url]"
                              />
                              <div class="image-info">
                                <div>{{ image.alt || '无描述' }}</div>
                                <div class="image-size">{{ image.width }}x{{ image.height }}</div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <!-- 链接 -->
                        <div v-if="result.extracted_data.links && result.extracted_data.links.length > 0" class="data-section">
                          <h5>链接 ({{ result.extracted_data.links.length }})</h5>
                          <div class="links-list">
                            <div v-for="(link, idx) in result.extracted_data.links" :key="idx" class="link-item">
                              <el-link :href="link.url" target="_blank" type="primary">
                                {{ link.text || link.url }}
                              </el-link>
                            </div>
                          </div>
                        </div>
                        
                        <!-- 文本 -->
                        <div v-if="result.extracted_data.texts && result.extracted_data.texts.length > 0" class="data-section">
                          <h5>文本内容 ({{ result.extracted_data.texts.length }})</h5>
                          <div class="texts-list">
                            <div v-for="(text, idx) in result.extracted_data.texts" :key="idx" class="text-item">
                              {{ text }}
                            </div>
                          </div>
                        </div>
                        
                        <!-- 使用的规则 -->
                        <div v-if="result.extracted_data.xpath_rules_used && result.extracted_data.xpath_rules_used.length > 0" class="data-section">
                          <h5>使用的提取规则</h5>
                          <div class="rules-list">
                            <el-tag v-for="rule in result.extracted_data.xpath_rules_used" :key="rule" size="small" class="rule-tag">
                              {{ rule }}
                            </el-tag>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                  
                  <!-- 页面元数据 -->
                  <div v-if="result.page_metadata" class="page-metadata">
                    <el-descriptions :column="2" size="small">
                      <el-descriptions-item label="任务名称">
                        {{ result.page_metadata.task_name || '-' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="抓取时间">
                        {{ result.page_metadata.crawl_time ? new Date(result.page_metadata.crawl_time * 1000).toLocaleString() : '-' }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-card>
              </div>
            </div>
            
            <div v-else class="no-results">
              <el-empty description="暂无抓取结果" />
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
  if (!props.task?.id) {
    console.warn('⚠️ 任务ID不存在，无法获取结果')
    return
  }
  
  resultsLoading.value = true
  try {
    await taskStore.fetchTaskResults(props.task.id)
    taskResults.value = taskStore.taskResults || null
    
    console.log('📊 获取爬虫结果成功:', {
      hasData: !!taskResults.value,
      crawlerResultsCount: taskResults.value?.crawler_results?.length || 0,
      status: taskResults.value?.status,
      itemsProcessed: taskResults.value?.items_processed
    })
    
  } catch (error) {
    console.error('❌ [TaskDetailDrawer] 刷新任务结果失败:', error)
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
        
        .result-item {
          margin-bottom: 16px;
          
          .result-card {
            .result-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              
              .result-index {
                font-weight: 600;
                color: var(--el-text-color-primary);
              }
            }
            
            .result-basic {
              margin-bottom: 16px;
              
              .result-title {
                font-size: 16px;
                font-weight: 600;
                color: var(--el-text-color-primary);
                margin-bottom: 8px;
              }
              
              .result-url {
                margin-bottom: 8px;
              }
              
              .result-time {
                font-size: 12px;
                color: var(--el-text-color-secondary);
              }
            }
            
            .extracted-data {
              .data-section {
                margin-bottom: 16px;
                
                h5 {
                  margin: 0 0 8px 0;
                  font-size: 14px;
                  font-weight: 600;
                  color: var(--el-text-color-primary);
                }
                
                .comments-list {
                  .comment-item {
                    margin-bottom: 8px;
                    padding: 8px;
                    background: var(--el-fill-color-lighter);
                    border-radius: 4px;
                    
                    .comment-text {
                      font-size: 14px;
                      color: var(--el-text-color-regular);
                      margin-bottom: 4px;
                    }
                    
                    .comment-children {
                      margin-left: 16px;
                      margin-top: 8px;
                      
                      .child-comment {
                        padding: 4px 8px;
                        background: var(--el-fill-color);
                        border-radius: 4px;
                        margin-bottom: 4px;
                        font-size: 13px;
                        color: var(--el-text-color-regular);
                      }
                    }
                  }
                  
                  .more-comments {
                    font-size: 12px;
                    color: var(--el-text-color-secondary);
                    text-align: center;
                    padding: 8px;
                  }
                }
                
                .images-list {
                  display: grid;
                  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                  gap: 12px;
                  
                  .image-item {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    
                    .image-info {
                      margin-top: 8px;
                      text-align: center;
                      font-size: 12px;
                      color: var(--el-text-color-secondary);
                      
                      .image-size {
                        color: var(--el-text-color-placeholder);
                      }
                    }
                  }
                }
                
                .links-list {
                  .link-item {
                    margin-bottom: 4px;
                  }
                }
                
                .texts-list {
                  .text-item {
                    margin-bottom: 8px;
                    padding: 8px;
                    background: var(--el-fill-color-lighter);
                    border-radius: 4px;
                    font-size: 14px;
                    color: var(--el-text-color-regular);
                    line-height: 1.5;
                  }
                }
                
                .rules-list {
                  .rule-tag {
                    margin-right: 8px;
                    margin-bottom: 4px;
                  }
                }
              }
            }
          }
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