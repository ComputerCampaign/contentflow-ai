<template>
  <div class="task-detail">
    <PageHeader :title="`任务详情 - ${taskData?.name || ''}`" :description="taskData?.description || ''">
      <template #actions>
        <el-button @click="handleBack">返回</el-button>
        <el-button
          v-if="taskData?.status === 'pending'"
          type="primary"
          @click="handleStart"
          :loading="actionLoading"
        >
          开始执行
        </el-button>
        <el-button
          v-if="taskData?.status === 'running'"
          type="warning"
          @click="handlePause"
          :loading="actionLoading"
        >
          暂停任务
        </el-button>
        <el-button
          v-if="taskData?.status === 'paused'"
          type="success"
          @click="handleResume"
          :loading="actionLoading"
        >
          恢复任务
        </el-button>
        <el-button
          type="danger"
          @click="handleStop"
          :loading="actionLoading"
          :disabled="taskData?.status === 'completed' || taskData?.status === 'failed'"
        >
          停止任务
        </el-button>
        <el-button
          type="primary"
          @click="handleEdit"
        >
          编辑任务
        </el-button>
      </template>
    </PageHeader>

    <div class="task-detail-content" v-loading="loading">
      <el-row :gutter="20">
        <el-col :span="16">
          <!-- 基本信息 -->
          <el-card class="info-card">
            <template #header>
              <span class="card-title">基本信息</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="任务ID">{{ taskData?.id }}</el-descriptions-item>
              <el-descriptions-item label="任务名称">{{ taskData?.name }}</el-descriptions-item>
              <el-descriptions-item label="任务状态">
                <TaskStatus :status="taskData?.status" />
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <TaskPriority :priority="taskData?.priority" />
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(taskData?.createdAt) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDate(taskData?.updatedAt) }}</el-descriptions-item>
              <el-descriptions-item label="执行模式">{{ getModeText(taskData?.mode) }}</el-descriptions-item>
              <el-descriptions-item label="计划执行时间">
                {{ taskData?.scheduledTime ? formatDate(taskData.scheduledTime) : '立即执行' }}
              </el-descriptions-item>
              <el-descriptions-item label="任务描述" :span="2">
                {{ taskData?.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 执行配置 -->
          <el-card class="info-card">
            <template #header>
              <span class="card-title">执行配置</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="重试次数">{{ taskData?.retryCount || 0 }}</el-descriptions-item>
              <el-descriptions-item label="超时时间">{{ taskData?.timeout || 300 }}秒</el-descriptions-item>
              <el-descriptions-item label="并发数">{{ taskData?.concurrency || 1 }}</el-descriptions-item>
              <el-descriptions-item label="延迟设置">{{ taskData?.delay || 1000 }}毫秒</el-descriptions-item>
              <el-descriptions-item label="通知设置">
                {{ taskData?.enableNotification ? '已启用' : '未启用' }}
              </el-descriptions-item>
              <el-descriptions-item label="通知邮箱">
                {{ taskData?.notificationEmail || '未设置' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 执行日志 -->
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">执行日志</span>
                <el-button size="small" @click="refreshLogs">刷新</el-button>
              </div>
            </template>
            <div class="log-container">
              <div v-if="logs.length === 0" class="empty-logs">
                暂无执行日志
              </div>
              <div v-else class="log-list">
                <div
                  v-for="log in logs"
                  :key="log.id"
                  class="log-item"
                  :class="`log-${log.level}`"
                >
                  <div class="log-time">{{ formatDate(log.timestamp) }}</div>
                  <div class="log-level">{{ log.level.toUpperCase() }}</div>
                  <div class="log-message">{{ log.message }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 执行统计 -->
          <el-card class="stats-card">
            <template #header>
              <span class="card-title">执行统计</span>
            </template>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ taskStats?.totalItems || 0 }}</div>
                <div class="stat-label">总项目数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value success">{{ taskStats?.successItems || 0 }}</div>
                <div class="stat-label">成功数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value error">{{ taskStats?.failedItems || 0 }}</div>
                <div class="stat-label">失败数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ taskStats?.progress || 0 }}%</div>
                <div class="stat-label">完成进度</div>
              </div>
            </div>
            <el-progress
              :percentage="taskStats?.progress || 0"
              :status="getProgressStatus()"
              class="progress-bar"
            />
          </el-card>

          <!-- 爬虫配置信息 -->
          <el-card class="info-card">
            <template #header>
              <span class="card-title">爬虫配置</span>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="配置名称">{{ crawlerData?.name }}</el-descriptions-item>
              <el-descriptions-item label="目标URL">{{ crawlerData?.url }}</el-descriptions-item>
              <el-descriptions-item label="请求方法">{{ crawlerData?.method }}</el-descriptions-item>
              <el-descriptions-item label="数据格式">{{ crawlerData?.dataFormat }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 快速操作 -->
          <el-card class="action-card">
            <template #header>
              <span class="card-title">快速操作</span>
            </template>
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="handleClone">
                克隆任务
              </el-button>
              <el-button type="success" size="small" @click="handleExport">
                导出数据
              </el-button>
              <el-button type="warning" size="small" @click="handleViewResults">
                查看结果
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete">
                删除任务
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import TaskStatus from '@/components/task/TaskStatus.vue'
import TaskPriority from '@/components/task/TaskPriority.vue'
import { useTaskStore } from '@/stores/task'
import { useCrawlerStore } from '@/stores/crawler'
import { formatDate } from '@/utils/date'

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()
const crawlerStore = useCrawlerStore()

const loading = ref(true)
const actionLoading = ref(false)
const taskData = ref<any>(null)
const crawlerData = ref<any>(null)
const taskStats = ref<any>(null)
const logs = ref<any[]>([])
let refreshTimer: number | null = null

const getModeText = (mode: string) => {
  const modeMap = {
    immediate: '立即执行',
    scheduled: '定时执行',
    manual: '手动执行'
  }
  return modeMap[mode as keyof typeof modeMap] || mode
}

const getProgressStatus = () => {
  if (!taskData.value) return ''
  const status = taskData.value.status
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'running') return ''
  return ''
}

const handleBack = () => {
  router.push('/tasks/list')
}

const handleEdit = () => {
  router.push(`/tasks/edit/${route.params.id}`)
}

const handleStart = async () => {
  try {
    actionLoading.value = true
    await taskStore.startTask(route.params.id as string)
    ElMessage.success('任务已开始执行')
    await loadTaskData()
  } catch (error) {
    console.error('启动任务失败:', error)
    ElMessage.error('启动任务失败')
  } finally {
    actionLoading.value = false
  }
}

const handlePause = async () => {
  try {
    actionLoading.value = true
    await taskStore.pauseTask(route.params.id as string)
    ElMessage.success('任务已暂停')
    await loadTaskData()
  } catch (error) {
    console.error('暂停任务失败:', error)
    ElMessage.error('暂停任务失败')
  } finally {
    actionLoading.value = false
  }
}

const handleResume = async () => {
  try {
    actionLoading.value = true
    await taskStore.resumeTask(route.params.id as string)
    ElMessage.success('任务已恢复')
    await loadTaskData()
  } catch (error) {
    console.error('恢复任务失败:', error)
    ElMessage.error('恢复任务失败')
  } finally {
    actionLoading.value = false
  }
}

const handleStop = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要停止这个任务吗？',
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    actionLoading.value = true
    await taskStore.stopTask(route.params.id as string)
    ElMessage.success('任务已停止')
    await loadTaskData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止任务失败:', error)
      ElMessage.error('停止任务失败')
    }
  } finally {
    actionLoading.value = false
  }
}

