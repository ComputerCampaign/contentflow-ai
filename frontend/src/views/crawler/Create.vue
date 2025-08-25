<template>
  <div class="crawler-create">
    <PageHeader title="创建爬虫配置" description="配置新的网页爬虫任务">
      <template #actions>
        <el-button @click="handleBack">返回</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          创建配置
        </el-button>
      </template>
    </PageHeader>

    <div class="crawler-create-content">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        size="default"
      >
        <el-card class="form-section">
          <template #header>
            <span class="section-title">基本信息</span>
          </template>
          
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
              <el-form-item label="目标网站" prop="url">
                <el-input
                  v-model="formData.url"
                  placeholder="请输入目标网站URL"
                  type="url"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="配置描述" prop="description">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="3"
              placeholder="请输入配置描述"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="配置类型" prop="type">
                <el-select v-model="formData.type" placeholder="请选择类型">
                  <el-option label="网页爬虫" value="web" />
                  <el-option label="API接口" value="api" />
                  <el-option label="RSS订阅" value="rss" />
                  <el-option label="站点地图" value="sitemap" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-radio-group v-model="formData.status">
                  <el-radio label="active">启用</el-radio>
                  <el-radio label="inactive">禁用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="form-section">
          <template #header>
            <span class="section-title">请求配置</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="请求方法" prop="method">
                <el-select v-model="formData.method" placeholder="选择请求方法">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="超时时间" prop="timeout">
                <el-input-number
                  v-model="formData.timeout"
                  :min="1"
                  :max="300"
                  placeholder="秒"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="重试次数" prop="retryCount">
                <el-input-number
                  v-model="formData.retryCount"
                  :min="0"
                  :max="10"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="请求头" prop="headers">
            <div class="headers-container">
              <div
                v-for="(header, index) in formData.headers"
                :key="index"
                class="header-item"
              >
                <el-input
                  v-model="header.key"
                  placeholder="Header名称"
                  style="width: 200px; margin-right: 10px"
                />
                <el-input
                  v-model="header.value"
                  placeholder="Header值"
                  style="width: 300px; margin-right: 10px"
                />
                <el-button
                  type="danger"
                  size="small"
                  @click="removeHeader(index)"
                  :disabled="formData.headers.length <= 1"
                >
                  删除
                </el-button>
              </div>
              <el-button type="primary" size="small" @click="addHeader">
                添加Header
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="请求参数" prop="params" v-if="formData.method !== 'GET'">
            <el-input
              v-model="formData.params"
              type="textarea"
              :rows="4"
              placeholder="请输入JSON格式的请求参数"
            />
          </el-form-item>
        </el-card>

        <el-card class="form-section">
          <template #header>
            <span class="section-title">数据提取配置</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="数据格式" prop="dataFormat">
                <el-select v-model="formData.dataFormat" placeholder="选择数据格式">
                  <el-option label="JSON" value="json" />
                  <el-option label="HTML" value="html" />
                  <el-option label="XML" value="xml" />
                  <el-option label="文本" value="text" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="编码格式" prop="encoding">
                <el-select v-model="formData.encoding" placeholder="选择编码格式">
                  <el-option label="UTF-8" value="utf-8" />
                  <el-option label="GBK" value="gbk" />
                  <el-option label="GB2312" value="gb2312" />
                  <el-option label="自动检测" value="auto" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="XPath规则" prop="xpathRules">
            <div class="xpath-container">
              <div
                v-for="(rule, index) in formData.xpathRules"
                :key="index"
                class="xpath-item"
              >
                <el-input
                  v-model="rule.name"
                  placeholder="字段名称"
                  style="width: 150px; margin-right: 10px"
                />
                <el-input
                  v-model="rule.xpath"
                  placeholder="XPath表达式"
                  style="width: 300px; margin-right: 10px"
                />
                <el-select
                  v-model="rule.type"
                  placeholder="数据类型"
                  style="width: 100px; margin-right: 10px"
                >
                  <el-option label="文本" value="text" />
                  <el-option label="链接" value="link" />
                  <el-option label="图片" value="image" />
                  <el-option label="数字" value="number" />
                </el-select>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeXPathRule(index)"
                  :disabled="formData.xpathRules.length <= 1"
                >
                  删除
                </el-button>
              </div>
              <el-button type="primary" size="small" @click="addXPathRule">
                添加规则
              </el-button>
            </div>
          </el-form-item>
        </el-card>

        <el-card class="form-section">
          <template #header>
            <span class="section-title">高级设置</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="请求间隔" prop="delay">
                <el-input-number
                  v-model="formData.delay"
                  :min="100"
                  :max="10000"
                  placeholder="毫秒"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="并发数" prop="concurrency">
                <el-input-number
                  v-model="formData.concurrency"
                  :min="1"
                  :max="10"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="User-Agent" prop="userAgent">
                <el-select v-model="formData.userAgent" placeholder="选择User-Agent">
                  <el-option label="Chrome" value="chrome" />
                  <el-option label="Firefox" value="firefox" />
                  <el-option label="Safari" value="safari" />
                  <el-option label="自定义" value="custom" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item>
                <el-checkbox v-model="formData.enableProxy">启用代理</el-checkbox>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <el-checkbox v-model="formData.enableCookies">启用Cookies</el-checkbox>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="代理设置" prop="proxyConfig" v-if="formData.enableProxy">
            <el-input
              v-model="formData.proxyConfig"
              placeholder="代理服务器地址，格式：http://proxy:port"
            />
          </el-form-item>

          <el-form-item label="自定义UA" prop="customUserAgent" v-if="formData.userAgent === 'custom'">
            <el-input
              v-model="formData.customUserAgent"
              placeholder="请输入自定义User-Agent"
            />
          </el-form-item>
        </el-card>

        <div class="form-actions">
          <el-button @click="handleTest" :loading="testLoading">
            测试配置
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            创建配置
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { useCrawlerStore } from '@/stores/crawler'

