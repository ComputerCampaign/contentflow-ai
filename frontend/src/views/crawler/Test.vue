<template>
  <div class="crawler-test">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>爬虫配置测试</h2>
          <div class="header-actions">
            <el-button @click="handleReset">重置</el-button>
            <el-button type="primary" @click="handleTest" :loading="testing">开始测试</el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="test-form"
      >
        <!-- 基本配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>基本配置</h3>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="目标URL" prop="url">
                <el-input v-model="form.url" placeholder="请输入要测试的URL" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="请求方法" prop="method">
                <el-select v-model="form.method" placeholder="选择请求方法">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="User-Agent">
            <el-input
              v-model="form.userAgent"
              placeholder="自定义User-Agent（可选）"
            />
          </el-form-item>
        </el-card>

        <!-- XPath测试 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>XPath表达式测试</h3>
          </template>
          
          <el-form-item label="XPath表达式" prop="xpath">
            <el-input
              v-model="form.xpath"
              type="textarea"
              :rows="3"
              placeholder="请输入要测试的XPath表达式"
            />
          </el-form-item>
          
          <el-form-item label="提取类型">
            <el-radio-group v-model="form.extractType">
              <el-radio label="text">文本内容</el-radio>
              <el-radio label="html">HTML内容</el-radio>
              <el-radio label="attr">属性值</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item v-if="form.extractType === 'attr'" label="属性名称">
            <el-input v-model="form.attrName" placeholder="请输入属性名称" />
          </el-form-item>
        </el-card>
      </el-form>
    </el-card>

    <!-- 测试结果 -->
    <el-card v-if="testResult" class="result-card">
      <template #header>
        <h3>测试结果</h3>
      </template>
      
      <div class="result-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="请求状态">
            <el-tag :type="testResult.success ? 'success' : 'danger'">
              {{ testResult.success ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应时间">
            {{ testResult.responseTime }}ms
          </el-descriptions-item>
          <el-descriptions-item label="状态码">
            {{ testResult.statusCode }}
          </el-descriptions-item>
          <el-descriptions-item label="内容长度">
            {{ testResult.contentLength }} 字符
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="testResult.error" class="error-message">
          <h4>错误信息：</h4>
          <el-alert :title="testResult.error" type="error" show-icon />
        </div>
        
        <div v-if="testResult.extractedData" class="extracted-data">
          <h4>提取结果：</h4>
          <el-input
            v-model="testResult.extractedData"
            type="textarea"
            :rows="6"
            readonly
            class="result-textarea"
          />
        </div>
        
        <div v-if="testResult.htmlPreview" class="html-preview">
          <h4>页面预览：</h4>
          <div class="preview-container">
            <iframe
              :srcdoc="testResult.htmlPreview"
              class="preview-iframe"
              sandbox="allow-same-origin"
            ></iframe>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { useCrawlerStore } from '@/stores/crawler'

const crawlerStore = useCrawlerStore()

const formRef = ref<FormInstance>()
const testing = ref(false)

const form = reactive({
  url: '',
  method: 'GET',
  userAgent: '',
  xpath: '',
  extractType: 'text',
  attrName: ''
})

const testResult = ref<any>(null)

const rules = {
  url: [
    { required: true, message: '请输入目标URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  xpath: [
    { required: true, message: '请输入XPath表达式', trigger: 'blur' }
  ]
}

// 开始测试
const handleTest = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    testing.value = true
    testResult.value = null
    
    const testConfig = {
      url: form.url,
      method: form.method,
      userAgent: form.userAgent,
      xpath: form.xpath,
      extractType: form.extractType,
      attrName: form.attrName
    }
    
    const result = await crawlerStore.testXPath(form.url, form.xpath)
    testResult.value = result
    
    if (result.success) {
      ElMessage.success('测试完成')
    } else {
      ElMessage.error('测试失败：' + result.error)
    }
  } catch (error) {
    console.error('Test error:', error)
    ElMessage.error('测试过程中发生错误')
  } finally {
    testing.value = false
  }
}

// 重置表单
const handleReset = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  testResult.value = null
  Object.assign(form, {
    url: '',
    method: 'GET',
    userAgent: '',
    xpath: '',
    extractType: 'text',
    attrName: ''
  })
}
</script>

<style scoped>
.crawler-test {
  padding: 20px;
}

.page-card,
.result-card {
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

.test-form {
  max-width: 1000px;
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

.result-content {
  padding: 20px 0;
}

.error-message,
.extracted-data,
.html-preview {
  margin-top: 20px;
}

.error-message h4,
.extracted-data h4,
.html-preview h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.result-textarea {
  font-family: 'Courier New', monospace;
}

.preview-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 400px;
  border: none;
}
</style>