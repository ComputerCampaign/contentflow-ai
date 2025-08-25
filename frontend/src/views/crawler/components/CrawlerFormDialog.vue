<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'create' ? '新建爬虫配置' : '编辑爬虫配置'"
    width="800px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <!-- 基本信息 -->
      <el-divider content-position="left">基本信息</el-divider>
      <el-form-item label="配置名称" prop="name" required>
        <el-input 
          v-model="formData.name" 
          placeholder="请输入配置名称"
        />
      </el-form-item>
      <el-form-item label="配置描述">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="2"
          placeholder="请输入配置描述"
        />
      </el-form-item>
      
      <!-- 存储配置 -->
      <el-divider content-position="left">存储配置</el-divider>
      <el-form-item label="数据目录">
        <el-input v-model="formData.data_dir" placeholder="crawler_data" />
      </el-form-item>
      
      <!-- 爬虫核心配置 -->
      <el-divider content-position="left">爬虫核心配置</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="超时时间(秒)" prop="timeout">
            <el-input-number v-model="formData.timeout" :min="1" :max="300" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="重试次数" prop="retry">
            <el-input-number v-model="formData.retry" :min="0" :max="10" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="最大工作线程" prop="max_workers">
            <el-input-number v-model="formData.max_workers" :min="1" :max="20" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="使用Selenium">
            <el-switch v-model="formData.use_selenium" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="邮件通知">
            <el-switch v-model="formData.email_notification" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="User Agent">
        <el-input v-model="formData.user_agent" type="textarea" :rows="2" placeholder="请输入User Agent" />
      </el-form-item>
      
      <!-- Selenium配置 -->
      <el-divider content-position="left">Selenium配置</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="无头模式">
            <el-switch v-model="formData.headless" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="禁用GPU">
            <el-switch v-model="formData.selenium_disable_gpu" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="禁用dev-shm">
            <el-switch v-model="formData.selenium_disable_dev_shm_usage" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="窗口大小">
            <el-input v-model="formData.selenium_window_size" placeholder="1920,1080" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="页面加载超时" prop="selenium_page_load_timeout">
            <el-input-number v-model="formData.selenium_page_load_timeout" :min="1" :max="300" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="隐式等待" prop="selenium_implicit_wait">
            <el-input-number v-model="formData.selenium_implicit_wait" :min="1" :max="60" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="代理设置">
            <el-input v-model="formData.proxy" placeholder="请输入代理地址，如：http://proxy.example.com:8080" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="页面加载等待时间">
            <el-input-number v-model="formData.page_load_wait" :min="1" :max="300" />
          </el-form-item>
        </el-col>
      </el-row>

      
      <!-- XPath配置 -->
      <el-divider content-position="left">XPath配置</el-divider>
      <el-form-item label="启用XPath">
        <el-switch v-model="formData.enable_xpath" />
      </el-form-item>
      <el-form-item label="规则ID列表">
        <el-select
          v-model="formData.rule_ids"
          multiple
          filterable
          placeholder="请选择要使用的XPath规则"
          style="width: 100%"
          :loading="loadingXPathRules"
        >
          <el-option
            v-for="rule in enabledXPathRules"
            :key="rule.rule_id"
            :label="`${rule.name} (${rule.rule_id})`"
            :value="rule.rule_id"
          >
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ rule.name }}</span>
              <span style="color: #999; font-size: 12px;">{{ rule.rule_id }}</span>
            </div>
          </el-option>
        </el-select>
        <div style="font-size: 12px; color: #999; margin-top: 4px;">选择要使用的XPath规则，支持多选和搜索</div>
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="XPath规则路径">
            <el-input v-model="formData.xpath_rules_path" placeholder="crawler/config/xpath/xpath_rules.json" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="默认规则ID">
            <el-input v-model="formData.xpath_default_rule_id" placeholder="general_article" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 脚本配置 -->
      <el-divider content-position="left">脚本配置</el-divider>
      <el-form-item label="Stealth脚本路径">
        <el-input v-model="formData.scripts_stealth_path" placeholder="crawler/config/scripts/stealth.min.js" />
      </el-form-item>
      
      <!-- 图片存储配置 -->
      <el-divider content-position="left">图片存储配置</el-divider>
      <el-form-item label="存储类型">
        <el-select v-model="formData.image_storage_type" style="width: 100%">
          <el-option label="GitHub" value="github"></el-option>
          <el-option label="本地" value="local"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          {{ mode === 'create' ? '创建配置' : '更新配置' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useCrawlerStore } from '@/stores/crawler'
import request from '@/utils/request'

interface Props {
  modelValue: boolean
  config?: any
  mode: 'create' | 'edit'
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const crawlerStore = useCrawlerStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const loadingXPathRules = ref(false)
const enabledXPathRules = ref<any[]>([])

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表单数据
const defaultFormData = {
  name: '',
  description: '',
  // 基本配置
  output: '',
  config: 'config.json',
  // 存储配置
  data_dir: 'crawler_data',
  // 爬虫核心配置
  timeout: 30,
  retry: 3,
  max_workers: 4,
  use_selenium: false,
  email_notification: false,
  user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  // Selenium配置
  headless: true,
  selenium_disable_gpu: true,
  selenium_disable_dev_shm_usage: true,
  selenium_window_size: '1920,1080',
  selenium_page_load_timeout: 30,
  selenium_implicit_wait: 10,
  proxy: '',
  page_load_wait: 10,
  // XPath配置
  enable_xpath: false,
  rule_ids: [] as string[],
  xpath_rules_path: 'crawler/config/xpath/xpath_rules.json',
  xpath_default_rule_id: 'general_article',
  // 脚本配置
  scripts_stealth_path: 'crawler/config/scripts/stealth.min.js',
  // 图片存储配置
  image_storage_type: 'github'
}

const formData = ref({ ...defaultFormData })

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 1, max: 50, message: '配置名称长度在1到50个字符', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' },
    { type: 'number', min: 1, max: 300, message: '超时时间范围为1-300秒', trigger: 'blur' }
  ],
  retry: [
    { required: true, message: '请输入重试次数', trigger: 'blur' },
    { type: 'number', min: 0, max: 10, message: '重试次数范围为0-10次', trigger: 'blur' }
  ],
  max_workers: [
    { required: true, message: '请输入最大工作线程数', trigger: 'blur' },
    { type: 'number', min: 1, max: 20, message: '最大工作线程数范围为1-20', trigger: 'blur' }
  ],
  selenium_page_load_timeout: [
    { type: 'number', min: 1, max: 300, message: '页面加载超时范围为1-300秒', trigger: 'blur' }
  ],
  selenium_implicit_wait: [
    { type: 'number', min: 1, max: 60, message: '隐式等待范围为1-60秒', trigger: 'blur' }
  ]
}

