<template>
  <div class="crawler-import-page">
    <PageHeader 
      title="配置导入导出" 
      description="批量导入导出爬虫配置"
      show-back
      @back="handleBack"
    />
    
    <div class="import-export-container">
      <!-- 导入配置 -->
      <el-card class="import-section" shadow="never">
        <template #header>
          <div class="section-header">
            <h3 class="section-title">
              <el-icon><Upload /></el-icon>
              导入配置
            </h3>
          </div>
        </template>
        
        <div class="import-content">
          <div class="upload-area">
            <el-upload
              ref="uploadRef"
              class="upload-dragger"
              drag
              :auto-upload="false"
              :show-file-list="false"
              accept=".json,.zip"
              :on-change="handleFileChange"
              :before-upload="beforeUpload"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <div class="el-upload__tip">
                支持 JSON 和 ZIP 格式，单个文件不超过 10MB
              </div>
            </el-upload>
          </div>
          
          <!-- 文件信息 -->
          <div v-if="selectedFile" class="file-info">
            <div class="file-item">
              <div class="file-details">
                <div class="file-name">
                  <el-icon><Document /></el-icon>
                  {{ selectedFile.name }}
                </div>
                <div class="file-meta">
                  <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
                  <span class="file-type">{{ getFileType(selectedFile.name) }}</span>
                </div>
              </div>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Delete" 
                @click="clearFile"
              >
                移除
              </el-button>
            </div>
          </div>
          
          <!-- 导入选项 -->
          <div v-if="selectedFile" class="import-options">
            <h4>导入选项</h4>
            <el-form :model="importForm" label-width="120px">
              <el-form-item label="冲突处理：">
                <el-radio-group v-model="importForm.conflictStrategy">
                  <el-radio value="skip">跳过重复</el-radio>
                  <el-radio value="overwrite">覆盖现有</el-radio>
                  <el-radio value="rename">自动重命名</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="验证配置：">
                <el-switch 
                  v-model="importForm.validateConfig" 
                  active-text="启用" 
                  inactive-text="禁用"
                />
              </el-form-item>
              
              <el-form-item label="导入后状态：">
                <el-select v-model="importForm.defaultStatus" placeholder="选择状态">
                  <el-option label="活跃" value="active" />
                  <el-option label="未激活" value="inactive" />
                  <el-option label="测试中" value="testing" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 导入按钮 -->
          <div v-if="selectedFile" class="import-actions">
            <el-button 
              type="primary" 
              size="large"
              :loading="importing"
              :icon="Upload"
              @click="handleImport"
            >
              {{ importing ? '导入中...' : '开始导入' }}
            </el-button>
          </div>
        </div>
      </el-card>
      
      <!-- 导出配置 -->
      <el-card class="export-section" shadow="never">
        <template #header>
          <div class="section-header">
            <h3 class="section-title">
              <el-icon><Download /></el-icon>
              导出配置
            </h3>
          </div>
        </template>
        
        <div class="export-content">
          <!-- 配置选择 -->
          <div class="config-selection">
            <h4>选择要导出的配置</h4>
            <div class="selection-controls">
              <el-button size="small" @click="selectAll">全选</el-button>
              <el-button size="small" @click="selectNone">全不选</el-button>
              <el-button size="small" @click="selectActive">仅选择活跃</el-button>
            </div>
            
            <div class="config-list">
              <el-checkbox-group v-model="selectedConfigs">
                <div 
                  v-for="config in crawlerConfigs" 
                  :key="config.id" 
                  class="config-item"
                >
                  <el-checkbox :value="config.id">
                    <div class="config-info">
                      <div class="config-name">{{ config.name }}</div>
                      <div class="config-meta">
                        <el-tag :type="getStatusType(config.status)" size="small">
                          {{ getStatusText(config.status) }}
                        </el-tag>
                        <span class="config-url">{{ config.url }}</span>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
              </el-checkbox-group>
            </div>
          </div>
          
          <!-- 导出选项 -->
          <div class="export-options">
            <h4>导出选项</h4>
            <el-form :model="exportForm" label-width="120px">
              <el-form-item label="导出格式：">
                <el-radio-group v-model="exportForm.format">
                  <el-radio value="json">JSON 格式</el-radio>
                  <el-radio value="zip">ZIP 压缩包</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="包含数据：">
                <el-checkbox-group v-model="exportForm.includeData">
                  <el-checkbox value="statistics">统计信息</el-checkbox>
                  <el-checkbox value="logs">运行日志</el-checkbox>
                  <el-checkbox value="results">爬取结果</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="敏感信息：">
                <el-switch 
                  v-model="exportForm.excludeSensitive" 
                  active-text="排除" 
                  inactive-text="包含"
                />
                <div class="form-tip">
                  排除 Cookie、Token 等敏感信息
                </div>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 导出按钮 -->
          <div class="export-actions">
            <el-button 
              type="success" 
              size="large"
              :loading="exporting"
              :disabled="selectedConfigs.length === 0"
              :icon="Download"
              @click="handleExport"
            >
              {{ exporting ? '导出中...' : `导出配置 (${selectedConfigs.length})` }}
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 导入结果对话框 -->
    <el-dialog 
      v-model="importResultVisible" 
      title="导入结果" 
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="import-result">
        <div class="result-summary">
          <div class="summary-item">
            <span class="label">总计：</span>
            <span class="value">{{ importResult.total || 0 }}</span>
          </div>
          <div class="summary-item success">
            <span class="label">成功：</span>
            <span class="value">{{ importResult.success || 0 }}</span>
          </div>
          <div class="summary-item failed">
            <span class="label">失败：</span>
            <span class="value">{{ importResult.failed || 0 }}</span>
          </div>
          <div class="summary-item skipped">
            <span class="label">跳过：</span>
            <span class="value">{{ importResult.skipped || 0 }}</span>
          </div>
        </div>
        
        <div v-if="importResult.errors?.length" class="error-list">
          <h4>错误详情</h4>
          <div class="error-items">
            <div 
              v-for="(error, index) in importResult.errors" 
              :key="index" 
              class="error-item"
            >
              <div class="error-config">{{ error.config }}</div>
              <div class="error-message">{{ error.message }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="importResultVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleRefreshList">刷新列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  UploadFilled,
  Download,
  Document,
  Delete
} from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'
import PageHeader from '@/components/common/PageHeader.vue'

