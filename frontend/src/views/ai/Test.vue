<template>
  <div class="ai-model-test">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" style="margin-right: 16px">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h1>测试AI模型</h1>
          <p v-if="model">测试模型：{{ model.name }}</p>
          <p v-else>测试AI模型的生成效果</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="aiStore.loading && !model" class="loading-container">
      <el-skeleton :rows="4" animated />
    </div>

    <!-- 测试界面 -->
    <div v-else-if="model" class="test-content">
      <!-- 模型信息 -->
      <el-card class="model-info-card">
        <template #header>
          <span>模型信息</span>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="模型名称">
            <span class="model-name">{{ model.name }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="模型标识">
            <el-tag>{{ model.model }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="model.is_active ? 'success' : 'danger'">
              {{ model.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 测试区域 -->
      <div class="test-area">
        <!-- 输入区域 -->
        <el-card class="input-card">
          <template #header>
            <div class="card-header">
              <span>测试输入</span>
              <el-button size="small" @click="clearInput">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </div>
          </template>
          
          <el-form :model="testForm" label-width="100px">
            <el-form-item label="测试提示词">
              <el-input
                v-model="testForm.prompt"
                type="textarea"
                :rows="6"
                placeholder="请输入要测试的提示词内容..."
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="临时参数">
              <div class="temp-params">
                <div class="param-item">
                  <label>最大令牌数:</label>
                  <el-input-number
                    v-model="testForm.max_tokens"
                    :min="1"
                    :max="8000"
                    :step="100"
                    size="small"
                    controls-position="right"
                  />
                </div>
                <div class="param-item">
                  <label>温度:</label>
                  <el-input-number
                    v-model="testForm.temperature"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    :precision="1"
                    size="small"
                    controls-position="right"
                  />
                </div>
                <div class="param-item">
                  <label>Top P:</label>
                  <el-input-number
                    v-model="testForm.top_p"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    :precision="1"
                    size="small"
                    controls-position="right"
                  />
                </div>
              </div>
              <div class="form-tip">
                这些参数仅用于本次测试，不会保存到模型配置中
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                @click="handleTest"
                :loading="testing"
                :disabled="!testForm.prompt.trim()"
              >
                <el-icon><VideoPlay /></el-icon>
                开始测试
              </el-button>
              <el-button @click="loadPresetPrompts">
                <el-icon><Document /></el-icon>
                加载预设提示词
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 输出区域 -->
        <el-card class="output-card">
          <template #header>
            <div class="card-header">
              <span>测试结果</span>
              <div v-if="testResult">
                <el-button size="small" @click="copyResult">
                  <el-icon><DocumentCopy /></el-icon>
                  复制结果
                </el-button>
                <el-button size="small" @click="clearResult">
                  <el-icon><Delete /></el-icon>
                  清空结果
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 测试中状态 -->
          <div v-if="testing" class="testing-status">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在生成内容，请稍候...</span>
          </div>
          
          <!-- 测试结果 -->
          <div v-else-if="testResult" class="test-result">
            <div class="result-content">
              <pre>{{ testResult.content }}</pre>
            </div>
            
            <div class="result-meta">
              <el-descriptions :column="4" size="small">
                <el-descriptions-item label="生成时间">
                  {{ testResult.duration }}ms
                </el-descriptions-item>
                <el-descriptions-item label="输入令牌">
                  {{ testResult.input_tokens || 'N/A' }}
                </el-descriptions-item>
                <el-descriptions-item label="输出令牌">
                  {{ testResult.output_tokens || 'N/A' }}
                </el-descriptions-item>
                <el-descriptions-item label="总令牌">
                  {{ testResult.total_tokens || 'N/A' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          
          <!-- 错误信息 -->
          <div v-else-if="testError" class="test-error">
            <el-alert
              :title="testError.title || '测试失败'"
              :description="testError.message"
              type="error"
              show-icon
              :closable="false"
            />
          </div>
          
          <!-- 空状态 -->
          <el-empty v-else description="暂无测试结果" />
        </el-card>
      </div>

      <!-- 测试历史 -->
      <el-card v-if="testHistory.length > 0" class="history-card">
        <template #header>
          <div class="card-header">
            <span>测试历史</span>
            <el-button size="small" @click="clearHistory">
              <el-icon><Delete /></el-icon>
              清空历史
            </el-button>
          </div>
        </template>
        
        <div class="history-list">
          <div
            v-for="(item, index) in testHistory"
            :key="index"
            class="history-item"
            @click="loadHistoryItem(item)"
          >
            <div class="history-prompt">
              {{ item.prompt.substring(0, 100) }}{{ item.prompt.length > 100 ? '...' : '' }}
            </div>
            <div class="history-meta">
              <span>{{ formatDate(item.timestamp) }}</span>
              <span>{{ item.duration }}ms</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 未找到模型 -->
    <el-empty v-else description="未找到该模型" />

    <!-- 预设提示词对话框 -->
    <el-dialog
      v-model="showPresetDialog"
      title="选择预设提示词"
      width="600px"
    >
      <div class="preset-list">
        <div
          v-for="(preset, index) in presetPrompts"
          :key="index"
          class="preset-item"
          @click="selectPreset(preset)"
        >
          <div class="preset-title">{{ preset.title }}</div>
          <div class="preset-content">{{ preset.content }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  VideoPlay,
  Delete,
  Document,
  DocumentCopy,
  Loading
} from '@element-plus/icons-vue'
import { useAIStore } from '@/stores/ai'
import { formatDate } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const aiStore = useAIStore()

const modelId = computed(() => route.params.id as string)

// 获取当前模型
const model = computed(() => {
  if (!modelId.value) return null
  return aiStore.aiModels.find(m => m.id?.toString() === modelId.value)
})

// 测试表单
const testForm = reactive({
  prompt: '',
  max_tokens: 1000,
  temperature: 0.7,
  top_p: 1.0
})

// 测试状态
const testing = ref(false)
const testResult = ref<any>(null)
const testError = ref<any>(null)

// 测试历史
const testHistory = ref<any[]>([])

// 预设提示词
const showPresetDialog = ref(false)
const presetPrompts = ref([
  {
    title: '文章摘要',
    content: '请为以下文章生成一个简洁的摘要，突出主要观点和关键信息：\n\n[在此处粘贴文章内容]'
  },
  {
    title: '创意写作',
    content: '请写一个关于未来科技的短故事，要求：\n1. 故事长度约500字\n2. 包含人工智能元素\n3. 有积极向上的结局'
  },
  {
    title: '代码解释',
    content: '请解释以下代码的功能和工作原理：\n\n```\n[在此处粘贴代码]\n```\n\n请用通俗易懂的语言解释。'
  },
  {
    title: '问题解答',
    content: '请详细回答以下问题，要求逻辑清晰、条理分明：\n\n[在此处输入问题]'
  }
])

// 返回列表
const handleBack = () => {
  router.push('/ai')
}

// 清空输入
const clearInput = () => {
  testForm.prompt = ''
}

// 清空结果
const clearResult = () => {
  testResult.value = null
  testError.value = null
}

// 复制结果
const copyResult = async () => {
  if (!testResult.value?.content) return
  
  try {
    await navigator.clipboard.writeText(testResult.value.content)
    ElMessage.success('复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 执行测试
const handleTest = async () => {
  if (!model.value?.id || !testForm.prompt.trim()) return
  
  testing.value = true
  testResult.value = null
  testError.value = null
  
  const startTime = Date.now()
  
  try {
    const result = await aiStore.testAIModel(model.value.id, testForm.prompt)
    
    const duration = Date.now() - startTime
    
    testResult.value = {
      content: result.content,
      duration,
      input_tokens: result.usage?.input_tokens,
      output_tokens: result.usage?.output_tokens,
      total_tokens: result.usage?.total_tokens
    }
    
    // 添加到历史记录
    testHistory.value.unshift({
      prompt: testForm.prompt,
      result: testResult.value.content,
      duration,
      timestamp: new Date()
    })
    
    // 限制历史记录数量
    if (testHistory.value.length > 10) {
      testHistory.value = testHistory.value.slice(0, 10)
    }
    
    ElMessage.success('测试完成')
  } catch (error: any) {
    testError.value = {
      title: '测试失败',
      message: error.message || '未知错误'
    }
    ElMessage.error('测试失败')
    console.error('AI模型测试失败:', error)
  } finally {
    testing.value = false
  }
}

// 加载预设提示词
const loadPresetPrompts = () => {
  showPresetDialog.value = true
}

// 选择预设提示词
const selectPreset = (preset: any) => {
  testForm.prompt = preset.content
  showPresetDialog.value = false
}

// 清空历史
const clearHistory = () => {
  testHistory.value = []
}

// 加载历史项目
const loadHistoryItem = (item: any) => {
  testForm.prompt = item.prompt
  testResult.value = {
    content: item.result,
    duration: item.duration
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  try {
    // 如果store中没有数据，先加载
    if (aiStore.aiModels.length === 0) {
      await aiStore.fetchAIModels()
    }
    
    // 检查是否找到模型
    if (!model.value) {
      ElMessage.error('未找到指定的模型')
      router.push('/ai')
      return
    }
    
    // 初始化测试参数
    if (model.value.generation_config) {
      testForm.max_tokens = model.value.generation_config.max_tokens || 1000
      testForm.temperature = model.value.generation_config.temperature || 0.7
      testForm.top_p = model.value.generation_config.top_p || 1.0
    }
  } catch (error) {
    ElMessage.error('加载模型信息失败')
    console.error('加载模型信息失败:', error)
  }
})
</script>

<style scoped>
.ai-model-test {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left h1 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 24px;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.loading-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.model-info-card,
.input-card,
.output-card,
.history-card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-name {
  font-weight: 600;
  color: #303133;
}

.test-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 1200px) {
  .test-area {
    grid-template-columns: 1fr;
  }
}

.temp-params {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-item label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.testing-status {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #409eff;
  font-size: 16px;
}

.testing-status .el-icon {
  margin-right: 8px;
  font-size: 20px;
}

.test-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-content {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.result-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #495057;
}

.result-meta {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.test-error {
  padding: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.history-prompt {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.preset-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.preset-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.preset-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.preset-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

:deep(.el-input-number) {
  width: 120px;
}
</style>