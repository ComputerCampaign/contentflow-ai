<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'create' ? '创建任务' : '编辑任务'"
    width="800px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      @submit.prevent
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="任务名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入任务名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="formData.priority" placeholder="请选择优先级">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="爬虫配置" prop="crawlerConfigId">
        <el-select
          v-model="formData.crawlerConfigId"
          placeholder="请选择爬虫配置"
          filterable
          @focus="loadCrawlerConfigs"
        >
          <el-option
            v-for="config in crawlerConfigs"
            :key="config.id"
            :label="config.name"
            :value="config.id"
          >
            <div class="config-option">
              <span>{{ config.name }}</span>
              <el-tag size="small" type="info">{{ config.url }}</el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="任务描述">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入任务描述（可选）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 执行配置 -->
      <el-divider content-position="left">执行配置</el-divider>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="最大页面数" prop="config.maxPages">
            <el-input-number
              v-model="formData.config.maxPages"
              :min="1"
              :max="10000"
              placeholder="最大页面数"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="并发数" prop="config.concurrency">
            <el-input-number
              v-model="formData.config.concurrency"
              :min="1"
              :max="10"
              placeholder="并发数"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="延迟时间(ms)" prop="config.delay">
            <el-input-number
              v-model="formData.config.delay"
              :min="0"
              :max="10000"
              placeholder="延迟时间"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="超时时间(ms)" prop="config.timeout">
            <el-input-number
              v-model="formData.config.timeout"
              :min="1000"
              :max="300000"
              placeholder="超时时间"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="重试次数" prop="config.retries">
            <el-input-number
              v-model="formData.config.retries"
              :min="0"
              :max="5"
              placeholder="重试次数"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="输出格式" prop="config.outputFormat">
            <el-select v-model="formData.config.outputFormat" placeholder="输出格式">
              <el-option label="JSON" value="json" />
              <el-option label="CSV" value="csv" />
              <el-option label="Excel" value="xlsx" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 调度配置 -->
      <el-divider content-position="left">调度配置</el-divider>
      
      <el-form-item label="执行方式">
        <el-radio-group v-model="formData.scheduleType">
          <el-radio label="immediate">立即执行</el-radio>
          <el-radio label="scheduled">定时执行</el-radio>
          <el-radio label="recurring">周期执行</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item
        v-if="formData.scheduleType === 'scheduled'"
        label="执行时间"
        prop="scheduledAt"
      >
        <el-date-picker
          v-model="formData.scheduledAt"
          type="datetime"
          placeholder="选择执行时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
      
      <el-form-item
        v-if="formData.scheduleType === 'recurring'"
        label="执行周期"
        prop="cronExpression"
      >
        <el-input
          v-model="formData.cronExpression"
          placeholder="请输入Cron表达式，如：0 0 * * *"
        >
          <template #append>
            <el-button @click="showCronHelper = true">帮助</el-button>
          </template>
        </el-input>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ mode === 'create' ? '创建' : '保存' }}
        </el-button>
      </div>
    </template>
    
    <!-- Cron表达式帮助对话框 -->
    <el-dialog
      v-model="showCronHelper"
      title="Cron表达式帮助"
      width="600px"
      append-to-body
    >
      <div class="cron-helper">
        <p>Cron表达式格式：分 时 日 月 周</p>
        <el-table :data="cronExamples" size="small">
          <el-table-column prop="expression" label="表达式" width="120" />
          <el-table-column prop="description" label="说明" />
        </el-table>
      </div>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useTaskStore } from '@/stores/task'
import { useCrawlerStore } from '@/stores/crawler'

