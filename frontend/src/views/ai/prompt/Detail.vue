<template>
  <div class="prompt-detail">
    <el-card class="page-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>提示词详情</h2>
          <div class="header-actions">
            <el-button @click="handleBack">返回</el-button>
            <el-button type="primary" @click="handleEdit">
              编辑
            </el-button>
          </div>
        </div>
      </template>

      <div class="detail-content" v-if="promptData">
        <!-- 基本信息 -->
        <el-card class="detail-section">
          <template #header>
            <span class="section-title">基本信息</span>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="提示词名称">
              {{ promptData.name }}
            </el-descriptions-item>
            <el-descriptions-item label="提示词标识">
              <el-tag type="info">{{ promptData.key }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="promptData.status === 'active' ? 'success' : 'info'">
                {{ promptData.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="默认提示词">
              <el-tag v-if="promptData.is_default" type="warning">是</el-tag>
              <span v-else>否</span>
            </el-descriptions-item>
            <el-descriptions-item label="使用次数" :span="2">
              <el-badge :value="promptData.usage_count || 0" :max="999" />
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 提示词配置 -->
        <el-card class="detail-section">
          <template #header>
            <span class="section-title">提示词配置</span>
          </template>
          
          <div class="config-item">
            <h4>系统提示词</h4>
            <div class="config-content">
              <pre v-if="promptData.system">{{ promptData.system }}</pre>
              <el-text v-else type="info">未设置</el-text>
            </div>
          </div>
          
          <div class="config-item">
            <h4>用户模板</h4>
            <div class="config-content">
              <pre v-if="promptData.user_template">{{ promptData.user_template }}</pre>
              <el-text v-else type="info">未设置</el-text>
            </div>
            <div class="template-help" v-if="promptData.user_template">
              <el-text type="info" size="small">
                支持的变量：{title} - 标题，{description} - 描述，{images} - 图片信息，{comments} - 评论信息
              </el-text>
            </div>
          </div>
        </el-card>

        <!-- 测试配置 -->
        <el-card class="detail-section">
          <template #header>
            <div class="section-header">
              <span class="section-title">测试配置</span>
              <el-button size="small" type="primary" @click="handleTest" :loading="testing">
                测试提示词
              </el-button>
            </div>
          </template>
          
          <div class="test-section">
            <div class="test-input">
              <h4>测试数据</h4>
              <el-input
                v-model="testData"
                type="textarea"
                :rows="4"
                placeholder="请输入测试数据（JSON格式），例如：{&quot;title&quot;: &quot;测试标题&quot;, &quot;description&quot;: &quot;测试描述&quot;}"
              />
            </div>
            
            <div class="test-result" v-if="testResult">
              <h4>测试结果</h4>
              <div class="result-content">
                <pre>{{ testResult }}</pre>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAIStore } from '@/stores/ai'

const router = useRouter()
const route = useRoute()
const aiStore = useAIStore()

const loading = ref(false)
const testing = ref(false)
const testData = ref('')
const testResult = ref('')
const promptData = ref<any>(null)

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    const key = route.params.key as string
    if (!key) {
      ElMessage.error('参数错误')
      router.push('/ai')
      return
    }
    
    await aiStore.fetchPromptsConfig()
    
    const prompt = aiStore.promptsConfig.prompts[key]
    if (!prompt) {
      ElMessage.error('提示词不存在')
      router.push('/ai')
      return
    }
    
    promptData.value = {
      key,
      name: key,
      system: prompt.system || '',
      user_template: prompt.user_template || '',
      status: 'active', // 默认状态
      usage_count: 0, // 默认使用次数
      is_default: aiStore.promptsConfig.default_prompt === key
    }
    
  } catch (error) {
    console.error('Load data error:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 返回
const handleBack = () => {
  router.push('/ai')
}

// 编辑
const handleEdit = () => {
  router.push(`/ai/prompt/edit/${promptData.value.key}`)
}

// 测试提示词
const handleTest = async () => {
  if (!promptData.value.system || !promptData.value.user_template) {
    ElMessage.warning('系统提示词和用户模板不能为空')
    return
  }
  
  try {
    testing.value = true
    
    let testDataObj = {}
    if (testData.value) {
      try {
        testDataObj = JSON.parse(testData.value)
      } catch (e) {
        ElMessage.error('测试数据格式错误，请输入有效的JSON格式')
        return
      }
    }
    
    // 替换模板中的变量
    let processedTemplate = promptData.value.user_template
    Object.entries(testDataObj).forEach(([key, value]) => {
      const regex = new RegExp(`\\{${key}\\}`, 'g')
      processedTemplate = processedTemplate.replace(regex, String(value))
    })
    
    testResult.value = `系统提示词：\n${promptData.value.system}\n\n用户提示词：\n${processedTemplate}`
    
    ElMessage.success('测试完成')
    
  } catch (error) {
    console.error('Test error:', error)
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.prompt-detail {
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

.card-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.detail-content {
  max-width: 800px;
}

.detail-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 600;
  color: #303133;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.config-item {
  margin-bottom: 20px;
}

.config-item:last-child {
  margin-bottom: 0;
}

.config-item h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.config-content {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  min-height: 60px;
}

.config-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #303133;
}

.template-help {
  margin-top: 8px;
}

.test-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-input h4,
.test-result h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.result-content {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.result-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #303133;
}
</style>