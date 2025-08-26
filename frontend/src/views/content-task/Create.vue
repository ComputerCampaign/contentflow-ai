<template>
  <div class="task-create">
    <PageHeader title="创建文本生成任务" description="创建新的文本生成任务">
      <template #actions>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          创建任务
        </el-button>
      </template>
    </PageHeader>

    <div class="task-create-content">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="task-form"
      >
        <el-card class="form-section">
          <template #header>
            <span class="section-title">基本信息</span>
          </template>
          
          <el-form-item label="任务名称" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入任务名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="任务描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入任务描述"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="数据源任务" prop="sourceTaskId">
            <el-select
              v-model="form.sourceTaskId"
              placeholder="请选择已完成的爬虫任务作为数据源"
              style="width: 100%"
              filterable
              @change="handleSourceTaskChange"
            >
              <el-option
                v-for="task in sourceTaskList"
                :key="task.id"
                :label="task.name"
                :value="task.id"
              >
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ task.name }}</span>
                  <span style="color: #999; font-size: 12px;">{{ formatDate(task.completed_at) }}</span>
                </div>
              </el-option>
            </el-select>
            <div style="font-size: 12px; color: #999; margin-top: 4px;">只显示已完成的爬虫任务</div>
          </el-form-item>
          
          <el-form-item label="AI模型配置" prop="aiModelConfigId">
            <el-select
              v-model="form.aiModelConfigId"
              placeholder="请选择AI模型配置"
              style="width: 100%"
              filterable
              @change="handleModelChange"
            >
              <el-option
                v-for="model in aiModelList"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              >
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ model.name }}</span>
                  <span style="color: #999; font-size: 12px;">{{ model.model_type }}</span>
                </div>
              </el-option>
            </el-select>
            <div style="font-size: 12px; color: #999; margin-top: 4px;">选择用于文本生成的AI模型</div>
          </el-form-item>
          
          <el-form-item label="任务优先级" prop="priority">
            <el-select v-model="form.priority" placeholder="请选择任务优先级">
              <el-option label="低 (1)" :value="1" />
              <el-option label="普通 (2)" :value="2" />
              <el-option label="高 (3)" :value="3" />
              <el-option label="很高 (4)" :value="4" />
              <el-option label="紧急 (5)" :value="5" />
            </el-select>
          </el-form-item>
        </el-card>

        <el-card class="form-section">
          <template #header>
            <span class="section-title">生成配置</span>
          </template>
          
          <el-form-item label="生成提示词" prop="prompt">
            <el-input
              v-model="form.prompt"
              type="textarea"
              :rows="4"
              placeholder="请输入文本生成的提示词，如：请总结以下内容的要点..."
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="最大生成长度" prop="maxLength">
            <el-input-number
              v-model="form.maxLength"
              :min="100"
              :max="4000"
              placeholder="生成文本的最大长度"
            />
          </el-form-item>
          
          <el-form-item label="启用通知">
            <el-switch
              v-model="form.enableNotification"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>
          
          <el-form-item
            v-if="form.enableNotification"
            label="通知邮箱"
            prop="notificationEmail"
          >
            <el-input
              v-model="form.notificationEmail"
              placeholder="任务完成后通知邮箱"
            />
          </el-form-item>
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { useTaskStore } from '@/stores/task'
import { useCrawlerStore } from '@/stores/crawler'
import taskApi, { type TaskPriority } from '@/api/task'
import aiModelApi from '@/api/ai-model'

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()
const crawlerStore = useCrawlerStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const sourceTaskList = ref<any[]>([])
const aiModelList = ref<any[]>([])

const form = reactive({
  name: '',
  description: '',
  sourceTaskId: '',
  aiModelConfigId: '',
  prompt: '',
  maxLength: 1000,
  enableNotification: false,
  notificationEmail: '',
  priority: 2 as TaskPriority
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '任务名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  sourceTaskId: [
    { required: true, message: '请选择数据源任务', trigger: 'change' }
  ],
  aiModelConfigId: [
    { required: true, message: '请选择AI模型配置', trigger: 'change' }
  ],
  prompt: [
    { required: true, message: '请输入生成提示词', trigger: 'blur' },
    { min: 10, max: 1000, message: '提示词长度在 10 到 1000 个字符', trigger: 'blur' }
  ],
  notificationEmail: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择任务优先级', trigger: 'change' }
  ]
}

// 根据路由参数获取任务类型
const getTaskType = () => {
  const taskType = route.query.type as string
  return taskType || 'web_scraping' // 默认为爬虫任务
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

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const taskType = getTaskType()
    await taskStore.createTask({
      ...form,
      type: taskType as any
    })
    ElMessage.success('任务创建成功')
    router.push(getTaskListPath(taskType))
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error('创建任务失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消创建任务吗？未保存的数据将丢失。',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '继续编辑',
        type: 'warning'
      }
    )
    const taskType = getTaskType()
    router.push(getTaskListPath(taskType))
  } catch {
    // 用户取消
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 处理数据源任务变化
const handleSourceTaskChange = (taskId: string) => {
  const selectedTask = sourceTaskList.value.find(task => task.id === taskId)
  if (selectedTask) {
    // 可以根据选中的任务自动填充一些信息
    if (!form.name) {
      form.name = `${selectedTask.name}_文本生成`
    }
  }
}

// 处理AI模型变化
const handleModelChange = (modelId: string) => {
  const selectedModel = aiModelList.value.find(model => model.id === modelId)
  if (selectedModel) {
    console.log('选中的AI模型:', selectedModel.name)
  }
}

// 加载已完成的爬虫任务列表
const loadSourceTasks = async () => {
  try {
    const response = await taskApi.getTasks({
       type: 'crawl',
       status: 'completed',
       pageSize: 100
     })
     
     if (response.success && response.data) {
       sourceTaskList.value = response.data.list.map(task => ({
         id: task.id,
         name: task.name,
         status: task.status,
         createdAt: task.completedAt || task.createdAt,
         description: task.description
       }))
    }
  } catch (error) {
    console.error('加载数据源任务失败:', error)
    ElMessage.error('加载数据源任务失败')
  }
}

// 加载AI模型配置列表
const loadAIModels = async () => {
  try {
    const response = await aiModelApi.getActiveAIModels()
    
    if (response.success && response.data) {
      aiModelList.value = response.data.models.map(model => ({
         id: model.id,
         name: model.name,
         description: model.description,
         model_key: model.model_key
       }))
    }
  } catch (error) {
    console.error('加载AI模型配置失败:', error)
    ElMessage.error('加载AI模型配置失败')
  }
}

onMounted(() => {
  loadSourceTasks()
  loadAIModels()
  
  // 如果URL参数中有source_task_id，自动选择
  const sourceTaskId = route.query.source_task_id as string
  if (sourceTaskId) {
    form.sourceTaskId = sourceTaskId
  }
})
</script>

<style scoped lang="scss">
.task-create {
  padding: 20px;
  
  &-content {
    margin-top: 20px;
  }
}

.task-form {
  max-width: 800px;
}

.form-section {
  margin-bottom: 20px;
  
  .section-title {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>