const router = useRouter()
const crawlerStore = useCrawlerStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const testLoading = ref(false)

const formData = reactive({
  name: '',
  url: '',
  description: '',
  type: 'web',
  status: 'active',
  method: 'GET',
  timeout: 30,
  retryCount: 3,
  headers: [{ key: 'User-Agent', value: 'Mozilla/5.0 (compatible; WebCrawler/1.0)' }],
  params: '',
  dataFormat: 'html',
  encoding: 'utf-8',
  xpathRules: [{ name: 'title', xpath: '//title/text()', type: 'text' }],
  delay: 1000,
  concurrency: 1,
  userAgent: 'chrome',
  customUserAgent: '',
  enableProxy: false,
  enableCookies: true,
  proxyConfig: ''
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入目标网站URL', trigger: 'blur' },
    { 
      pattern: /^https?:\/\/.+/,
      message: '请输入有效的URL地址',
      trigger: 'blur'
    }
  ],
  type: [
    { required: true, message: '请选择配置类型', trigger: 'change' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  dataFormat: [
    { required: true, message: '请选择数据格式', trigger: 'change' }
  ],
  encoding: [
    { required: true, message: '请选择编码格式', trigger: 'change' }
  ]
}

const addHeader = () => {
  formData.headers.push({ key: '', value: '' })
}

const removeHeader = (index: number) => {
  formData.headers.splice(index, 1)
}

const addXPathRule = () => {
  formData.xpathRules.push({ name: '', xpath: '', type: 'text' })
}

const removeXPathRule = (index: number) => {
  formData.xpathRules.splice(index, 1)
}

const handleBack = () => {
  router.push('/crawler/list')
}

const handleReset = () => {
  formRef.value?.resetFields()
}

const handleTest = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    testLoading.value = true
    
    // 测试爬虫配置
    await crawlerStore.testCrawlerConfig(formData.url)
    ElMessage.success('配置测试成功')
  } catch (error) {
    console.error('测试配置失败:', error)
    ElMessage.error('配置测试失败，请检查配置参数')
  } finally {
    testLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 转换表单数据为后端API格式
    const createParams = {
      name: formData.name,
      description: formData.description,
      type: formData.type as 'web' | 'api' | 'rss' | 'sitemap',
      targetUrl: formData.url,
      extractionRules: formData.xpathRules.map((rule: any) => ({
        name: rule.name,
        method: 'xpath' as 'xpath' | 'css' | 'regex' | 'json',
        selector: rule.xpath || '',
        field: 'text',
        required: false,
        defaultValue: ''
      }))
    }
    
    // 创建爬虫配置
    await crawlerStore.createCrawlerConfig(createParams)
    ElMessage.success('爬虫配置创建成功')
    router.push('/crawler/list')
  } catch (error) {
    console.error('创建配置失败:', error)
    ElMessage.error('创建配置失败')
  } finally {
    loading.value = false
  }
}

const getUserAgentString = (type: string) => {
  const userAgents = {
    chrome: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    firefox: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
  }
  return userAgents[type as keyof typeof userAgents] || userAgents.chrome
}
</script>

<style scoped lang="scss">
.crawler-create {
  padding: 20px;
  
  &-content {
    margin-top: 20px;
  }
}

.form-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.headers-container,
.xpath-container {
  .header-item,
  .xpath-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
}

.form-actions {
  text-align: center;
  padding: 20px 0;
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 20px;
  
  .el-button {
    margin: 0 10px;
  }
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>