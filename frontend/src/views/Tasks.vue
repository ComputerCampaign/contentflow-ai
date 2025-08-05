<template>
  <div class="tasks-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>任务管理</h1>
        <p>管理和监控所有爬虫任务</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <i class="fas fa-plus"></i>
          创建任务
        </el-button>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索任务名称或描述"
          prefix-icon="Search"
          style="width: 300px"
          clearable
        />
        <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px">
          <el-option label="全部" value=""></el-option>
          <el-option label="运行中" value="running"></el-option>
          <el-option label="已完成" value="completed"></el-option>
          <el-option label="已暂停" value="paused"></el-option>
          <el-option label="失败" value="failed"></el-option>
        </el-select>
        <el-select v-model="typeFilter" placeholder="类型筛选" style="width: 120px">
          <el-option label="全部" value=""></el-option>
          <el-option label="新闻采集" value="news"></el-option>
          <el-option label="博客采集" value="blog"></el-option>
          <el-option label="论坛采集" value="forum"></el-option>
          <el-option label="电商采集" value="ecommerce"></el-option>
        </el-select>
      </div>
      <div class="filter-right">
        <el-button @click="refreshTasks">
          <i class="fas fa-sync-alt"></i>
          刷新
        </el-button>
        <el-button @click="exportTasks">
          <i class="fas fa-download"></i>
          导出
        </el-button>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="tasks-container">
      <div class="tasks-grid">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-card"
          :class="task.status"
        >
          <div class="task-header">
            <div class="task-info">
              <h3 class="task-name">{{ task.name }}</h3>
              <div class="task-meta">
                <span class="task-type">
                  <i :class="getTypeIcon(task.type)"></i>
                  {{ getTypeText(task.type) }}
                </span>
                <span class="task-created">{{ formatTime(task.createdAt) }}</span>
              </div>
            </div>
            <div class="task-actions">
              <el-dropdown @command="handleTaskAction">
                <el-button type="text" class="action-btn">
                  <i class="fas fa-ellipsis-v"></i>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{ action: 'view', task }">
                      <i class="fas fa-eye"></i> 查看详情
                    </el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'edit', task }">
                      <i class="fas fa-edit"></i> 编辑
                    </el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'clone', task }">
                      <i class="fas fa-copy"></i> 克隆
                    </el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'delete', task }" divided>
                      <i class="fas fa-trash"></i> 删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <div class="task-description">
            {{ task.description }}
          </div>

          <div class="task-progress">
            <div class="progress-info">
              <span>进度</span>
              <span>{{ task.progress }}%</span>
            </div>
            <el-progress
              :percentage="task.progress"
              :color="getProgressColor(task.status)"
              :show-text="false"
              :stroke-width="6"
            />
          </div>

          <div class="task-stats">
            <div class="stat-item">
              <span class="stat-label">已采集</span>
              <span class="stat-value">{{ task.collected }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成功率</span>
              <span class="stat-value">{{ task.successRate }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">耗时</span>
              <span class="stat-value">{{ formatDuration(task.duration) }}</span>
            </div>
          </div>

          <div class="task-footer">
            <div class="task-status">
              <span class="status-badge" :class="task.status">
                <i :class="getStatusIcon(task.status)"></i>
                {{ getStatusText(task.status) }}
              </span>
            </div>
            <div class="task-controls">
              <el-button
                v-if="task.status === 'paused'"
                type="success"
                size="small"
                @click="resumeTask(task)"
              >
                <i class="fas fa-play"></i>
                继续
              </el-button>
              <el-button
                v-else-if="task.status === 'running'"
                type="warning"
                size="small"
                @click="pauseTask(task)"
              >
                <i class="fas fa-pause"></i>
                暂停
              </el-button>
              <el-button
                v-else-if="task.status === 'failed'"
                type="primary"
                size="small"
                @click="retryTask(task)"
              >
                <i class="fas fa-redo"></i>
                重试
              </el-button>
              <el-button
                size="small"
                @click="viewTaskLogs(task)"
              >
                <i class="fas fa-list-alt"></i>
                日志
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredTasks.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-tasks"></i>
        </div>
        <h3>暂无任务</h3>
        <p>点击上方按钮创建您的第一个爬虫任务</p>
        <el-button type="primary" @click="showCreateDialog = true">
          创建任务
        </el-button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="filteredTasks.length > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="totalTasks"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新任务"
      width="600px"
      :before-close="handleCreateDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="createForm.type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="新闻采集" value="news">
              <i class="fas fa-newspaper"></i> 新闻采集
            </el-option>
            <el-option label="博客采集" value="blog">
              <i class="fas fa-blog"></i> 博客采集
            </el-option>
            <el-option label="论坛采集" value="forum">
              <i class="fas fa-comments"></i> 论坛采集
            </el-option>
            <el-option label="电商采集" value="ecommerce">
              <i class="fas fa-shopping-cart"></i> 电商采集
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="目标网站" prop="targetUrl">
          <el-input v-model="createForm.targetUrl" placeholder="请输入目标网站URL" />
        </el-form-item>
        <el-form-item label="采集频率" prop="frequency">
          <el-select v-model="createForm.frequency" placeholder="请选择采集频率" style="width: 100%">
            <el-option label="每小时" value="hourly"></el-option>
            <el-option label="每天" value="daily"></el-option>
            <el-option label="每周" value="weekly"></el-option>
            <el-option label="手动执行" value="manual"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createTask" :loading="creating">
            创建任务
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="800px"
    >
      <div v-if="selectedTask" class="task-detail">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <label>任务名称:</label>
              <span>{{ selectedTask.name }}</span>
            </div>
            <div class="detail-item">
              <label>任务类型:</label>
              <span>{{ getTypeText(selectedTask.type) }}</span>
            </div>
            <div class="detail-item">
              <label>目标网站:</label>
              <span>{{ selectedTask.targetUrl }}</span>
            </div>
            <div class="detail-item">
              <label>创建时间:</label>
              <span>{{ formatTime(selectedTask.createdAt) }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>执行统计</h4>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-value">{{ selectedTask.collected }}</div>
              <div class="stat-label">已采集</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ selectedTask.successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ formatDuration(selectedTask.duration) }}</div>
              <div class="stat-label">总耗时</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ selectedTask.progress }}%</div>
              <div class="stat-label">完成进度</div>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>最近日志</h4>
          <div class="log-list">
            <div
              v-for="log in selectedTask.logs"
              :key="log.id"
              class="log-item"
              :class="log.level"
            >
              <span class="log-time">{{ formatTime(log.time) }}</span>
              <span class="log-level">{{ log.level.toUpperCase() }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// 响应式数据
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const creating = ref(false)
const selectedTask = ref(null)

// 表单数据
const createForm = ref({
  name: '',
  type: '',
  targetUrl: '',
  frequency: '',
  description: ''
})

const createFormRef = ref(null)

// 表单验证规则
const createRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  targetUrl: [
    { required: true, message: '请输入目标网站URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  frequency: [
    { required: true, message: '请选择采集频率', trigger: 'change' }
  ]
}

// 模拟任务数据
const tasks = ref([
  {
    id: 1,
    name: '技术博客采集',
    type: 'blog',
    description: '采集知名技术博客的最新文章',
    targetUrl: 'https://example-blog.com',
    status: 'running',
    progress: 75,
    collected: 156,
    successRate: 95,
    duration: 3600000,
    createdAt: new Date(Date.now() - 86400000),
    logs: [
      { id: 1, time: new Date(), level: 'info', message: '开始采集新文章' },
      { id: 2, time: new Date(Date.now() - 300000), level: 'success', message: '成功采集文章: Vue 3 最佳实践' },
      { id: 3, time: new Date(Date.now() - 600000), level: 'warning', message: '检测到反爬虫机制，正在调整策略' }
    ]
  },
  {
    id: 2,
    name: '新闻资讯采集',
    type: 'news',
    description: '采集主流新闻网站的科技资讯',
    targetUrl: 'https://example-news.com',
    status: 'completed',
    progress: 100,
    collected: 89,
    successRate: 92,
    duration: 2400000,
    createdAt: new Date(Date.now() - 172800000),
    logs: [
      { id: 1, time: new Date(Date.now() - 3600000), level: 'success', message: '任务执行完成' },
      { id: 2, time: new Date(Date.now() - 7200000), level: 'info', message: '正在处理最后一批数据' }
    ]
  },
  {
    id: 3,
    name: '论坛讨论采集',
    type: 'forum',
    description: '采集技术论坛的热门讨论话题',
    targetUrl: 'https://example-forum.com',
    status: 'paused',
    progress: 45,
    collected: 234,
    successRate: 88,
    duration: 1800000,
    createdAt: new Date(Date.now() - 259200000),
    logs: [
      { id: 1, time: new Date(Date.now() - 1800000), level: 'warning', message: '任务已暂停' },
      { id: 2, time: new Date(Date.now() - 3600000), level: 'info', message: '检测到目标网站维护' }
    ]
  },
  {
    id: 4,
    name: '电商产品采集',
    type: 'ecommerce',
    description: '采集电商平台的产品信息和价格',
    targetUrl: 'https://example-shop.com',
    status: 'failed',
    progress: 20,
    collected: 45,
    successRate: 65,
    duration: 900000,
    createdAt: new Date(Date.now() - 345600000),
    logs: [
      { id: 1, time: new Date(Date.now() - 900000), level: 'error', message: '连接超时，任务失败' },
      { id: 2, time: new Date(Date.now() - 1800000), level: 'warning', message: '网络连接不稳定' }
    ]
  }
])

// 计算属性
const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  if (searchQuery.value) {
    filtered = filtered.filter(task => 
      task.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(task => task.status === statusFilter.value)
  }
  
  if (typeFilter.value) {
    filtered = filtered.filter(task => task.type === typeFilter.value)
  }
  
  return filtered
})

