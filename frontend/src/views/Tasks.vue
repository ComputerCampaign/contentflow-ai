<template>
  <div class="tasks-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <i class="fas fa-tasks"></i>
          任务管理
        </h1>
        <p class="page-subtitle">管理和监控您的爬虫任务</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openCreateDialog">
          <i class="fas fa-plus"></i>
          创建任务
        </el-button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="filter-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索任务名称或描述"
          prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          @change="handleFilter"
          class="filter-select"
        >
          <el-option label="全部状态" value="" />
          <el-option label="等待中" value="pending" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
          <el-option label="已暂停" value="paused" />
        </el-select>
        <el-select
          v-model="typeFilter"
          placeholder="类型筛选"
          clearable
          @change="handleFilter"
          class="filter-select"
        >
          <el-option label="全部类型" value="" />
          <el-option label="爬虫任务" value="crawler" />
          <el-option label="完整流水线" value="full_pipeline" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button @click="refreshTasks" :loading="loading">
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
    <div class="tasks-grid" v-loading="loading">
      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        <i class="fas fa-inbox empty-icon"></i>
        <h3>暂无任务</h3>
        <p>点击上方"创建任务"按钮开始创建您的第一个任务</p>
      </div>
      
      <div v-else class="task-cards">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-card"
          @click="showTaskDetail(task)"
        >
          <div class="card-header">
            <div class="task-info">
              <h3 class="task-name">{{ task.name }}</h3>
              <span class="task-type">{{ getTaskTypeLabel(task.type) }}</span>
            </div>
            <div class="task-status">
              <el-tag :type="getStatusType(task.status)" size="small">
                {{ getStatusLabel(task.status) }}
              </el-tag>
            </div>
          </div>
          
          <div class="card-body">
            <div class="task-meta">
              <div class="meta-item">
                <i class="fas fa-link"></i>
                <span class="meta-label">目标URL:</span>
                <span class="meta-value" :title="task.url">{{ task.url || '-' }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-calendar"></i>
                <span class="meta-label">创建时间:</span>
                <span class="meta-value">{{ formatDate(task.created_at) }}</span>
              </div>
              <div v-if="task.description" class="meta-item">
                <i class="fas fa-align-left"></i>
                <span class="meta-label">描述:</span>
                <span class="meta-value">{{ task.description }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <div class="task-actions">
              <el-button size="small" @click.stop="showTaskDetail(task)">
                <i class="fas fa-eye"></i>
                查看详情
              </el-button>
              <el-button size="small" @click.stop="editTask(task)">
                <i class="fas fa-edit"></i>
                编辑
              </el-button>
              <el-button size="small" @click.stop="cloneTask(task)">
                <i class="fas fa-copy"></i>
                克隆
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click.stop="deleteTask(task)"
              >
                <i class="fas fa-trash"></i>
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="pagination.total > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditMode ? '编辑任务' : '创建任务'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input
            v-model="createForm.name"
            placeholder="请输入任务名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="createForm.type" placeholder="请选择任务类型" style="width: 100%" @change="onTaskTypeChange">
            <el-option label="爬虫任务" value="crawler" />
            <el-option label="完整流水线" value="full_pipeline" />
          </el-select>
        </el-form-item>
        
        <!-- URL输入框 -->
        <el-form-item 
          v-if="createForm.type === 'crawler' || createForm.type === 'full_pipeline'" 
          label="目标URL" 
          prop="url"
        >
          <el-input
            v-model="createForm.url"
            placeholder="请输入要爬取的网站URL"
            maxlength="500"
          />
        </el-form-item>
        
        <!-- 爬虫配置选择 -->
        <el-form-item 
          v-if="createForm.type === 'crawler' || createForm.type === 'full_pipeline'" 
          label="爬虫配置" 
          prop="crawler_config_id"
        >
          <div style="width: 100%">
            <el-select 
              v-model="createForm.crawler_config_id" 
              placeholder="请选择爬虫配置" 
              style="width: 100%"
              :loading="configsLoading"
            >
              <el-option 
                v-for="config in crawlerConfigs" 
                :key="config.id" 
                :label="config.name" 
                :value="config.id"
              />
            </el-select>
            <div v-if="crawlerConfigs.length === 0 && !configsLoading" class="config-tip">
              <el-text type="warning" size="small">
                暂无可用的爬虫配置，请先到
                <el-link type="primary" href="/crawler" target="_blank">爬虫配置页面</el-link>
                创建配置
              </el-text>
            </div>
          </div>
        </el-form-item>
        

        

        
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelDialog">取消</el-button>
          <el-button type="primary" @click="submitTask" :loading="createLoading">
            {{ isEditMode ? '保存修改' : '创建任务' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedTask" class="task-detail">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">任务名称:</span>
              <span class="info-value">{{ selectedTask.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">任务类型:</span>
              <span class="info-value">{{ getTaskTypeLabel(selectedTask.type) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">目标URL:</span>
              <span class="info-value">{{ selectedTask.url || '-' }}</span>
            </div>
            <div v-if="selectedTask.crawler_config_id" class="info-item">
              <span class="info-label">爬虫配置:</span>
              <span class="info-value">{{ crawlerConfigName || '加载中...' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间:</span>
              <span class="info-value">{{ formatDate(selectedTask.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">任务状态:</span>
              <el-tag :type="getStatusType(selectedTask.status)" size="small">
                {{ getStatusLabel(selectedTask.status) }}
              </el-tag>
            </div>
            <div v-if="selectedTask.description" class="info-item full-width">
              <span class="info-label">任务描述:</span>
              <span class="info-value">{{ selectedTask.description }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>执行信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">最后执行时间:</span>
              <span class="info-value">{{ formatDate(selectedTask.last_run) || '未执行' }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>执行命令生成</h4>
          <div class="command-section">
            <div class="command-actions">
              <el-button type="primary" @click="generateCommand">
                <i class="fas fa-terminal"></i>
                生成执行命令
              </el-button>
            </div>
            <div v-if="generatedCommand" class="command-output">
              <el-input
                v-model="generatedCommand"
                type="textarea"
                :rows="3"
                readonly
                placeholder="点击上方按钮生成执行命令"
              >
                <template #append>
                  <el-button @click="copyCommand">
                    <i class="fas fa-copy"></i>
                    复制
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tasksAPI } from '@/api/tasks'
import { crawlerAPI } from '@/api/crawler'
import { xpathAPI } from '@/api/xpath'

// 响应式数据
const loading = ref(false)
const createLoading = ref(false)
const configsLoading = ref(false)
const sourceTasksLoading = ref(false)
const tasks = ref([])
const selectedTask = ref(null)
const taskLogs = ref([])
const crawlerConfigs = ref([])
const sourceTasks = ref([])
const generatedCommand = ref('')
const crawlerConfigName = ref('')
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const createFormRef = ref(null)
const isEditMode = ref(false)
const editingTaskId = ref(null)

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 创建任务表单
const createForm = reactive({
  name: '',
  type: '',
  url: '',
  crawler_config_id: '',
  source_task_id: '',
  description: ''
})

// 表单验证规则
const createFormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '任务名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  url: [
    { 
      required: true, 
      message: '请输入目标URL', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if ((createForm.type === 'crawler' || createForm.type === 'full_pipeline') && !value) {
          callback(new Error('请输入目标URL'))
        } else if (value && !/^https?:\/\/.+/.test(value)) {
          callback(new Error('请输入有效的URL格式'))
        } else {
          callback()
        }
      }
    }
  ],
  crawler_config_id: [
    { 
      required: true, 
      message: '请选择爬虫配置', 
      trigger: 'change',
      validator: (rule, value, callback) => {
        if ((createForm.type === 'crawler' || createForm.type === 'full_pipeline') && !value) {
          callback(new Error('请选择爬虫配置'))
        } else {
          callback()
        }
      }
    }
  ],
  source_task_id: [
    {
      required: true,
      message: '请选择源任务',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (createForm.type === 'content_generation' && !value) {
          callback(new Error('请选择源任务'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 获取任务列表
const getTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      search: searchQuery.value,
      status: statusFilter.value,
      type: typeFilter.value
    }
    
    const response = await tasksAPI.getTasks(params)
    tasks.value = response.data.tasks || []
    pagination.total = response.data.pagination?.total || 0
  } catch (error) {
    ElMessage.error('获取任务列表失败')
    console.error('获取任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取爬虫配置列表
const getCrawlerConfigs = async () => {
  configsLoading.value = true
  try {
    const response = await crawlerAPI.getConfigs({ enabled: 'true' })
    crawlerConfigs.value = response.data.configs || []
  } catch (error) {
    ElMessage.error('获取爬虫配置列表失败')
    console.error('获取爬虫配置列表失败:', error)
    crawlerConfigs.value = []
  } finally {
    configsLoading.value = false
  }
}



// 获取源任务列表（爬虫任务）
const getSourceTasks = async () => {
  sourceTasksLoading.value = true
  try {
    const response = await tasksAPI.getTasks({
      type: 'crawler',
      status: 'completed',
      per_page: 100
    })
    sourceTasks.value = response.data.tasks || []
  } catch (error) {
    ElMessage.error('获取源任务列表失败')
    console.error('获取源任务列表失败:', error)
    sourceTasks.value = []
  } finally {
    sourceTasksLoading.value = false
  }
}

// 任务类型变化处理
const onTaskTypeChange = (type) => {
  // 重置相关字段
  createForm.url = ''
  createForm.crawler_config_id = ''
  createForm.source_task_id = ''
  
  // 根据任务类型获取相应的配置列表
  if (type === 'crawler' || type === 'full_pipeline') {
    getCrawlerConfigs()
  }
}

// 创建任务
const createTask = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    createLoading.value = true
    
    let taskData = {
      name: createForm.name,
      url: createForm.url,
      crawler_config_id: createForm.crawler_config_id
    }
    
    // 根据任务类型调用不同的API端点
    if (createForm.type === 'crawler') {
      // 调用爬虫任务创建端点
      await tasksAPI.createCrawlerTask(taskData)
    } else if (createForm.type === 'full_pipeline') {
      // 全流程任务需要AI配置ID，这里暂时使用默认值或从表单获取
      taskData.ai_config_id = createForm.ai_config_id || 'default'
      await tasksAPI.createCombinedTask(taskData)
    } else {
      // 其他类型任务使用通用创建方法
      taskData.type = createForm.type
      taskData.description = createForm.description
      await tasksAPI.createTask(taskData)
    }
    
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    resetCreateForm()
    getTasks()
  } catch (error) {
    ElMessage.error('任务创建失败')
    console.error('任务创建失败:', error)
  } finally {
    createLoading.value = false
  }
}

// 重置创建表单
const resetCreateForm = () => {
  Object.assign(createForm, {
    name: '',
    type: '',
    url: '',
    crawler_config_id: '',
    source_task_id: '',
    description: ''
  })
  createFormRef.value?.resetFields()
  isEditMode.value = false
  editingTaskId.value = null
}

// 打开创建对话框
const openCreateDialog = () => {
  resetCreateForm()
  showCreateDialog.value = true
}

// 取消对话框
const cancelDialog = () => {
  showCreateDialog.value = false
  resetCreateForm()
}

// 提交任务（创建或更新）
const submitTask = async () => {
  if (isEditMode.value) {
    await updateTask()
  } else {
    await createTask()
  }
}

// 更新任务
const updateTask = async () => {
  if (!createFormRef.value || !editingTaskId.value) return
  
  try {
    await createFormRef.value.validate()
    createLoading.value = true
    
    const taskData = {
      name: createForm.name,
      url: createForm.url,
      crawler_config_id: createForm.crawler_config_id,
      description: createForm.description
    }
    
    await tasksAPI.updateTask(editingTaskId.value, taskData)
    
    ElMessage.success('任务更新成功')
    showCreateDialog.value = false
    resetCreateForm()
    getTasks()
  } catch (error) {
    ElMessage.error('任务更新失败')
    console.error('任务更新失败:', error)
  } finally {
    createLoading.value = false
  }
}

// 显示任务详情
const showTaskDetail = async (task) => {
  selectedTask.value = task
  showDetailDialog.value = true
  
  // 不再获取任务日志，避免404错误
  taskLogs.value = []
  // 清空之前生成的命令
  generatedCommand.value = ''
  // 清空爬虫配置名称
  crawlerConfigName.value = ''
  
  // 如果任务有爬虫配置ID，获取配置名称
  if (task.crawler_config_id) {
    try {
      console.log('正在获取爬虫配置，ID:', task.crawler_config_id)
      const response = await crawlerAPI.getConfig(task.crawler_config_id)
      console.log('爬虫配置API响应:', response)
      
      // 根据后端实际返回的数据结构处理
      if (response.data && response.data.name) {
        crawlerConfigName.value = response.data.name
        console.log('成功设置爬虫配置名称:', response.data.name)
      } else {
        console.log('响应数据结构不符合预期:', response)
        crawlerConfigName.value = '未知配置'
      }
    } catch (error) {
      console.error('获取爬虫配置名称失败:', error)
      crawlerConfigName.value = '未知配置'
    }
  }
}

// 编辑任务
const editTask = (task) => {
  // 设置编辑模式
  isEditMode.value = true
  editingTaskId.value = task.id
  
  // 填充编辑表单
  Object.assign(createForm, {
    name: task.name,
    type: task.type,
    url: task.url || '',
    crawler_config_id: task.crawler_config_id || '',
    source_task_id: task.source_task_id || '',
    description: task.description || ''
  })
  
  // 根据任务类型获取相应的配置列表
  if (task.type === 'crawler' || task.type === 'full_pipeline') {
    getCrawlerConfigs()
  }
  
  showCreateDialog.value = true
}

// 克隆任务
const cloneTask = async (task) => {
  try {
    await tasksAPI.cloneTask(task.id)
    ElMessage.success('任务克隆成功')
    getTasks()
  } catch (error) {
    ElMessage.error('任务克隆失败')
    console.error('任务克隆失败:', error)
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await tasksAPI.deleteTask(task.id)
    ElMessage.success('任务删除成功')
    getTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('任务删除失败')
      console.error('任务删除失败:', error)
    }
  }
}



// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  getTasks()
}

// 筛选处理
const handleFilter = () => {
  pagination.page = 1
  getTasks()
}

// 刷新任务
const refreshTasks = () => {
  getTasks()
}

// 导出任务
const exportTasks = async () => {
  try {
    await tasksAPI.exportTasks({
      search: searchQuery.value,
      status: statusFilter.value,
      type: typeFilter.value
    })
    ElMessage.success('任务数据导出成功')
  } catch (error) {
    ElMessage.error('任务数据导出失败')
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  getTasks()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  getTasks()
}

// 获取当前启用的XPath规则ID列表
const getActiveRuleIds = async () => {
  try {
    const response = await xpathAPI.getRules({ status: 'active', enabled: 'true', per_page: 100 })
    if (response.success && response.data && response.data.rules) {
      return response.data.rules.map(rule => rule.rule_id).join(',')
    }
  } catch (error) {
    console.warn('获取XPath规则失败:', error)
  }
  return '' // 如果获取失败，返回空字符串
}

// 生成执行命令
const generateCommand = async () => {
  if (!selectedTask.value || !selectedTask.value.id) {
    ElMessage.error('请选择有效的任务')
    return
  }
  
  try {
    console.log('正在生成命令，任务ID:', selectedTask.value.id)
    const response = await tasksAPI.getTaskCommand(selectedTask.value.id)
    console.log('任务命令API响应:', response)
    
    // 处理不同的响应数据结构
    if (response.data) {
      // 尝试多种可能的数据结构
      const commandData = response.data.data || response.data.command || response.data
      
      if (typeof commandData === 'string') {
        // 如果直接返回命令字符串
        generatedCommand.value = commandData
        console.log('成功生成命令:', commandData)
        ElMessage.success('命令生成成功')
      } else if (commandData && commandData.command) {
        // 如果返回包含command字段的对象
        generatedCommand.value = commandData.command
        console.log('成功生成命令:', commandData.command)
        ElMessage.success('命令生成成功')
      } else {
        console.log('命令生成失败，响应数据结构不符合预期:', response)
        ElMessage.error(response.data.message || '生成命令失败：响应数据格式错误')
      }
    } else {
      console.log('命令生成失败，响应数据为空:', response)
      ElMessage.error('生成命令失败：服务器响应为空')
    }
  } catch (error) {
    console.error('生成命令失败:', error)
    ElMessage.error('生成命令失败，请稍后重试')
  }
}

// 复制命令到剪贴板
const copyCommand = async () => {
  if (!generatedCommand.value) {
    ElMessage.warning('请先生成执行命令')
    return
  }
  
  try {
    await navigator.clipboard.writeText(generatedCommand.value)
    ElMessage.success('命令已复制到剪贴板')
  } catch (error) {
    // 降级方案：使用传统方法复制
    const textArea = document.createElement('textarea')
    textArea.value = generatedCommand.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('命令已复制到剪贴板')
  }
}

// 工具函数
const getTaskTypeLabel = (type) => {
  const typeMap = {
    crawler: '爬虫任务',
    full_pipeline: '完整流水线'
  }
  return typeMap[type] || type
}

const getStatusLabel = (status) => {
  const statusMap = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    paused: '已暂停'
  }
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    paused: 'info'
  }
  return typeMap[status] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}



// 生命周期
onMounted(() => {
  getTasks()
})
</script>

<style scoped>
.config-tip {
  margin-top: 8px;
  padding: 8px;
  background-color: #fdf6ec;
  border: 1px solid #f5dab1;
  border-radius: 4px;
}
.tasks-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title i {
  color: #409eff;
}

.page-subtitle {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.filter-right {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 150px;
}

.tasks-grid {
  margin-bottom: 24px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 64px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #606266;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #909399;
  margin: 0;
}

.task-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.task-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.task-type {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.task-status {
  margin-left: 16px;
}

.card-body {
  padding: 16px 20px;
}

.task-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.meta-item i {
  color: #909399;
  width: 14px;
  text-align: center;
}

.meta-label {
  color: #606266;
  font-weight: 500;
  min-width: 70px;
}

.meta-value {
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.task-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.task-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-item.full-width {
  grid-column: 1 / -1;
  align-items: flex-start;
}

.info-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.info-value {
  color: #303133;
  flex: 1;
  word-break: break-all;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.no-logs {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.logs-list {
  padding: 16px;
}

.log-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-time {
  color: #909399;
  font-size: 12px;
}

.log-error {
  color: #f56c6c;
  margin-bottom: 4px;
}

.log-result {
  color: #67c23a;
  font-family: monospace;
  font-size: 12px;
}

.command-section {
  margin-top: 16px;
}

.command-actions {
  margin-bottom: 16px;
}

.command-output {
  margin-top: 16px;
}

.command-output .el-input {
  font-family: 'Courier New', monospace;
}

.command-output .el-textarea__inner {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}

.command-output .el-input-group__append {
  padding: 0;
}

.command-output .el-input-group__append .el-button {
  border-left: none;
  border-radius: 0 4px 4px 0;
}

@media (max-width: 768px) {
  .tasks-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-left {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-input,
  .filter-select {
    width: 100%;
  }
  
  .task-cards {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>