// 获取启用状态的XPath规则
const fetchEnabledXPathRules = async () => {
  try {
    loadingXPathRules.value = true
    const response = await request.get('/xpath/configs', {
      params: {
        status: 'active',
        per_page: 100
      }
    })
    
    if (response.success) {
      enabledXPathRules.value = response.data.items || []
    } else {
      console.error('获取XPath规则失败:', response.message)
      ElMessage.error(response.message || '获取XPath规则失败')
    }
  } catch (error: any) {
    console.error('获取XPath规则失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '获取XPath规则失败')
  } finally {
    loadingXPathRules.value = false
  }
}

// 监听配置变化
watch(
  () => props.config,
  (newConfig) => {
    if (newConfig && props.mode === 'edit') {
      formData.value = {
        ...defaultFormData,
        ...newConfig,
        // 处理rule_ids字段：如果是字符串，转换为数组
        rule_ids: typeof newConfig.rule_ids === 'string' 
          ? (newConfig.rule_ids ? newConfig.rule_ids.split(',').map((id: string) => id.trim()) : [])
          : (newConfig.rule_ids || [])
      }
    } else {
      formData.value = { ...defaultFormData }
    }
  },
  { immediate: true }
)

// 监听对话框显示状态
watch(visible, (newVisible) => {
  if (newVisible) {
    fetchEnabledXPathRules()
    nextTick(() => {
      formRef.value?.clearValidate()
    })
  }
})

// 事件处理
const handleClose = () => {
  visible.value = false
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.error('请检查表单输入')
    return
  }
  
  try {
    loading.value = true
    
    if (props.mode === 'create') {
      // 创建模式：直接调用后端API
      const configData = {
        name: formData.value.name,
        description: formData.value.description,
        output: formData.value.output,
        data_dir: formData.value.data_dir,
        use_selenium: formData.value.use_selenium,
        timeout: formData.value.timeout,
        retry: formData.value.retry,
        config: formData.value.config,
        email_notification: formData.value.email_notification,
        headless: formData.value.headless,
        selenium_disable_gpu: formData.value.selenium_disable_gpu,
        selenium_disable_dev_shm_usage: formData.value.selenium_disable_dev_shm_usage,
        selenium_window_size: formData.value.selenium_window_size,
        selenium_page_load_timeout: formData.value.selenium_page_load_timeout,
        selenium_implicit_wait: formData.value.selenium_implicit_wait,
        proxy: formData.value.proxy,
        page_load_wait: formData.value.page_load_wait,
        user_agent: formData.value.user_agent,
        rule_ids: Array.isArray(formData.value.rule_ids) ? formData.value.rule_ids.join(',') : (formData.value.rule_ids || ''),
        enable_xpath: formData.value.enable_xpath,
        xpath_rules_path: formData.value.xpath_rules_path,
        xpath_default_rule_id: formData.value.xpath_default_rule_id,
        scripts_stealth_path: formData.value.scripts_stealth_path,
        image_storage_type: formData.value.image_storage_type
      }
      await request.post('/api/crawler/configs', configData)
    } else {
      // 编辑模式：直接调用后端API
      const submitData = { ...formData.value }
      // 处理rule_ids：如果是数组，转换为字符串
      if (Array.isArray(submitData.rule_ids)) {
        (submitData as any).rule_ids = submitData.rule_ids.join(',')
      }
      await request.put(`/api/crawler/configs/${props.config.id}`, submitData)
    }
    
    ElMessage.success(props.mode === 'create' ? '创建成功' : '更新成功')
    emit('success')
    visible.value = false
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '操作失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchEnabledXPathRules()
})
</script>

<style lang="scss" scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>