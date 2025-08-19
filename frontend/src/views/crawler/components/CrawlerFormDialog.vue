<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'create' ? '创建爬虫配置' : '编辑爬虫配置'"
    width="800px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="left"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h3 class="section-title">基本信息</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="name">
              <el-input
                v-model="formData.name"
                placeholder="请输入配置名称"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型" prop="type">
              <el-select v-model="formData.type" placeholder="请选择类型">
                <el-option label="列表页" value="list" />
                <el-option label="详情页" value="detail" />
                <el-option label="搜索页" value="search" />
                <el-option label="分类页" value="category" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="目标URL" prop="url">
          <el-input
            v-model="formData.url"
            placeholder="请输入目标URL，如：https://example.com"
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>
      
      <!-- 爬取配置 -->
      <div class="form-section">
        <h3 class="section-title">爬取配置</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="请求间隔" prop="delay">
              <el-input-number
                v-model="formData.delay"
                :min="100"
                :max="60000"
                :step="100"
                controls-position="right"
              />
              <span class="unit">毫秒</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="超时时间" prop="timeout">
              <el-input-number
                v-model="formData.timeout"
                :min="1000"
                :max="300000"
                :step="1000"
                controls-position="right"
              />
              <span class="unit">毫秒</span>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="重试次数" prop="retries">
              <el-input-number
                v-model="formData.retries"
                :min="0"
                :max="10"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="并发数" prop="concurrency">
              <el-input-number
                v-model="formData.concurrency"
                :min="1"
                :max="10"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="User-Agent">
          <el-select
            v-model="formData.userAgent"
            placeholder="请选择或输入User-Agent"
            filterable
            allow-create
          >
            <el-option
              v-for="ua in userAgentOptions"
              :key="ua.value"
              :label="ua.label"
              :value="ua.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Cookie">
          <el-input
            v-model="formData.cookies"
            type="textarea"
            :rows="2"
            placeholder="请输入Cookie，格式：name1=value1; name2=value2"
          />
        </el-form-item>
      </div>
      
      <!-- 提取规则 -->
      <div class="form-section">
        <h3 class="section-title">
          提取规则
          <el-button
            type="primary"
            size="small"
            :icon="Plus"
            @click="addExtractionRule"
          >
            添加规则
          </el-button>
        </h3>
        
        <div v-if="formData.extractionRules.length" class="rules-list">
          <div
            v-for="(rule, index) in formData.extractionRules"
            :key="index"
            class="rule-item"
          >
            <div class="rule-header">
              <span class="rule-index">规则 {{ index + 1 }}</span>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="removeExtractionRule(index)"
              >
                删除
              </el-button>
            </div>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  :prop="`extractionRules.${index}.name`"
                  :rules="[{ required: true, message: '请输入规则名称' }]"
                  label="规则名称"
                >
                  <el-input
                    v-model="rule.name"
                    placeholder="请输入规则名称"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="数据类型">
                  <el-select v-model="rule.type" placeholder="请选择数据类型">
                    <el-option label="文本" value="text" />
                    <el-option label="链接" value="link" />
                    <el-option label="图片" value="image" />
                    <el-option label="数字" value="number" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item
              :prop="`extractionRules.${index}.xpath`"
              :rules="[{ required: true, message: '请输入XPath表达式' }]"
              label="XPath表达式"
            >
              <el-input
                v-model="rule.xpath"
                placeholder="请输入XPath表达式，如：//div[@class='title']/text()"
              />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="属性名">
                  <el-input
                    v-model="rule.attribute"
                    placeholder="如：href, src等"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="默认值">
                  <el-input
                    v-model="rule.defaultValue"
                    placeholder="提取失败时的默认值"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="正则表达式">
              <el-input
                v-model="rule.regex"
                placeholder="用于进一步处理提取的内容"
              />
            </el-form-item>
          </div>
        </div>
        
        <div v-else class="empty-rules">
          <el-empty description="暂无提取规则" :image-size="60">
            <el-button type="primary" :icon="Plus" @click="addExtractionRule">
              添加第一个规则
            </el-button>
          </el-empty>
        </div>
      </div>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          {{ mode === 'create' ? '创建' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'

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

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表单数据
const defaultFormData = {
  name: '',
  url: '',
  type: 'web',
  description: '',
  status: 'active',
  delay: 1000,
  timeout: 30000,
  retries: 3,
  concurrency: 1,
  userAgent: '',
  cookies: '',
  extractionRules: [] as any[]
}

const formData = ref({ ...defaultFormData })

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入目标URL', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+/,
      message: '请输入有效的URL',
      trigger: 'blur'
    }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ],
  delay: [
    { required: true, message: '请输入请求间隔', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ],
  retries: [
    { required: true, message: '请输入重试次数', trigger: 'blur' }
  ],
  concurrency: [
    { required: true, message: '请输入并发数', trigger: 'blur' }
  ]
}