const totalTasks = computed(() => filteredTasks.value.length)

// 方法
const getTypeIcon = (type) => {
  const icons = {
    news: 'fas fa-newspaper',
    blog: 'fas fa-blog',
    forum: 'fas fa-comments',
    ecommerce: 'fas fa-shopping-cart'
  }
  return icons[type] || 'fas fa-globe'
}

const getTypeText = (type) => {
  const texts = {
    news: '新闻采集',
    blog: '博客采集',
    forum: '论坛采集',
    ecommerce: '电商采集'
  }
  return texts[type] || '未知类型'
}

const getStatusIcon = (status) => {
  const icons = {
    running: 'fas fa-play',
    completed: 'fas fa-check',
    paused: 'fas fa-pause',
    failed: 'fas fa-times'
  }
  return icons[status] || 'fas fa-question'
}

const getStatusText = (status) => {
  const texts = {
    running: '运行中',
    completed: '已完成',
    paused: '已暂停',
    failed: '失败'
  }
  return texts[status] || '未知状态'
}

const getProgressColor = (status) => {
  const colors = {
    running: '#409eff',
    completed: '#67c23a',
    paused: '#e6a23c',
    failed: '#f56c6c'
  }
  return colors[status] || '#909399'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const formatDuration = (duration) => {
  const hours = Math.floor(duration / 3600000)
  const minutes = Math.floor((duration % 3600000) / 60000)
  return `${hours}h ${minutes}m`
}

const refreshTasks = () => {
  ElMessage.success('任务列表已刷新')
  // 这里可以添加实际的刷新逻辑
}

const exportTasks = () => {
  ElMessage.success('任务数据导出中...')
  // 这里可以添加实际的导出逻辑
}

const handleTaskAction = ({ action, task }) => {
  switch (action) {
    case 'view':
      selectedTask.value = task
      showDetailDialog.value = true
      break
    case 'edit':
      ElMessage.info(`编辑任务: ${task.name}`)
      break
    case 'clone':
      ElMessage.info(`克隆任务: ${task.name}`)
      break
    case 'delete':
      handleDeleteTask(task)
      break
  }
}

const handleDeleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index > -1) {
      tasks.value.splice(index, 1)
      ElMessage.success('任务删除成功')
    }
  } catch (error) {
    // 用户取消删除
  }
}

