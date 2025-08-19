<template>
  <div class="ai-model-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" style="margin-right: 16px">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h1>{{ model?.name || 'AI模型详情' }}</h1>
          <p>查看AI模型的详细配置信息</p>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="handleTest" type="success">
          <el-icon><VideoPlay /></el-icon>
          测试模型
        </el-button>
        <el-button @click="handleEdit" type="primary">
          <el-icon><Edit /></el-icon>
          编辑模型
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="aiStore.loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 模型详情 -->
    <div v-else-if="model" class="detail-content">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag v-if="model.is_default" type="success">默认模型</el-tag>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">
            <span class="model-name">{{ model.name }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="模型标识">
            <el-tag>{{ model.model }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="API地址">
            <el-link :href="model.base_url" target="_blank" type="primary">
              {{ model.base_url }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="API密钥环境变量">
            <el-tag type="info">{{ model.api_key_env }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="超时设置">
            {{ model.timeout }} 秒
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="model.is_active ? 'success' : 'danger'">
              {{ model.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(model.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(model.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 生成配置 -->
      <el-card class="config-card">
        <template #header>
          <span>生成配置</span>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="最大令牌数">
            <el-tag type="primary">{{ model.generation_config?.max_tokens || 'N/A' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="温度">
            <el-tag type="warning">{{ model.generation_config?.temperature || 'N/A' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Top P">
            <el-tag>{{ model.generation_config?.top_p || 'N/A' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="频率惩罚">
            <el-tag>{{ model.generation_config?.frequency_penalty || 'N/A' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="存在惩罚">
            <el-tag>{{ model.generation_config?.presence_penalty || 'N/A' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="停止序列">
            <div v-if="model.generation_config?.stop_sequences?.length">
              <el-tag
                v-for="(seq, index) in model.generation_config.stop_sequences"
                :key="index"
                style="margin-right: 8px; margin-bottom: 4px"
              >
                {{ seq }}
              </el-tag>
            </div>
            <span v-else class="text-muted">无</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 系统提示词 -->
      <el-card v-if="model.system_prompt" class="prompt-card">
        <template #header>
          <span>系统提示词</span>
        </template>
        
        <div class="prompt-content">
          <pre>{{ model.system_prompt }}</pre>
        </div>
      </el-card>

      <!-- 操作历史 -->
      <el-card class="history-card">
        <template #header>
          <span>操作历史</span>
        </template>
        
        <el-timeline>
          <el-timeline-item
            :timestamp="model.created_at ? formatDate(model.created_at) : ''"
            type="primary"
          >
            模型创建
          </el-timeline-item>
          <el-timeline-item
            v-if="model.updated_at && model.updated_at !== model.created_at"
            :timestamp="model.updated_at ? formatDate(model.updated_at) : ''"
            type="success"
          >
            配置更新
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <!-- 未找到模型 -->
    <el-empty v-else description="未找到该模型" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Edit,
  VideoPlay
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

// 返回列表
const handleBack = () => {
  router.push('/ai')
}

// 编辑模型
const handleEdit = () => {
  if (model.value?.id) {
    router.push(`/ai/edit/${model.value.id}`)
  }
}

// 测试模型
const handleTest = () => {
  if (model.value?.id) {
    router.push(`/ai/test/${model.value.id}`)
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
    }
  } catch (error) {
    ElMessage.error('加载模型详情失败')
    console.error('加载模型详情失败:', error)
  }
})
</script>

<style scoped>
.ai-model-detail {
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

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card,
.config-card,
.prompt-card,
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

.prompt-content {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.prompt-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #495057;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>