// User-Agent选项
const userAgentOptions = [
  {
    label: 'Chrome (Windows)',
    value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  },
  {
    label: 'Chrome (Mac)',
    value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  },
  {
    label: 'Firefox (Windows)',
    value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
  },
  {
    label: 'Safari (Mac)',
    value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
  }
]

// 监听配置变化
watch(
  () => props.config,
  (newConfig) => {
    if (newConfig && props.mode === 'edit') {
      formData.value = {
        ...defaultFormData,
        ...newConfig,
        extractionRules: newConfig.extractionRules || []
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
    nextTick(() => {
      formRef.value?.clearValidate()
    })
  }
})

// 提取规则相关方法
const addExtractionRule = () => {
  formData.value.extractionRules.push({
    name: '',
    type: 'text',
    xpath: '',
    attribute: '',
    regex: '',
    defaultValue: ''
  })
}

const removeExtractionRule = (index: number) => {
  formData.value.extractionRules.splice(index, 1)
}

// 事件处理
const handleClose = () => {
  visible.value = false
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    loading.value = true
    
    if (props.mode === 'create') {
      const createParams = {
        name: formData.value.name,
        description: formData.value.description,
        type: formData.value.type as 'web' | 'api' | 'rss' | 'sitemap',
        targetUrl: formData.value.url,
        extractionRules: formData.value.extractionRules.map((rule: any) => ({
          name: rule.name,
          method: rule.type as 'xpath' | 'css' | 'regex' | 'json',
          selector: rule.xpath || rule.selector || '',
          field: rule.attribute || 'text',
          required: rule.required || false,
          defaultValue: rule.defaultValue || ''
        }))
      }
      await crawlerStore.createCrawlerConfig(createParams)
      ElMessage.success('创建成功')
    } else {
      const updateParams = {
        name: formData.value.name,
        description: formData.value.description,
        type: formData.value.type as 'web' | 'api' | 'rss' | 'sitemap',
        targetUrl: formData.value.url,
        extractionRules: formData.value.extractionRules.map((rule: any) => ({
          name: rule.name,
          method: rule.type as 'xpath' | 'css' | 'regex' | 'json',
          selector: rule.xpath || rule.selector || '',
          field: rule.attribute || 'text',
          required: rule.required || false,
          defaultValue: rule.defaultValue || ''
        }))
      }
      await crawlerStore.updateCrawlerConfig(props.config.id, updateParams)
      ElMessage.success('保存成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.form-section {
  margin-bottom: 32px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
}

.unit {
  margin-left: 8px;
  color: var(--el-text-color-regular);
  font-size: 12px;
}

.rules-list {
  .rule-item {
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 16px;
    background: var(--el-fill-color-extra-light);
    
    .rule-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      .rule-index {
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
    }
  }
}

.empty-rules {
  text-align: center;
  padding: 40px 0;
}

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