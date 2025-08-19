<template>
  <div class="crawler-edit">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>编辑爬虫配置</h2>
          <div class="header-actions">
            <el-button @click="handleTest" :loading="testing">测试配置</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">保存配置</el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="crawler-form"
      >
        <!-- 基本信息 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>基本信息</h3>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="配置名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入配置名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="目标网站" prop="baseUrl">
                <el-input v-model="form.baseUrl" placeholder="请输入目标网站URL" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入配置描述"
            />
          </el-form-item>
        </el-card>

        <!-- 请求配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>请求配置</h3>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="请求方法" prop="method">
                <el-select v-model="form.method" placeholder="选择请求方法">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="请求间隔" prop="requestInterval">
                <el-input-number
                  v-model="form.requestInterval"
                  :min="100"
                  :max="60000"
                  :step="100"
                  placeholder="毫秒"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="超时时间" prop="timeout">
                <el-input-number
                  v-model="form.timeout"
                  :min="1000"
                  :max="300000"
                  :step="1000"
                  placeholder="毫秒"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="请求头">
            <div class="headers-config">
              <div
                v-for="(header, index) in form.headers"
                :key="index"
                class="header-item"
              >
                <el-input
                  v-model="header.key"
                  placeholder="Header名称"
                  class="header-key"
                />
                <el-input
                  v-model="header.value"
                  placeholder="Header值"
                  class="header-value"
                />
                <el-button
                  type="danger"
                  icon="Delete"
                  @click="removeHeader(index)"
                  circle
                />
              </div>
              <el-button @click="addHeader" type="primary" plain>
                添加请求头
              </el-button>
            </div>
          </el-form-item>
        </el-card>

        <!-- 数据提取配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>数据提取配置</h3>
          </template>
          
          <el-form-item label="提取规则">
            <div class="extraction-rules">
              <div
                v-for="(rule, index) in form.extractionRules"
                :key="index"
                class="rule-item"
              >
                <el-row :gutter="10">
                  <el-col :span="6">
                    <el-input
                      v-model="rule.name"
                      placeholder="字段名称"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-select v-model="rule.method" placeholder="提取类型">
                      <el-option label="XPath" value="xpath" />
                      <el-option label="CSS选择器" value="css" />
                      <el-option label="正则表达式" value="regex" />
                    </el-select>
                  </el-col>
                  <el-col :span="10">
                    <el-input
                      v-model="rule.selector"
                      placeholder="选择器表达式"
                    />
                  </el-col>
                  <el-col :span="2">
                    <el-button
                      type="danger"
                      icon="Delete"
                      @click="removeRule(index)"
                      circle
                    />
                  </el-col>
                </el-row>
                <el-row :gutter="10" style="margin-top: 10px">
                  <el-col :span="6">
                    <el-select v-model="rule.field" placeholder="字段名称">
                      <el-option label="文本" value="text" />
                      <el-option label="链接" value="link" />
                      <el-option label="图片" value="image" />
                      <el-option label="数字" value="number" />
                    </el-select>
                  </el-col>
                  <el-col :span="6">
                    <el-checkbox v-model="rule.required">必填字段</el-checkbox>
                  </el-col>
                  <el-col :span="12">
                    <el-input
                      v-model="rule.defaultValue"
                      placeholder="默认值（可选）"
                    />
                  </el-col>
                </el-row>
              </div>
              <el-button @click="addRule" type="primary" plain>
                添加提取规则
              </el-button>
            </div>
          </el-form-item>
        </el-card>

        <!-- 高级设置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>高级设置</h3>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="最大重试次数">
                <el-input-number
                  v-model="form.maxRetries"
                  :min="0"
                  :max="10"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="并发数">
                <el-input-number
                  v-model="form.concurrency"
                  :min="1"
                  :max="10"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="状态">
                <el-switch
                  v-model="form.enabled"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="User-Agent">
                <el-input
                  v-model="form.userAgent"
                  placeholder="自定义User-Agent"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="代理设置">
                <el-input
                  v-model="form.proxy"
                  placeholder="代理服务器地址（可选）"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useCrawlerStore } from '@/stores/crawler'
