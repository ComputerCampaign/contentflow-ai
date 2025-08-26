<template>
  <div class="xpath-test">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
            <h2>XPath测试工具</h2>
          </div>
          <div class="header-actions">
            <el-button @click="clearAll" :icon="Delete">清空</el-button>
            <el-button @click="loadFromConfig" :icon="DocumentCopy">从配置加载</el-button>
          </div>
        </div>
      </template>

      <div class="test-content">
        <!-- 测试表单 -->
        <el-form
          ref="formRef"
          :model="testForm"
          :rules="rules"
          label-width="120px"
          class="test-form"
        >
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="测试URL" prop="url">
                <div class="url-input-group">
                  <el-input
                    v-model="testForm.url"
                    placeholder="请输入要测试的URL，例如：https://example.com"
                    class="url-input"
                  />
                  <el-button @click="fetchPageContent" :loading="fetchLoading">
                    获取页面
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="16">
              <el-form-item label="XPath表达式" prop="xpath">
                <el-input
                  v-model="testForm.xpath"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入XPath表达式，例如：//div[@class='content']//text()"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="提取类型" prop="extractType">
                <el-select v-model="testForm.extractType" placeholder="选择类型">
                  <el-option label="文本" value="text" />
                  <el-option label="HTML" value="html" />
                  <el-option label="属性" value="attr" />
                  <el-option label="链接" value="href" />
                </el-select>
              </el-form-item>
              
              <el-form-item 
                v-if="testForm.extractType === 'attr'" 
                label="属性名称" 
                prop="attrName"
              >
                <el-input
                  v-model="testForm.attrName"
                  placeholder="例如：href, src"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="数据处理">
                <el-checkbox-group v-model="testForm.processing">
                  <el-checkbox label="trim">去除首尾空格</el-checkbox>
                  <el-checkbox label="lowercase">转换为小写</el-checkbox>
                  <el-checkbox label="uppercase">转换为大写</el-checkbox>
                  <el-checkbox label="removeHtml">移除HTML标签</el-checkbox>
                  <el-checkbox label="removeNewlines">移除换行符</el-checkbox>
                  <el-checkbox label="unique">去重</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
          </el-row>

          <div class="test-actions">
            <el-button 
              type="primary" 
              @click="runTest" 
              :loading="testLoading"
              :disabled="!testForm.url || !testForm.xpath"
              size="large"
            >
              <el-icon><VideoPlay /></el-icon>
              开始测试
            </el-button>
            <el-button @click="saveAsConfig" :disabled="!hasValidResult">
              <el-icon><DocumentAdd /></el-icon>
              保存为配置
            </el-button>
          </div>
        </el-form>

        <!-- 测试结果 -->
        <div v-if="testResult" class="test-result">
          <el-card>
            <template #header>
              <div class="result-header">
                <h3>测试结果</h3>
                <div class="result-stats">
                  <el-tag v-if="testResult.success" type="success">
                    成功提取 {{ testResult.count || 0 }} 个结果
                  </el-tag>
                  <el-tag v-else type="danger">
                    测试失败
                  </el-tag>
                  <span class="test-time">耗时: {{ testResult.duration || 0 }}ms</span>
                </div>
              </div>
            </template>

            <div v-if="testResult.success" class="result-content">
              <div class="result-actions">
                <el-button size="small" @click="copyResult">
                  <el-icon><DocumentCopy /></el-icon>
                  复制结果
                </el-button>
                <el-button size="small" @click="downloadResult">
                  <el-icon><Download /></el-icon>
                  下载结果
                </el-button>
              </div>
              
              <el-input
                v-model="testResult.data"
                type="textarea"
                :rows="12"
                readonly
                class="result-textarea"
              />
            </div>
            
            <div v-else class="error-content">
              <el-alert
                title="测试失败"
                type="error"
                :description="testResult.error"
                show-icon
              />
            </div>
          </el-card>
        </div>

        <!-- 页面内容预览 -->
        <div v-if="pageContent" class="page-preview">
          <el-card>
            <template #header>
              <div class="preview-header">
                <h3>页面内容预览</h3>
                <el-button size="small" @click="pageContent = ''">
                  <el-icon><Close /></el-icon>
                  关闭预览
                </el-button>
              </div>
            </template>
            
            <el-input
              v-model="pageContent"
              type="textarea"
              :rows="8"
              readonly
              class="preview-textarea"
            />
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 保存配置对话框 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="保存为配置"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="saveForm" label-width="100px">
        <el-form-item label="配置名称" required>
          <el-input v-model="saveForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="saveForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSave" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 加载配置对话框 -->
    <el-dialog
      v-model="loadDialogVisible"
      title="选择配置"
      width="600px"
    >
      <el-table :data="configList" @row-click="selectConfig">
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="xpath" label="XPath表达式" show-overflow-tooltip />
        <el-table-column prop="extractType" label="提取类型">
          <template #default="{ row }">
            <el-tag size="small">{{ getExtractTypeText(row.extractType) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="loadDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  ArrowLeft,
  Delete,
  DocumentCopy,
  VideoPlay,
  DocumentAdd,
  Download,
  Close
} from '@element-plus/icons-vue'
import { useXPathStore } from '@/stores/xpath'
import type { XPathConfig } from '@/stores/xpath'

const router = useRouter()
const xpathStore = useXPathStore()

const formRef = ref<FormInstance>()
const testLoading = ref(false)
const fetchLoading = ref(false)
const saveLoading = ref(false)
const saveDialogVisible = ref(false)
const loadDialogVisible = ref(false)
const testResult = ref<any>(null)
const pageContent = ref('')
const configList = ref<XPathConfig[]>([])

// 测试表单
const testForm = reactive({
  url: '',
  xpath: '',
  extractType: 'text',
  attrName: '',
  processing: ['trim']
})

// 保存表单
const saveForm = reactive({
  name: '',
  description: ''
})

// 表单验证规则
const rules: FormRules = {
  url: [
    { required: true, message: '请输入测试URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  xpath: [
    { required: true, message: '请输入XPath表达式', trigger: 'blur' }
  ],
  extractType: [
    { required: true, message: '请选择提取类型', trigger: 'change' }
  ],
  attrName: [
    {
      validator: (rule, value, callback) => {
        if (testForm.extractType === 'attr' && !value) {
          callback(new Error('选择属性提取时必须输入属性名称'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 是否有有效结果
const hasValidResult = computed(() => {
  return testResult.value && testResult.value.success && testResult.value.data
})

// 获取提取类型文本
const getExtractTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    text: '文本',
    html: 'HTML',
    attr: '属性',
    href: '链接'
  }
  return textMap[type] || type
}

// 返回
const goBack = () => {
  router.push('/xpath')
}

// 清空所有
const clearAll = () => {
  testForm.url = ''
  testForm.xpath = ''
  testForm.extractType = 'text'
  testForm.attrName = ''
  testForm.processing = ['trim']
  testResult.value = null
  pageContent.value = ''
}

// 获取页面内容
const fetchPageContent = async () => {
  if (!testForm.url) {
    ElMessage.warning('请输入URL')
    return
  }
  
  try {
    fetchLoading.value = true
    // 这里应该调用API获取页面内容
    // const content = await api.fetchPageContent(testForm.url)
    // pageContent.value = content
    ElMessage.info('页面内容获取功能需要后端支持')
  } catch (error) {
    console.error('Fetch page error:', error)
    ElMessage.error('获取页面内容失败')
  } finally {
    fetchLoading.value = false
  }
}

// 运行测试
const runTest = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    testLoading.value = true
    const startTime = Date.now()
    
    const result = await xpathStore.testXPath({
      url: testForm.url,
      xpath: testForm.xpath,
      extractType: testForm.extractType as 'text' | 'html' | 'attr' | 'href',
      attrName: testForm.attrName,
      processing: testForm.processing
    })
    
    const duration = Date.now() - startTime
    testResult.value = {
      ...result,
      duration
    }
    
    if (result.success) {
      ElMessage.success(`测试完成，提取到 ${result.count || 0} 个结果`)
    } else {
      ElMessage.error('测试失败')
    }
  } catch (error) {
    console.error('Test error:', error)
    testResult.value = {
      success: false,
      error: '测试过程中发生错误',
      duration: 0
    }
    ElMessage.error('测试失败')
  } finally {
    testLoading.value = false
  }
}

// 复制结果
const copyResult = async () => {
  if (testResult.value?.data) {
    try {
      await navigator.clipboard.writeText(testResult.value.data)
      ElMessage.success('结果已复制到剪贴板')
    } catch (error) {
      console.error('Copy error:', error)
      ElMessage.error('复制失败')
    }
  }
}

// 下载结果
const downloadResult = () => {
  if (testResult.value?.data) {
    const blob = new Blob([testResult.value.data], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `xpath-test-result-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('结果已下载')
  }
}

// 保存为配置
const saveAsConfig = () => {
  if (!hasValidResult.value) {
    ElMessage.warning('请先进行成功的测试')
    return
  }
  
  saveForm.name = ''
  saveForm.description = ''
  saveDialogVisible.value = true
}

// 确认保存
const confirmSave = async () => {
  if (!saveForm.name) {
    ElMessage.warning('请输入配置名称')
    return
  }
  
  try {
    saveLoading.value = true
    
    const configData = {
      name: saveForm.name,
      description: saveForm.description,
      xpath: testForm.xpath,
      extractType: testForm.extractType,
      attrName: testForm.attrName,
      processing: testForm.processing,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      usageCount: 0,
      usage_count: 0, // 补充 usage_count 属性
      // 补充 XPathConfig 接口中缺失的属性
      id: '', // 假设后端会生成，这里给个空字符串或临时值
      rule_id: '', // 假设后端会生成
      config_id: '', // 假设后端会生成
      field_name: saveForm.name, // 使用名称作为字段名
      rule_type: testForm.extractType, // 假设 rule_type 和 extractType 相同
      enabled: true, // 默认启用
      domain_patterns: [], // 默认空数组
      is_public: false, // 默认不公开
      user_id: '', // 假设后端会从会话中获取
      last_used_at: null, // 默认null
      created_at: new Date().toISOString(), // 补充 created_at
      updated_at: new Date().toISOString() // 补充 updated_at
    } as XPathConfig
    
    const success = await xpathStore.createXPathConfig(configData)
    
    if (success) {
      ElMessage.success('配置保存成功')
      saveDialogVisible.value = false
    }
  } catch (error) {
    console.error('Save config error:', error)
    ElMessage.error('保存配置失败')
  } finally {
    saveLoading.value = false
  }
}

// 从配置加载
const loadFromConfig = async () => {
  try {
    await xpathStore.fetchXPathConfigs()
    configList.value = xpathStore.xpathConfigs
    loadDialogVisible.value = true
  } catch (error) {
    console.error('Load configs error:', error)
    ElMessage.error('加载配置列表失败')
  }
}

// 选择配置
const selectConfig = (config: XPathConfig) => {
  testForm.xpath = config.xpath
  testForm.extractType = config.extractType
  testForm.attrName = config.attrName || ''
  testForm.processing = config.processing || ['trim']
  loadDialogVisible.value = false
  ElMessage.success(`已加载配置: ${config.name}`)
}

onMounted(() => {
  // 初始化时可以加载一些示例数据
})
</script>

<style scoped>
.xpath-test {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.test-content {
  padding: 20px 0;
}

.test-form {
  margin-bottom: 30px;
}

.url-input-group {
  display: flex;
  gap: 10px;
}

.url-input {
  flex: 1;
}

.test-actions {
  margin: 30px 0;
  text-align: center;
}

.test-actions .el-button {
  margin: 0 10px;
}

.test-result {
  margin: 30px 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h3 {
  margin: 0;
  color: #303133;
}

.result-stats {
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-time {
  font-size: 12px;
  color: #909399;
}

.result-content {
  padding: 20px 0;
}

.result-actions {
  margin-bottom: 15px;
  text-align: right;
}

.result-textarea {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.error-content {
  padding: 20px 0;
}

.page-preview {
  margin: 30px 0;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  margin: 0;
  color: #303133;
}

.preview-textarea {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

:deep(.el-checkbox) {
  margin-right: 0;
}
</style>