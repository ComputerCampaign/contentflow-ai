<template>
  <div class="task-edit">
    <PageHeader :title="`编辑任务 - ${taskData?.name || ''}`" description="修改任务配置">
      <template #actions>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          保存修改
        </el-button>
      </template>
    </PageHeader>

    <div class="task-edit-content" v-loading="pageLoading">
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
          
          <el-form-item label="爬虫配置" prop="crawlerId">
            <el-select
              v-model="form.crawlerId"
              placeholder="请选择爬虫配置"
              style="width: 100%"
              filterable
            >
              <el-option
                v-for="crawler in crawlerList"
                :key="crawler.id"
                :label="crawler.name"
                :value="crawler.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="任务优先级" prop="priority">
            <el-select v-model="form.priority" placeholder="请选择优先级">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="任务状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择状态">
              <el-option label="待执行" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="已失败" value="failed" />
              <el-option label="已暂停" value="paused" />
            </el-select>
          </el-form-item>
        </el-card>

        <el-card class="form-section">
          <template #header>
            <span class="section-title">执行配置</span>
          </template>
          
          <el-form-item label="执行模式" prop="mode">
            <el-radio-group v-model="form.mode">
              <el-radio value="immediate">立即执行</el-radio>
              <el-radio value="scheduled">定时执行</el-radio>
              <el-radio value="manual">手动执行</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item
            v-if="form.mode === 'scheduled'"
            label="执行时间"
            prop="scheduledTime"
          >
            <el-date-picker
              v-model="form.scheduledTime"
              type="datetime"
              placeholder="选择执行时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
          
          <el-form-item label="重试次数" prop="retryCount">
            <el-input-number
              v-model="form.retryCount"
              :min="0"
              :max="10"
              placeholder="失败重试次数"
            />
          </el-form-item>
          
          <el-form-item label="超时时间" prop="timeout">
            <el-input-number
              v-model="form.timeout"
              :min="10"
              :max="3600"
              placeholder="任务超时时间（秒）"
            />
          </el-form-item>
        </el-card>

        <el-card class="form-section">
          <template #header>
            <span class="section-title">高级设置</span>
          </template>
          
          <el-form-item label="并发数" prop="concurrency">
            <el-input-number
              v-model="form.concurrency"
              :min="1"
              :max="20"
              placeholder="并发执行数量"
            />
          </el-form-item>
          
          <el-form-item label="延迟设置" prop="delay">
            <el-input-number
              v-model="form.delay"
              :min="0"
              :max="10000"
              placeholder="请求间隔延迟（毫秒）"
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

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()
const crawlerStore = useCrawlerStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const pageLoading = ref(true)
const crawlerList = ref<any[]>([])
const taskData = ref<any>(null)

const form = reactive({
  name: '',
  description: '',
  crawlerId: '',
  priority: 'medium',
  status: 'pending',
  mode: 'immediate',
  scheduledTime: '',
  retryCount: 3,
  timeout: 300,
  concurrency: 1,
  delay: 1000,
  enableNotification: false,
  notificationEmail: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '任务名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  crawlerId: [
    { required: true, message: '请选择爬虫配置', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择任务优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择任务状态', trigger: 'change' }
  ],
  mode: [
    { required: true, message: '请选择执行模式', trigger: 'change' }
  ],
  scheduledTime: [
    { required: true, message: '请选择执行时间', trigger: 'change' }
  ],
  notificationEmail: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
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
    
    await taskStore.updateTask(parseInt(route.params.id as string), {
      ...form,
      priority: form.priority as any
    })
    ElMessage.success('任务修改成功')
    router.push(getTaskListPath(taskData.value?.type || 'web_scraping'))
  } catch (error) {
    console.error('修改任务失败:', error)
    ElMessage.error('修改任务失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消修改吗？未保存的数据将丢失。',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '继续编辑',
        type: 'warning'
      }
    )
    router.push(getTaskListPath(taskData.value?.type || 'web_scraping'))
  } catch {
    // 用户取消
  }
}

const loadTaskData = async () => {
  try {
    const taskId = route.params.id as string
    const task = await taskStore.fetchTaskById(parseInt(taskId))
    taskData.value = task
    
    // 填充表单数据
    Object.assign(form, {
      name: task?.name || '',
      description: task?.description || '',
      crawlerId: task?.crawlerConfigId || '',
      priority: task?.priority || 'medium',
      status: task?.status || 'pending',
      mode: task?.mode || 'immediate',
      scheduledTime: task?.scheduledTime || '',
      retryCount: task?.retryCount || 3,
      timeout: task?.timeout || 30000,
      concurrency: task?.concurrency || 1,
      delay: task?.delay || 1000,
      enableNotification: task?.enableNotification || false,
      notificationEmail: task?.notificationEmail || ''
    })
  } catch (error) {
    console.error('加载任务数据失败:', error)
    ElMessage.error('加载任务数据失败')
    router.push('/crawler-tasks/list') // 默认跳转到爬虫任务列表
  }
}

const loadCrawlerList = async () => {
  try {
    await crawlerStore.fetchCrawlerConfigs()
    crawlerList.value = crawlerStore.crawlerConfigs
  } catch (error) {
    console.error('加载爬虫配置失败:', error)
    ElMessage.error('加载爬虫配置失败')
  }
}

const initPage = async () => {
  pageLoading.value = true
  try {
    await Promise.all([
      loadTaskData(),
      loadCrawlerList()
    ])
  } finally {
    pageLoading.value = false
  }
}

onMounted(() => {
  initPage()
})
</script>

<style scoped lang="scss">
.task-edit {
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