// 路由
const router = useRouter()

// 状态管理
const crawlerStore = useCrawlerStore()

// 响应式数据
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const exporting = ref(false)
const importResultVisible = ref(false)
const crawlerConfigs = ref<any[]>([])
const selectedConfigs = ref<string[]>([])
const importResult = ref<any>({})

// 表单数据
const importForm = ref({
  conflictStrategy: 'skip',
  validateConfig: true,
  defaultStatus: 'inactive'
})

const exportForm = ref({
  format: 'json',
  includeData: ['statistics'],
  excludeSensitive: true
})

// 方法
const loadCrawlerConfigs = async () => {
  try {
    await crawlerStore.fetchCrawlerConfigs()
    crawlerConfigs.value = crawlerStore.crawlerConfigs
  } catch (error) {
    console.error('加载配置列表失败:', error)
    ElMessage.error('加载配置列表失败')
  }
}

const handleBack = () => {
  router.push('/crawler/list')
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const beforeUpload = (file: File) => {
  const isValidType = file.type === 'application/json' || file.name.endsWith('.zip')
  const isValidSize = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error('只支持 JSON 和 ZIP 格式的文件')
    return false
  }
  
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  return false // 阻止自动上传
}

const clearFile = () => {
  selectedFile.value = null
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }
  
  importing.value = true
  try {
    const result = await crawlerStore.importCrawlerConfigs(selectedFile.value)
    importResult.value = result
    importResultVisible.value = true
    
    ElMessage.success('导入完成')
    clearFile()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

const handleExport = async () => {
  if (selectedConfigs.value.length === 0) {
    ElMessage.warning('请选择要导出的配置')
    return
  }
  
  exporting.value = true
  try {
    await crawlerStore.exportCrawlerConfigs(selectedConfigs.value)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const selectAll = () => {
  selectedConfigs.value = crawlerConfigs.value.map(config => config.id)
}

const selectNone = () => {
  selectedConfigs.value = []
}

const selectActive = () => {
  selectedConfigs.value = crawlerConfigs.value
    .filter(config => config.status === 'active')
    .map(config => config.id)
}

const handleRefreshList = () => {
  importResultVisible.value = false
  loadCrawlerConfigs()
}

// 辅助方法
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileType = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  return ext === 'json' ? 'JSON 配置' : ext === 'zip' ? 'ZIP 压缩包' : '未知格式'
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

// 生命周期
onMounted(() => {
  loadCrawlerConfigs()
})
</script>

<style scoped>
.crawler-import-page {
  padding: 20px;
}

.import-export-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .import-export-container {
    grid-template-columns: 1fr;
  }
}

.import-section,
.export-section {
  height: fit-content;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.import-content,
.export-content {
  padding: 20px 0;
}

.upload-area {
  margin-bottom: 20px;
}

.upload-dragger {
  width: 100%;
}

.file-info {
  margin-bottom: 20px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #f8f9fa;
}

.file-details {
  flex: 1;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.import-options,
.export-options {
  margin-bottom: 20px;
}

.import-options h4,
.export-options h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.import-actions,
.export-actions {
  text-align: center;
}

.config-selection {
  margin-bottom: 20px;
}

.selection-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.config-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
}

.config-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.config-item:last-child {
  border-bottom: none;
}

.config-info {
  margin-left: 8px;
}

.config-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.config-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.config-url {
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.import-result {
  padding: 20px 0;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background: #f8f9fa;
}

.summary-item.success {
  background: #f0f9ff;
  color: #67c23a;
}

.summary-item.failed {
  background: #fef0f0;
  color: #f56c6c;
}

.summary-item.skipped {
  background: #fdf6ec;
  color: #e6a23c;
}

.summary-item .label {
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
}

.summary-item .value {
  font-size: 20px;
  font-weight: 600;
}

.error-list {
  margin-top: 20px;
}

.error-list h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #f56c6c;
}

.error-items {
  max-height: 200px;
  overflow-y: auto;
}

.error-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
}

.error-config {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.error-message {
  font-size: 12px;
  color: #f56c6c;
}
</style>