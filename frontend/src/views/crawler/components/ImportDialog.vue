<template>
  <el-dialog
    v-model="visible"
    title="导入爬虫配置"
    width="600px"
    :before-close="handleClose"
  >
    <div class="import-container">
      <!-- 导入方式选择 -->
      <div class="import-method">
        <el-radio-group v-model="importMethod" @change="handleMethodChange">
          <el-radio label="file">文件导入</el-radio>
          <el-radio label="json">JSON导入</el-radio>
          <el-radio label="url">URL导入</el-radio>
        </el-radio-group>
      </div>
      
      <!-- 文件导入 -->
      <div v-if="importMethod === 'file'" class="import-section">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          accept=".json"
          @change="handleFileChange"
          @remove="handleFileRemove"
        >
          <template #trigger>
            <el-button type="primary" :icon="Upload">
              选择文件
            </el-button>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              只能上传JSON格式的配置文件，且不超过1MB
            </div>
          </template>
        </el-upload>
      </div>
      
      <!-- JSON导入 -->
      <div v-if="importMethod === 'json'" class="import-section">
        <el-input
          v-model="jsonContent"
          type="textarea"
          :rows="10"
          placeholder="请粘贴JSON格式的配置内容"
          @input="handleJsonInput"
        />
        <div class="json-actions">
          <el-button size="small" @click="formatJson">
            格式化JSON
          </el-button>
          <el-button size="small" @click="validateJson">
            验证JSON
          </el-button>
        </div>
      </div>
      
      <!-- URL导入 -->
      <div v-if="importMethod === 'url'" class="import-section">
        <el-input
          v-model="importUrl"
          placeholder="请输入配置文件的URL地址"
          @input="handleUrlInput"
        >
          <template #append>
            <el-button :icon="Download" @click="fetchFromUrl">
              获取
            </el-button>
          </template>
        </el-input>
        <div class="url-tip">
          支持HTTP/HTTPS协议的JSON配置文件
        </div>
      </div>
      
      <!-- 预览区域 -->
      <div v-if="previewData" class="preview-section">
        <h3 class="preview-title">
          配置预览
          <el-tag type="info" size="small">
            {{ previewData.length }} 个配置
          </el-tag>
        </h3>
        
        <div class="preview-list">
          <div
            v-for="(config, index) in previewData"
            :key="index"
            class="preview-item"
          >
            <div class="item-header">
              <el-checkbox
                v-model="config.selected"
                :label="config.name"
              />
              <el-tag :type="getConfigTypeColor(config.type)" size="small">
                {{ getConfigTypeText(config.type) }}
              </el-tag>
            </div>
            <div class="item-details">
              <div class="detail-row">
                <span class="label">URL:</span>
                <span class="value">{{ config.url }}</span>
              </div>
              <div class="detail-row">
                <span class="label">规则:</span>
                <span class="value">{{ config.extractionRules?.length || 0 }} 条</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 批量操作 -->
        <div class="batch-actions">
          <el-button size="small" @click="selectAll">
            全选
          </el-button>
          <el-button size="small" @click="selectNone">
            全不选
          </el-button>
          <el-button size="small" @click="selectInvert">
            反选
          </el-button>
        </div>
      </div>
      
      <!-- 导入选项 -->
      <div v-if="previewData" class="import-options">
        <h3 class="options-title">导入选项</h3>
        <el-checkbox v-model="importOptions.overwrite">
          覆盖同名配置
        </el-checkbox>
        <el-checkbox v-model="importOptions.validateRules">
          验证提取规则
        </el-checkbox>
        <el-checkbox v-model="importOptions.autoActivate">
          自动启用配置
        </el-checkbox>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="errorMessage" class="error-section">
        <el-alert
          :title="errorMessage"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!canImport"
          @click="handleImport"
        >
          导入配置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import { Upload, Download } from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const crawlerStore = useCrawlerStore()
const uploadRef = ref()
const loading = ref(false)

// 响应式数据
const importMethod = ref('file')
const selectedFile = ref<File | null>(null)
const jsonContent = ref('')
const importUrl = ref('')
const previewData = ref<any[]>([])
const errorMessage = ref('')
const importOptions = ref({
  overwrite: false,
  validateRules: true,
  autoActivate: true
})

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const canImport = computed(() => {
  return previewData.value.length > 0 && 
         previewData.value.some(config => config.selected) &&
         !errorMessage.value
})

// 工具方法
const getConfigTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    list: 'primary',
    detail: 'success',
    search: 'warning',
    category: 'info'
  }
  return colorMap[type] || 'info'
}

const getConfigTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    list: '列表页',
    detail: '详情页',
    search: '搜索页',
    category: '分类页'
  }
  return typeMap[type] || type
}

const validateConfigData = (data: any): boolean => {
  if (!Array.isArray(data)) {
    errorMessage.value = '配置数据必须是数组格式'
    return false
  }
  
  for (let i = 0; i < data.length; i++) {
    const config = data[i]
    if (!config.name || !config.url) {
      errorMessage.value = `第 ${i + 1} 个配置缺少必要字段 (name, url)`
      return false
    }
    
    if (config.url && !/^https?:\/\/.+/.test(config.url)) {
      errorMessage.value = `第 ${i + 1} 个配置的URL格式不正确`
      return false
    }
  }
  
  return true
}

const processConfigData = (data: any[]) => {
  errorMessage.value = ''
  
  if (!validateConfigData(data)) {
    previewData.value = []
    return
  }
  
  previewData.value = data.map(config => ({
    ...config,
    selected: true
  }))
}