import type { CrawlerConfig, UpdateCrawlerParams } from '@/api/crawler'

const route = useRoute()
const router = useRouter()
const crawlerStore = useCrawlerStore()

const formRef = ref<FormInstance>()
const saving = ref(false)
const testing = ref(false)

const form = reactive({
  name: '',
  description: '',
  baseUrl: '',
  method: 'GET',
  headers: [] as { key: string; value: string }[],
  requestInterval: 1000,
  timeout: 30000,
  extractionRules: [] as { name: string; method: string; selector: string; field: string; required: boolean; defaultValue: string }[],
  maxRetries: 3,
  concurrency: 1,
  enabled: true,
  userAgent: '',
  proxy: ''
})

const rules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  baseUrl: [
    { required: true, message: '请输入目标网站URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  requestInterval: [
    { required: true, message: '请输入请求间隔', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ]
}

// 添加请求头
const addHeader = () => {
  form.headers.push({ key: '', value: '' })
}

// 删除请求头
const removeHeader = (index: number) => {
  form.headers.splice(index, 1)
}

// 添加提取规则
const addRule = () => {
  form.extractionRules.push({
    name: '',
    method: 'xpath',
    selector: '',
    field: '',
    required: false,
    defaultValue: ''
  })
}

// 删除提取规则
const removeRule = (index: number) => {
  form.extractionRules.splice(index, 1)
}

// 测试配置
const handleTest = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    testing.value = true
    const success = await crawlerStore.testCrawlerConfig(form.baseUrl)
    
    if (success) {
      ElMessage.success('配置测试通过')
    }
  } catch (error) {
    console.error('Test config error:', error)
  } finally {
    testing.value = false
  }
}

// 保存配置
const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    saving.value = true
    const configId = Number(route.params.id)
    const updateParams = {
      name: form.name,
      description: form.description,
      targetUrl: form.baseUrl,
      extractionRules: form.extractionRules.map(rule => ({
        name: rule.name,
        method: rule.method as 'xpath' | 'css' | 'regex' | 'json',
        selector: rule.selector,
        field: rule.field,
        required: rule.required,
        defaultValue: rule.defaultValue
      })),
      headers: form.headers.reduce((acc, header) => {
        if (header.key && header.value) {
          acc[header.key] = header.value
        }
        return acc
      }, {} as Record<string, string>)
    }
    const success = await crawlerStore.updateCrawlerConfig(configId, updateParams)
    
    if (success) {
      ElMessage.success('配置更新成功')
      router.push('/crawler')
    }
  } catch (error) {
    console.error('Save config error:', error)
  } finally {
    saving.value = false
  }
}

// 加载配置数据
const loadConfig = async () => {
  const configId = Number(route.params.id)
  if (!configId) {
    ElMessage.error('无效的配置ID')
    router.push('/crawler')
    return
  }
  
  const config = await crawlerStore.fetchCrawlerConfigById(configId.toString())
  if (config) {
    Object.assign(form, {
      name: config.name,
      description: config.description || '',
      baseUrl: config.targetUrl,
      method: 'GET',
      headers: Object.entries(config.headers || {}).map(([key, value]) => ({ key, value })),
      requestInterval: config.rateLimit?.delayBetweenRequests || 1000,
      timeout: 30000,
      extractionRules: config.extractionRules || [],
      maxRetries: config.retryConfig?.maxRetries || 3,
      concurrency: 1,
      enabled: config.status === 'active',
      userAgent: config.userAgent || '',
      proxy: config.proxyConfig?.host || ''
    })
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.crawler-edit {
  padding: 20px;
}

.page-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.crawler-form {
  max-width: 1200px;
}

.form-section {
  margin-bottom: 20px;
}

.form-section :deep(.el-card__header) {
  padding: 15px 20px;
  background-color: #f8f9fa;
}

.form-section h3 {
  margin: 0;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.headers-config,
.extraction-rules {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.header-item,
.rule-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.header-key,
.header-value {
  flex: 1;
}

.rule-item {
  flex-direction: column;
  align-items: stretch;
}

.rule-item .el-row {
  width: 100%;
}
</style>