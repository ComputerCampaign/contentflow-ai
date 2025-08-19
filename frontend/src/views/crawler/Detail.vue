<template>
  <div class="crawler-detail-page">
    <PageHeader 
      :title="`配置详情 - ${config?.name || ''}`" 
      description="查看爬虫配置的详细信息"
      show-back
      @back="handleBack"
    />
    
    <div v-if="config" class="crawler-detail">
      <!-- 基本信息 -->  
      <el-card class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <h3 class="section-title">基本信息</h3>
            <div class="section-actions">
              <el-button type="primary" :icon="VideoPlay" @click="handleTest">
                测试配置
              </el-button>
              <el-button type="success" :icon="Edit" @click="handleEdit">
                编辑配置
              </el-button>
              <el-button :icon="Download" @click="handleExport">
                导出配置
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <label>配置名称：</label>
            <span>{{ config.name }}</span>
          </div>
          <div class="info-item">
            <label>目标URL：</label>
            <el-link :href="config.url" target="_blank" type="primary">
              {{ config.url }}
            </el-link>
          </div>
          <div class="info-item">
            <label>类型：</label>
            <el-tag type="info" size="small">
              {{ getTypeText(config.type) }}
            </el-tag>
          </div>
          <div class="info-item">
            <label>状态：</label>
            <el-tag :type="getStatusType(config.status)" size="small">
              {{ getStatusText(config.status) }}
            </el-tag>
          </div>
          <div class="info-item">
            <label>创建时间：</label>
            <span>{{ formatDate(config.createdAt) }}</span>
          </div>
          <div class="info-item">
            <label>更新时间：</label>
            <span>{{ formatDate(config.updatedAt) }}</span>
          </div>
        </div>
      </el-card>
      
      <!-- 描述信息 -->
      <el-card v-if="config.description" class="detail-section" shadow="never">
        <template #header>
          <h3 class="section-title">描述</h3>
        </template>
        <p class="description">{{ config.description }}</p>
      </el-card>
      
      <!-- 爬取配置 -->
      <el-card class="detail-section" shadow="never">
        <template #header>
          <h3 class="section-title">爬取配置</h3>
        </template>
        
        <div class="config-grid">
          <div class="config-item">
            <label>请求间隔：</label>
            <span>{{ config.delay || 1000 }}ms</span>
          </div>
          <div class="config-item">
            <label>超时时间：</label>
            <span>{{ config.timeout || 30000 }}ms</span>
          </div>
          <div class="config-item">
            <label>重试次数：</label>
            <span>{{ config.retries || 3 }}</span>
          </div>
          <div class="config-item">
            <label>并发数：</label>
            <span>{{ config.concurrency || 1 }}</span>
          </div>
          <div class="config-item">
            <label>User-Agent：</label>
            <span class="user-agent">{{ config.userAgent || '默认' }}</span>
          </div>
          <div class="config-item">
            <label>Cookie：</label>
            <span>{{ config.cookies ? '已设置' : '未设置' }}</span>
          </div>
        </div>
      </el-card>
      
      <!-- 提取规则 -->
      <el-card class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <h3 class="section-title">
              提取规则
              <el-tag type="info" size="small" class="rule-count">
                {{ config.extractionRules?.length || 0 }} 条
              </el-tag>
            </h3>
            <el-button size="small" :icon="Setting" @click="handleConfigureXPath">
              配置XPath
            </el-button>
          </div>
        </template>
        
        <div v-if="config.extractionRules?.length" class="rules-list">
          <div
            v-for="(rule, index) in config.extractionRules"
            :key="index"
            class="rule-item"
          >
            <div class="rule-header">
              <span class="rule-name">{{ rule.name }}</span>
              <el-tag :type="getRuleTypeColor(rule.type)" size="small">
                {{ getRuleTypeText(rule.type) }}
              </el-tag>
            </div>
            <div class="rule-content">
              <div class="rule-field">
                <label>XPath：</label>
                <code class="xpath">{{ rule.xpath }}</code>
              </div>
              <div v-if="rule.attribute" class="rule-field">
                <label>属性：</label>
                <span>{{ rule.attribute }}</span>
              </div>
              <div v-if="rule.regex" class="rule-field">
                <label>正则表达式：</label>
                <code class="regex">{{ rule.regex }}</code>
              </div>
              <div v-if="rule.defaultValue" class="rule-field">
                <label>默认值：</label>
                <span>{{ rule.defaultValue }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-rules">
          <el-empty description="暂无提取规则" :image-size="80" />
        </div>
      </el-card>
      
      <!-- 统计信息 -->
      <el-card v-if="config.statistics" class="detail-section" shadow="never">
        <template #header>
          <h3 class="section-title">统计信息</h3>
        </template>
        
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ config.statistics.totalRuns || 0 }}</div>
            <div class="stat-label">总运行次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ config.statistics.successRuns || 0 }}</div>
            <div class="stat-label">成功次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ config.statistics.failedRuns || 0 }}</div>
            <div class="stat-label">失败次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ config.statistics.avgDuration || 0 }}s</div>
            <div class="stat-label">平均耗时</div>
          </div>
        </div>
      </el-card>
      
      <!-- 最近错误 -->
      <el-card v-if="config.lastError" class="detail-section" shadow="never">
        <template #header>
          <h3 class="section-title">最近错误</h3>
        </template>
        
        <div class="error-info">
          <div class="error-time">
            {{ formatDate(config.lastError.timestamp) }}
          </div>
          <div class="error-message">
            {{ config.lastError.message }}
          </div>
          <div v-if="config.lastError.stack" class="error-stack">
            <el-collapse>
              <el-collapse-item title="错误堆栈" name="stack">
                <pre class="stack-trace">{{ config.lastError.stack }}</pre>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-result
        icon="error"
        title="加载失败"
        sub-title="无法加载配置详情，请检查配置ID是否正确"
      >
        <template #extra>
          <el-button type="primary" @click="handleRefresh">重新加载</el-button>
          <el-button @click="handleBack">返回列表</el-button>
        </template>
      </el-result>
    </div>
    
    <!-- 测试结果对话框 -->
    <TestResultDialog
      v-model="testVisible"
      :config="config"
      :test-result="testResult"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  Edit,
  Download,
  Setting
} from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'
import PageHeader from '@/components/common/PageHeader.vue'
import TestResultDialog from './components/TestResultDialog.vue'
import { formatDate } from '@/utils/date'