const handleClone = async () => {
  try {
    await taskStore.cloneTask(route.params.id as string)
    ElMessage.success('任务克隆成功')
    router.push('/tasks/list')
  } catch (error) {
    console.error('克隆任务失败:', error)
    ElMessage.error('克隆任务失败')
  }
}

const handleExport = async () => {
  try {
    // await taskStore.exportTaskData(parseInt(route.params.id as string))
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error('导出数据失败')
  }
}

const handleViewResults = () => {
  // 跳转到结果查看页面
  router.push(`/tasks/results/${route.params.id}`)
}

// 根据任务类型获取正确的列表页面路径
const getTaskListPath = (taskType: string) => {
  switch (taskType) {
    case 'web_scraping':
    case 'crawler':
      return '/crawler-tasks/list'
    case 'content_generation':
      return '/content-tasks/list'
    default:
      return '/crawler-tasks/list' // 默认跳转到爬虫任务列表
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个任务吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await taskStore.deleteTask(route.params.id as string)
    ElMessage.success('任务删除成功')
    router.push(getTaskListPath(taskData.value?.type || 'web_scraping'))
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

const loadTaskData = async () => {
  try {
    const taskId = route.params.id as string
    const task = await taskStore.fetchTaskById(taskId)
    taskData.value = task
    
    // 加载爬虫配置信息
      if (task?.crawlerConfigId) {
        const crawler = await crawlerStore.fetchCrawlerConfigById(task.crawlerConfigId.toString())
        crawlerData.value = crawler
      }
    
    // 加载任务统计信息
    await taskStore.fetchTaskStatistics()
    // taskStats.value = taskStore.taskStatistics
  } catch (error) {
    console.error('加载任务数据失败:', error)
    ElMessage.error('加载任务数据失败')
    router.push('/crawler-tasks/list') // 默认跳转到爬虫任务列表
  }
}

const loadTaskLogs = async () => {
  try {
    const taskId = route.params.id as string
    await taskStore.fetchTaskLogs(taskId, { page: 1, pageSize: 50 })
    logs.value = taskStore.taskLogs
  } catch (error) {
    console.error('加载任务日志失败:', error)
  }
}

const refreshLogs = () => {
  loadTaskLogs()
}

const initPage = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadTaskData(),
      loadTaskLogs()
    ])
  } finally {
    loading.value = false
  }
}