const resumeTask = (task) => {
  task.status = 'running'
  ElMessage.success(`任务 "${task.name}" 已恢复运行`)
}

const pauseTask = (task) => {
  task.status = 'paused'
  ElMessage.success(`任务 "${task.name}" 已暂停`)
}

const retryTask = (task) => {
  task.status = 'running'
  task.progress = 0
  ElMessage.success(`任务 "${task.name}" 已重新开始`)
}

const viewTaskLogs = (task) => {
  selectedTask.value = task
  showDetailDialog.value = true
}

const createTask = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    // 模拟创建任务
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newTask = {
      id: Date.now(),
      ...createForm.value,
      status: 'running',
      progress: 0,
      collected: 0,
      successRate: 0,
      duration: 0,
      createdAt: new Date(),
      logs: []
    }
    
    tasks.value.unshift(newTask)
    
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    resetCreateForm()
  } catch (error) {
    console.error('创建任务失败:', error)
  } finally {
    creating.value = false
  }
}

const resetCreateForm = () => {
  createForm.value = {
    name: '',
    type: '',
    targetUrl: '',
    frequency: '',
    description: ''
  }
  if (createFormRef.value) {
    createFormRef.value.resetFields()
  }
}

const handleCreateDialogClose = () => {
  resetCreateForm()
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
.tasks-page {
  padding: 0;
}

// 页面头部
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
    }
  }
}