interface Props {
  modelValue: boolean
  task?: any
  mode: 'create' | 'edit'
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 状态管理
const taskStore = useTaskStore()
const crawlerStore = useCrawlerStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const showCronHelper = ref(false)
const crawlerConfigs = ref<any[]>([])

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  priority: 'medium',
  crawlerConfigId: null,
  scheduleType: 'immediate',
  scheduledAt: '',
  cronExpression: '',
  config: {
    maxPages: 100,
    concurrency: 1,
    delay: 1000,
    timeout: 30000,
    retries: 3,
    outputFormat: 'json'
  }
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '任务名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  crawlerConfigId: [
    { required: true, message: '请选择爬虫配置', trigger: 'change' }
  ],
  scheduledAt: [
    {
      validator: (rule, value, callback) => {
        if (formData.scheduleType === 'scheduled' && !value) {
          callback(new Error('请选择执行时间'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  cronExpression: [
    {
      validator: (rule, value, callback) => {
        if (formData.scheduleType === 'recurring' && !value) {
          callback(new Error('请输入Cron表达式'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  'config.maxPages': [
    { required: true, message: '请输入最大页面数', trigger: 'blur' }
  ],
  'config.concurrency': [
    { required: true, message: '请输入并发数', trigger: 'blur' }
  ],
  'config.timeout': [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ]
}

// Cron表达式示例
const cronExamples = [
  { expression: '0 0 * * *', description: '每天午夜执行' },
  { expression: '0 */6 * * *', description: '每6小时执行一次' },
  { expression: '0 9 * * 1-5', description: '工作日上午9点执行' },
  { expression: '0 0 1 * *', description: '每月1号午夜执行' },
  { expression: '*/30 * * * *', description: '每30分钟执行一次' }
]

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 方法
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    description: '',
    priority: 'medium',
    crawlerConfigId: null,
    scheduleType: 'immediate',
    scheduledAt: '',
    cronExpression: '',
    config: {
      maxPages: 100,
      concurrency: 1,
      delay: 1000,
      timeout: 30000,
      retries: 3,
      outputFormat: 'json'
    }
  })
}

const loadFormData = () => {
  if (props.task && props.mode === 'edit') {
    Object.assign(formData, {
      name: props.task.name || '',
      description: props.task.description || '',
      priority: props.task.priority || 'medium',
      crawlerConfigId: props.task.crawlerConfigId || null,
      scheduleType: props.task.scheduleType || 'immediate',
      scheduledAt: props.task.scheduledAt || '',
      cronExpression: props.task.cronExpression || '',
      config: {
        maxPages: props.task.config?.maxPages || 100,
        concurrency: props.task.config?.concurrency || 1,
        delay: props.task.config?.delay || 1000,
        timeout: props.task.config?.timeout || 30000,
        retries: props.task.config?.retries || 3,
        outputFormat: props.task.config?.outputFormat || 'json'
      }
    })
  } else {
    resetForm()
  }
}

const loadCrawlerConfigs = async () => {
  try {
    await crawlerStore.fetchCrawlerConfigs()
    crawlerConfigs.value = crawlerStore.crawlerConfigs
  } catch (error) {
    ElMessage.error('获取爬虫配置失败')
  }
}

const handleClose = () => {
  visible.value = false
  nextTick(() => {
    formRef.value?.resetFields()
    resetForm()
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const taskData = {
      ...formData,
      id: props.mode === 'edit' ? props.task?.id : undefined
    }
    
    if (props.mode === 'create') {
      await taskStore.createTask({
        ...taskData,
        type: 'web_scraping' as any,
        priority: taskData.priority as any,
        crawlerConfigId: taskData.crawlerConfigId || undefined
      })
      ElMessage.success('任务创建成功')
    } else {
      await taskStore.updateTask(taskData.id, {
        ...taskData,
        priority: taskData.priority as any
      })
      ElMessage.success('任务更新成功')
    }
    
    emit('success')
  } catch (error) {
    if (error !== false) { // 表单验证失败时不显示错误消息
      ElMessage.error(props.mode === 'create' ? '任务创建失败' : '任务更新失败')
    }
  } finally {
    submitting.value = false
  }
}

// 监听对话框显示状态
watch(
  visible,
  (newVisible) => {
    if (newVisible) {
      loadFormData()
      loadCrawlerConfigs()
    }
  }
)
</script>

<style lang="scss" scoped>
.config-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cron-helper {
  p {
    margin-bottom: 16px;
    font-weight: 600;
  }
}
</style>