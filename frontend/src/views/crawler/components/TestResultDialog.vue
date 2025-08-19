<template>
  <el-dialog
    v-model="visible"
    title="配置测试结果"
    width="900px"
    :before-close="handleClose"
  >
    <div v-if="testResult" class="test-result">
      <!-- 测试概览 -->
      <div class="result-overview">
        <div class="overview-item">
          <div class="item-label">测试状态</div>
          <div class="item-value">
            <el-tag :type="testResult.success ? 'success' : 'danger'" size="large">
              {{ testResult.success ? '成功' : '失败' }}
            </el-tag>
          </div>
        </div>
        <div class="overview-item">
          <div class="item-label">执行时间</div>
          <div class="item-value">{{ testResult.duration }}ms</div>
        </div>
        <div class="overview-item">
          <div class="item-label">提取数量</div>
          <div class="item-value">{{ testResult.extractedCount || 0 }} 条</div>
        </div>
        <div class="overview-item">
          <div class="item-label">测试时间</div>
          <div class="item-value">{{ formatDate(testResult.timestamp) }}</div>
        </div>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="!testResult.success && testResult.error" class="error-section">
        <h3 class="section-title">错误信息</h3>
        <div class="error-content">
          <div class="error-message">{{ testResult.error.message }}</div>
          <div v-if="testResult.error.stack" class="error-stack">
            <el-collapse>
              <el-collapse-item title="错误堆栈" name="stack">
                <pre class="stack-trace">{{ testResult.error.stack }}</pre>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>
      
      <!-- 提取结果 -->
      <div v-if="testResult.success && testResult.data" class="data-section">
        <h3 class="section-title">
          提取结果
          <el-button
            type="primary"
            size="small"
            :icon="Download"
            @click="handleExportData"
          >
            导出数据
          </el-button>
        </h3>
        
        <!-- 数据预览 -->
        <div class="data-preview">
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="表格视图" name="table">
              <div class="table-container">
                <el-table
                  :data="testResult.data"
                  border
                  stripe
                  max-height="400"
                  style="width: 100%"
                >
                  <el-table-column
                    v-for="(column, index) in dataColumns"
                    :key="index"
                    :prop="column.prop"
                    :label="column.label"
                    :width="column.width"
                    show-overflow-tooltip
                  >
                    <template #default="{ row }">
                      <div v-if="column.type === 'link'">
                        <el-link :href="row[column.prop]" target="_blank" type="primary">
                          {{ row[column.prop] }}
                        </el-link>
                      </div>
                      <div v-else-if="column.type === 'image'">
                        <el-image
                          :src="row[column.prop]"
                          :preview-src-list="[row[column.prop]]"
                          fit="cover"
                          style="width: 60px; height: 40px"
                        />
                      </div>
                      <div v-else>
                        {{ row[column.prop] }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="JSON视图" name="json">
              <div class="json-container">
                <pre class="json-content">{{ JSON.stringify(testResult.data, null, 2) }}</pre>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      
      <!-- 规则验证结果 -->
      <div v-if="testResult.ruleResults" class="rules-section">
        <h3 class="section-title">规则验证结果</h3>
        <div class="rules-list">
          <div
            v-for="(result, index) in testResult.ruleResults"
            :key="index"
            class="rule-result-item"
          >
            <div class="rule-header">
              <span class="rule-name">{{ result.ruleName }}</span>
              <el-tag :type="result.success ? 'success' : 'danger'" size="small">
                {{ result.success ? '成功' : '失败' }}
              </el-tag>
            </div>
            <div class="rule-details">
              <div class="detail-item">
                <label>XPath：</label>
                <code class="xpath">{{ result.xpath }}</code>
              </div>
              <div class="detail-item">
                <label>匹配数量：</label>
                <span>{{ result.matchCount || 0 }}</span>
              </div>
              <div v-if="result.sampleValue" class="detail-item">
                <label>示例值：</label>
                <span class="sample-value">{{ result.sampleValue }}</span>
              </div>
              <div v-if="result.error" class="detail-item">
                <label>错误信息：</label>
                <span class="error-text">{{ result.error }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 性能信息 -->
      <div v-if="testResult.performance" class="performance-section">
        <h3 class="section-title">性能信息</h3>
        <div class="performance-grid">
          <div class="perf-item">
            <div class="perf-label">页面加载时间</div>
            <div class="perf-value">{{ testResult.performance.loadTime }}ms</div>
          </div>
          <div class="perf-item">
            <div class="perf-label">DOM解析时间</div>
            <div class="perf-value">{{ testResult.performance.parseTime }}ms</div>
          </div>
          <div class="perf-item">
            <div class="perf-label">数据提取时间</div>
            <div class="perf-value">{{ testResult.performance.extractTime }}ms</div>
          </div>
          <div class="perf-item">
            <div class="perf-label">内存使用</div>
            <div class="perf-value">{{ formatBytes(testResult.performance.memoryUsage) }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="loading-container">
      <el-loading-spinner size="large" />
      <div class="loading-text">正在执行测试...</div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          v-if="testResult?.success"
          type="primary"
          :icon="Download"
          @click="handleExportData"
        >
          导出结果
        </el-button>
        <el-button
          type="success"
          :icon="Refresh"
          @click="handleRetest"
        >
          重新测试
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'

interface Props {
  modelValue: boolean
  config?: any
  testResult?: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'retest', config: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const crawlerStore = useCrawlerStore()
const activeTab = ref('table')

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const dataColumns = computed(() => {
  if (!props.testResult?.data?.length) return []
  
  const firstItem = props.testResult.data[0]
  const columns = Object.keys(firstItem).map(key => {
    // 根据配置中的提取规则确定列类型
    const rule = props.config?.extractionRules?.find((r: any) => r.name === key)
    const type = rule?.type || 'text'
    
    return {
      prop: key,
      label: rule?.name || key,
      type,
      width: type === 'image' ? 120 : undefined
    }
  })
  
  return columns
})

// 工具方法
const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleString()
}

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 事件处理
const handleClose = () => {
  visible.value = false
}

const handleRetest = () => {
  emit('retest', props.config)
}

const handleExportData = () => {
  if (!props.testResult?.data) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  try {
    const dataStr = JSON.stringify(props.testResult.data, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `test-result-${props.config?.name || 'config'}-${Date.now()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 监听测试结果变化
watch(
  () => props.testResult,
  (newResult) => {
    if (newResult && visible.value) {
      activeTab.value = 'table'
    }
  }
)
</script>

<style lang="scss" scoped>
.test-result {
  .result-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
    padding: 16px;
    background: var(--el-fill-color-extra-light);
    border-radius: 6px;
    
    .overview-item {
      text-align: center;
      
      .item-label {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-bottom: 4px;
      }
      
      .item-value {
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }
    }
  }
  
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

.error-section {
  margin-bottom: 24px;
  
  .error-content {
    .error-message {
      color: var(--el-color-danger);
      font-weight: 500;
      margin-bottom: 12px;
      padding: 12px;
      background: var(--el-color-danger-light-9);
      border-radius: 4px;
      border-left: 4px solid var(--el-color-danger);
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
}

.data-section {
  margin-bottom: 24px;
  
  .data-preview {
    .table-container {
      max-height: 400px;
      overflow-y: auto;
    }
    
    .json-container {
      max-height: 400px;
      overflow-y: auto;
      
      .json-content {
        font-family: monospace;
        font-size: 12px;
        background: var(--el-fill-color-light);
        padding: 16px;
        border-radius: 4px;
        margin: 0;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  }
}

.rules-section {
  margin-bottom: 24px;
  
  .rules-list {
    .rule-result-item {
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
      
      .rule-details {
        .detail-item {
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
          
          .xpath {
            font-family: monospace;
            font-size: 12px;
            background: var(--el-fill-color-light);
            padding: 2px 6px;
            border-radius: 3px;
            word-break: break-all;
          }
          
          .sample-value {
            font-family: monospace;
            font-size: 12px;
            background: var(--el-color-success-light-9);
            padding: 2px 6px;
            border-radius: 3px;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          
          .error-text {
            color: var(--el-color-danger);
            font-size: 12px;
          }
        }
      }
    }
  }
}

.performance-section {
  margin-bottom: 24px;
  
  .performance-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    
    .perf-item {
      text-align: center;
      padding: 12px;
      background: var(--el-fill-color-lighter);
      border-radius: 4px;
      
      .perf-label {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-bottom: 4px;
      }
      
      .perf-value {
        font-size: 14px;
        font-weight: 600;
        color: var(--el-color-primary);
      }
    }
  }
}

.loading-container {
  text-align: center;
  padding: 60px 0;
  
  .loading-text {
    margin-top: 16px;
    color: var(--el-text-color-regular);
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>