// 路由
const route = useRoute()
const router = useRouter()

// 状态管理
const crawlerStore = useCrawlerStore()

// 响应式数据
const loading = ref(false)
const config = ref<any>(null)
const testVisible = ref(false)
const testResult = ref<any>(null)

// 计算属性
const configId = computed(() => route.params.id as string)

// 方法
const loadConfig = async () => {
  if (!configId.value) return
  
  loading.value = true
  try {
    config.value = await crawlerStore.fetchCrawlerConfigById(configId.value)
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.push('/crawler/list')
}

const handleRefresh = () => {
  loadConfig()
}

const handleTest = async () => {
  if (!config.value) return
  
  try {
    testResult.value = await crawlerStore.testCrawlerConfig(config.value.id)
    testVisible.value = true
  } catch (error) {
    console.error('测试配置失败:', error)
    ElMessage.error('测试配置失败')
  }
}

const handleEdit = () => {
  router.push(`/crawler/edit/${config.value.id}`)
}

const handleExport = async () => {
  if (!config.value) return
  
  try {
    await crawlerStore.exportCrawlerConfigs([config.value.id.toString()])
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出配置失败:', error)
    ElMessage.error('导出配置失败')
  }
}

const handleConfigureXPath = () => {
  router.push(`/xpath/list?crawlerId=${config.value.id}`)
}

// 辅助方法
const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    web: '网页爬取',
    api: 'API接口',
    rss: 'RSS订阅',
    sitemap: '站点地图'
  }
  return typeMap[type] || type
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    error: 'danger',
    testing: 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '活跃',
    inactive: '未激活',
    error: '错误',
    testing: '测试中'
  }
  return statusMap[status] || status
}

const getRuleTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    text: 'primary',
    link: 'success',
    image: 'warning',
    data: 'info'
  }
  return colorMap[type] || 'info'
}

const getRuleTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    text: '文本',
    link: '链接',
    image: '图片',
    data: '数据'
  }
  return typeMap[type] || type
}

// 生命周期
onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.crawler-detail-page {
  padding: 20px;
}

.crawler-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.description {
  margin: 0;
  line-height: 1.6;
  color: #606266;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.config-item {
  display: flex;
  align-items: center;
}

.config-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.user-agent {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.rule-count {
  margin-left: 8px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rule-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rule-name {
  font-weight: 500;
  color: #303133;
}

.rule-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-field {
  display: flex;
  align-items: flex-start;
}

.rule-field label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
  flex-shrink: 0;
}

.xpath,
.regex {
  font-family: monospace;
  font-size: 12px;
  background: #f0f2f5;
  padding: 4px 8px;
  border-radius: 4px;
  word-break: break-all;
}

.empty-rules {
  text-align: center;
  padding: 40px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.error-info {
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 8px;
  padding: 16px;
}

.error-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.error-message {
  color: #f56c6c;
  font-weight: 500;
  margin-bottom: 12px;
}

.stack-trace {
  font-family: monospace;
  font-size: 12px;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.loading-container,
.error-container {
  padding: 40px 20px;
  text-align: center;
}
</style>