// 事件处理
const handleMethodChange = () => {
  // 清空数据
  previewData.value = []
  errorMessage.value = ''
  jsonContent.value = ''
  importUrl.value = ''
  uploadRef.value?.clearFiles()
}

const handleFileChange = (file: UploadFile) => {
  const rawFile = file.raw
  if (!rawFile) return
  
  if (rawFile.size > 1024 * 1024) {
    errorMessage.value = '文件大小不能超过1MB'
    uploadRef.value?.clearFiles()
    return
  }
  
  selectedFile.value = rawFile
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      const data = JSON.parse(content)
      processConfigData(data)
    } catch (error) {
      errorMessage.value = '文件格式错误，请确保是有效的JSON文件'
      previewData.value = []
    }
  }
  reader.readAsText(rawFile)
}

const handleFileRemove = () => {
  selectedFile.value = null
  previewData.value = []
  errorMessage.value = ''
}

const handleJsonInput = () => {
  if (!jsonContent.value.trim()) {
    previewData.value = []
    errorMessage.value = ''
    return
  }
  
  try {
    const data = JSON.parse(jsonContent.value)
    processConfigData(data)
  } catch (error) {
    errorMessage.value = 'JSON格式错误'
    previewData.value = []
  }
}

const handleUrlInput = () => {
  errorMessage.value = ''
}

const formatJson = () => {
  try {
    const data = JSON.parse(jsonContent.value)
    jsonContent.value = JSON.stringify(data, null, 2)
    ElMessage.success('JSON格式化成功')
  } catch (error) {
    ElMessage.error('JSON格式错误，无法格式化')
  }
}

const validateJson = () => {
  try {
    JSON.parse(jsonContent.value)
    ElMessage.success('JSON格式正确')
  } catch (error) {
    ElMessage.error('JSON格式错误')
  }
}

const fetchFromUrl = async () => {
  if (!importUrl.value) {
    ElMessage.warning('请输入URL地址')
    return
  }
  
  if (!/^https?:\/\/.+/.test(importUrl.value)) {
    errorMessage.value = 'URL格式不正确'
    return
  }
  
  try {
    loading.value = true
    const response = await fetch(importUrl.value)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    processConfigData(data)
    ElMessage.success('获取配置成功')
  } catch (error: any) {
    errorMessage.value = `获取配置失败: ${error.message}`
    previewData.value = []
  } finally {
    loading.value = false
  }
}

const selectAll = () => {
  previewData.value.forEach(config => {
    config.selected = true
  })
}

const selectNone = () => {
  previewData.value.forEach(config => {
    config.selected = false
  })
}

const selectInvert = () => {
  previewData.value.forEach(config => {
    config.selected = !config.selected
  })
}

const handleClose = () => {
  visible.value = false
}

const handleImport = async () => {
  const selectedConfigs = previewData.value.filter(config => config.selected)
  
  if (selectedConfigs.length === 0) {
    ElMessage.warning('请至少选择一个配置')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要导入 ${selectedConfigs.length} 个配置吗？`,
      '确认导入',
      {
        type: 'info'
      }
    )
    
    loading.value = true
    
    // 处理配置数据
    const configsToImport = selectedConfigs.map(config => {
      const { selected, ...configData } = config
      return {
        ...configData,
        status: importOptions.value.autoActivate ? 'active' : 'inactive'
      }
    })
    
    // 根据导入方式处理文件
    let fileToImport: File
    if (importMethod.value === 'file' && selectedFile.value) {
      fileToImport = selectedFile.value
    } else {
      // 对于JSON和URL导入，创建临时文件
      const jsonData = JSON.stringify(configsToImport, null, 2)
      const blob = new Blob([jsonData], { type: 'application/json' })
      fileToImport = new File([blob], 'import-configs.json', { type: 'application/json' })
    }
    
    await crawlerStore.importCrawlerConfigs(fileToImport)
    
    ElMessage.success(`成功导入 ${selectedConfigs.length} 个配置`)
    emit('success')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导入失败')
    }
  } finally {
    loading.value = false
  }
}

// 监听对话框显示状态
watch(visible, (newVisible) => {
  if (!newVisible) {
    // 重置数据
    importMethod.value = 'file'
    selectedFile.value = null
    jsonContent.value = ''
    importUrl.value = ''
    previewData.value = []
    errorMessage.value = ''
    uploadRef.value?.clearFiles()
  }
})
</script>

<style lang="scss" scoped>
.import-container {
  .import-method {
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
  
  .import-section {
    margin-bottom: 24px;
    
    .json-actions {
      margin-top: 8px;
      display: flex;
      gap: 8px;
    }
    
    .url-tip {
      margin-top: 8px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
  
  .preview-section {
    margin-bottom: 24px;
    
    .preview-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .preview-list {
      max-height: 300px;
      overflow-y: auto;
      border: 1px solid var(--el-border-color-light);
      border-radius: 4px;
      
      .preview-item {
        padding: 12px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        &:last-child {
          border-bottom: none;
        }
        
        .item-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .item-details {
          .detail-row {
            display: flex;
            align-items: center;
            margin-bottom: 4px;
            font-size: 12px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .label {
              color: var(--el-text-color-secondary);
              min-width: 40px;
              margin-right: 8px;
            }
            
            .value {
              color: var(--el-text-color-regular);
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
        }
      }
    }
    
    .batch-actions {
      margin-top: 12px;
      display: flex;
      gap: 8px;
    }
  }
  
  .import-options {
    margin-bottom: 24px;
    
    .options-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 12px;
    }
    
    .el-checkbox {
      display: block;
      margin-bottom: 8px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  
  .error-section {
    margin-bottom: 24px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-upload__tip) {
  margin-top: 8px;
}
</style>