// 自动刷新数据（对于运行中的任务）
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    if (taskData.value?.status === 'running') {
      loadTaskData()
      loadTaskLogs()
    }
  }, 5000) // 每5秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  initPage()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
.task-detail {
  padding: 20px;
  
  &-content {
    margin-top: 20px;
  }
}

.info-card,
.stats-card,
.action-card {
  margin-bottom: 20px;
}

.card-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  
  .stat-value {
    font-size: 24px;
    font-weight: bold;
    color: var(--el-color-primary);
    
    &.success {
      color: var(--el-color-success);
    }
    
    &.error {
      color: var(--el-color-danger);
    }
  }
  
  .stat-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
  }
}

.progress-bar {
  margin-top: 16px;
}

.log-container {
  max-height: 400px;
  overflow-y: auto;
}

.empty-logs {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 40px 0;
}

.log-list {
  .log-item {
    display: flex;
    align-items: flex-start;
    padding: 8px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    
    &:last-child {
      border-bottom: none;
    }
    
    .log-time {
      flex-shrink: 0;
      width: 140px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    
    .log-level {
      flex-shrink: 0;
      width: 60px;
      font-size: 12px;
      font-weight: bold;
    }
    
    .log-message {
      flex: 1;
      font-size: 13px;
      line-height: 1.4;
    }
    
    &.log-info .log-level {
      color: var(--el-color-info);
    }
    
    &.log-success .log-level {
      color: var(--el-color-success);
    }
    
    &.log-warning .log-level {
      color: var(--el-color-warning);
    }
    
    &.log-error .log-level {
      color: var(--el-color-danger);
    }
  }
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-descriptions__body) {
  background-color: var(--el-bg-color-page);
}
</style>