// 筛选区域
.filter-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: var(--shadow-light);
  
  .filter-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .filter-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

// 任务容器
.tasks-container {
  margin-bottom: 24px;
}

// 任务网格
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

// 任务卡片
.task-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  &.running {
    border-left-color: var(--primary-color);
  }
  
  &.completed {
    border-left-color: var(--success-color);
  }
  
  &.paused {
    border-left-color: var(--warning-color);
  }
  
  &.failed {
    border-left-color: var(--danger-color);
  }
}

.task-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
  
  .task-info {
    flex: 1;
    
    .task-name {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .task-meta {
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 12px;
      color: var(--text-secondary);
      
      .task-type {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
  
  .task-actions {
    .action-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

.task-description {
  color: var(--text-regular);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.task-progress {
  margin-bottom: 16px;
  
  .progress-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 12px;
    
    span:first-child {
      color: var(--text-secondary);
    }
    
    span:last-child {
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.task-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  
  .stat-item {
    text-align: center;
    
    .stat-label {
      display: block;
      font-size: 11px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }
    
    .stat-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
}

.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    
    &.running {
      background: rgba(64, 158, 255, 0.1);
      color: var(--primary-color);
    }
    
    &.completed {
      background: rgba(103, 194, 58, 0.1);
      color: var(--success-color);
    }
    
    &.paused {
      background: rgba(230, 162, 60, 0.1);
      color: var(--warning-color);
    }
    
    &.failed {
      background: rgba(245, 108, 108, 0.1);
      color: var(--danger-color);
    }
  }
  
  .task-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

// 空状态
.empty-state {
  text-align: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 64px;
    color: var(--text-placeholder);
    margin-bottom: 16px;
  }
  
  h3 {
    margin: 0 0 8px 0;
    color: var(--text-primary);
  }
  
  p {
    margin: 0 0 24px 0;
    color: var(--text-secondary);
  }
}

// 分页
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

// 任务详情
.task-detail {
  .detail-section {
    margin-bottom: 24px;
    
    h4 {
      margin: 0 0 16px 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      border-bottom: 1px solid var(--border-light);
      padding-bottom: 8px;
    }
  }
  
  .detail-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    
    .detail-item {
      display: flex;
      align-items: center;
      
      label {
        width: 80px;
        font-size: 12px;
        color: var(--text-secondary);
        margin-right: 8px;
      }
      
      span {
        font-size: 13px;
        color: var(--text-primary);
      }
    }
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    
    .stat-card {
      text-align: center;
      padding: 16px;
      background: var(--bg-secondary);
      border-radius: 8px;
      
      .stat-value {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .stat-label {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
  
  .log-list {
    max-height: 200px;
    overflow-y: auto;
    
    .log-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;
      border-bottom: 1px solid var(--border-lighter);
      font-size: 12px;
      
      &:last-child {
        border-bottom: none;
      }
      
      .log-time {
        color: var(--text-secondary);
        width: 120px;
        flex-shrink: 0;
      }
      
      .log-level {
        width: 60px;
        flex-shrink: 0;
        font-weight: 500;
        
        &.info {
          color: var(--info-color);
        }
        
        &.success {
          color: var(--success-color);
        }
        
        &.warning {
          color: var(--warning-color);
        }
        
        &.error {
          color: var(--danger-color);
        }
      }
      
      .log-message {
        flex: 1;
        color: var(--text-regular);
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-section {
    flex-direction: column;
    gap: 16px;
    
    .filter-left,
    .filter-right {
      width: 100%;
      justify-content: space-between;
    }
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .task-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .task-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>