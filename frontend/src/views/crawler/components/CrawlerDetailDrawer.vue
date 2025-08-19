<template>
  <el-drawer
    v-model="visible"
    title="配置详情"
    size="60%"
    direction="rtl"
    :before-close="handleClose"
  >
    <div v-if="config" class="crawler-detail">
      <!-- 基本信息 -->
      <div class="detail-section">
        <h3 class="section-title">基本信息</h3>
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
      </div>
      
      <!-- 描述信息 -->
      <div v-if="config.description" class="detail-section">
        <h3 class="section-title">描述</h3>
        <p class="description">{{ config.description }}</p>
      </div>
      
      <!-- 爬取配置 -->
      <div class="detail-section">
        <h3 class="section-title">爬取配置</h3>
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
      </div>
      
      <!-- 提取规则 -->
      <div class="detail-section">
        <h3 class="section-title">
          提取规则
          <el-tag type="info" size="small" class="rule-count">
            {{ config.extractionRules?.length || 0 }} 条
          </el-tag>
        </h3>
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
      </div>
      
      <!-- 统计信息 -->
      <div v-if="config.statistics" class="detail-section">
        <h3 class="section-title">统计信息</h3>
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
      </div>
      
      <!-- 最近错误 -->
      <div v-if="config.lastError" class="detail-section">
        <h3 class="section-title">最近错误</h3>
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
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleClose">关闭</el-button>
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
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Edit, Download } from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'

interface Props {
  modelValue: boolean
  config: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'refresh'): void
  (e: 'edit', config: any): void
  (e: 'test', config: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const crawlerStore = useCrawlerStore()

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 工具方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    error: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '启用',
    inactive: '禁用',
    error: '错误'
  }
  return statusMap[status] || status
}

const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    list: '列表页',
    detail: '详情页',
    search: '搜索页',
    category: '分类页'
  }
  return typeMap[type] || type
}

const getRuleTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    text: 'primary',
    link: 'success',
    image: 'warning',
    number: 'info'
  }
  return colorMap[type] || 'info'
}

const getRuleTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    text: '文本',
    link: '链接',
    image: '图片',
    number: '数字'
  }
  return typeMap[type] || type
}

const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleString()
}

// 事件处理
const handleClose = () => {
  visible.value = false
}

const handleTest = () => {
  emit('test', props.config)
  handleClose()
}

const handleEdit = () => {
  emit('edit', props.config)
  handleClose()
}

const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中')
}
</script>

<style lang="scss" scoped>
.crawler-detail {
  padding: 0 4px;
}

.detail-section {
  margin-bottom: 32px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .rule-count {
      margin-left: auto;
    }
  }
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  .info-item {
    display: flex;
    align-items: center;
    
    label {
      font-weight: 500;
      color: var(--el-text-color-regular);
      min-width: 80px;
      margin-right: 8px;
    }
  }
}

.description {
  color: var(--el-text-color-regular);
  line-height: 1.6;
  background: var(--el-fill-color-lighter);
  padding: 12px;
  border-radius: 4px;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  .config-item {
    display: flex;
    align-items: center;
    
    label {
      font-weight: 500;
      color: var(--el-text-color-regular);
      min-width: 80px;
      margin-right: 8px;
    }
    
    .user-agent {
      font-family: monospace;
      font-size: 12px;
      background: var(--el-fill-color-light);
      padding: 2px 6px;
      border-radius: 3px;
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

.rules-list {
  .rule-item {
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 12px;
    
    .rule-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      
      .rule-name {
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
    }
    
    .rule-content {
      .rule-field {
        display: flex;
        align-items: flex-start;
        margin-bottom: 8px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        label {
          font-weight: 500;
          color: var(--el-text-color-regular);
          min-width: 80px;
          margin-right: 8px;
          flex-shrink: 0;
        }
        
        .xpath,
        .regex {
          font-family: monospace;
          font-size: 12px;
          background: var(--el-fill-color-light);
          padding: 4px 8px;
          border-radius: 3px;
          word-break: break-all;
          flex: 1;
        }
      }
    }
  }
}

.empty-rules {
  text-align: center;
  padding: 40px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  
  .stat-item {
    text-align: center;
    padding: 16px;
    background: var(--el-fill-color-lighter);
    border-radius: 6px;
    
    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: var(--el-color-primary);
      margin-bottom: 4px;
    }
    
    .stat-label {
      font-size: 12px;
      color: var(--el-text-color-regular);
    }
  }
}

.error-info {
  .error-time {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 8px;
  }
  
  .error-message {
    color: var(--el-color-danger);
    font-weight: 500;
    margin-bottom: 12px;
  }
  
  .stack-trace {
    font-family: monospace;
    font-size: 12px;
    background: var(--el-fill-color-darker);
    padding: 12px;
    border-radius: 4px;
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
  }
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>