<template>
  <div class="xpath-detail">
    <el-card class="page-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
            <h2>{{ config?.name || 'XPath配置详情' }}</h2>
          </div>
          <div class="header-actions">
            <el-button @click="handleTest" :icon="VideoPlay">测试</el-button>
            <el-button type="primary" @click="handleEdit" :icon="Edit">编辑</el-button>
            <el-button type="danger" @click="handleDelete" :icon="Delete">删除</el-button>
          </div>
        </div>
      </template>

      <div v-if="config" class="config-content">
        <!-- 基本信息 -->  
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="配置名称">
            {{ config.name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="config.status === 'active' ? 'success' : 'info'">
              {{ config.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提取类型">
            <el-tag :type="getExtractTypeTag(config.extractType)">
              {{ getExtractTypeText(config.extractType) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="使用次数">
            {{ config.usageCount || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(config.createdAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(config.updatedAt) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 描述 -->
        <div v-if="config.description" class="section">
          <h3>描述</h3>
          <p class="description">{{ config.description }}</p>
        </div>

        <!-- XPath表达式 -->
        <div class="section">
          <h3>XPath表达式</h3>
          <div class="xpath-container">
            <pre class="xpath-code">{{ config.xpath }}</pre>
            <el-button 
              size="small" 
              @click="copyXPath" 
              :icon="DocumentCopy"
              class="copy-btn"
            >
              复制
            </el-button>
          </div>
        </div>

        <!-- 属性名称 -->
        <div v-if="config.extractType === 'attr' && config.attrName" class="section">
          <h3>属性名称</h3>
          <code class="attr-name">{{ config.attrName }}</code>
        </div>

        <!-- 处理规则 -->
        <div v-if="config.processing && config.processing.length > 0" class="section">
          <h3>处理规则</h3>
          <el-tag 
            v-for="rule in config.processing" 
            :key="rule" 
            class="processing-tag"
          >
            {{ rule }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="XPath测试"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="test-form">
        <el-form :model="testForm" label-width="100px">
          <el-form-item label="测试URL">
            <el-input v-model="testForm.url" placeholder="请输入要测试的URL" />
          </el-form-item>
          <el-form-item label="XPath">
            <el-input
              v-model="testForm.xpath"
              type="textarea"
              :rows="3"
              readonly
            />
          </el-form-item>
        </el-form>
        
        <div class="test-actions">
          <el-button type="primary" @click="runTest" :loading="testLoading">
            开始测试
          </el-button>
        </div>
        
        <div v-if="testResult" class="test-result">
          <h4>测试结果：</h4>
          <el-input
            v-model="testResult"
            type="textarea"
            :rows="6"
            readonly
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  Edit, 
  Delete, 
  VideoPlay, 
  DocumentCopy 
} from '@element-plus/icons-vue'
import { useXPathStore } from '@/stores/xpath'
import type { XPathConfig } from '@/stores/xpath'
import { formatDate } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const xpathStore = useXPathStore()

const loading = ref(false)
const config = ref<XPathConfig | null>(null)

// 测试对话框
const testDialogVisible = ref(false)
const testLoading = ref(false)
const testResult = ref('')
const testForm = reactive({
  url: '',
  xpath: ''
})

// 获取提取类型标签颜色
const getExtractTypeTag = (type: string) => {
  const tagMap: Record<string, string> = {
    text: 'primary',
    html: 'success',
    attr: 'warning',
    href: 'info'
  }
  return tagMap[type] || 'default'
}

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

// 获取配置详情
const fetchConfig = async () => {
  const id = route.params.id as string
  if (!id) {
    ElMessage.error('配置ID不能为空')
    goBack()
    return
  }

  try {
    loading.value = true
    const result = await xpathStore.getXPathConfig(id)
    if (result) {
      config.value = result
    } else {
      ElMessage.error('配置不存在')
      goBack()
    }
  } catch (error) {
    console.error('Fetch config error:', error)
    ElMessage.error('获取配置失败')
    goBack()
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/xpath')
}

// 编辑
const handleEdit = () => {
  if (config.value) {
    router.push(`/xpath/${config.value.id}/edit`)
  }
}

// 测试
const handleTest = () => {
  if (config.value) {
    testForm.xpath = config.value.xpath
    testForm.url = ''
    testResult.value = ''
    testDialogVisible.value = true
  }
}

// 运行测试
const runTest = async () => {
  if (!testForm.url) {
    ElMessage.warning('请输入测试URL')
    return
  }
  
  try {
    testLoading.value = true
    const result = await xpathStore.testXPath({
      url: testForm.url,
      xpath: testForm.xpath,
      extractType: config.value?.extractType,
      attrName: config.value?.attrName,
      processing: config.value?.processing
    })
    
    if (result.success) {
      testResult.value = result.data || '无匹配结果'
      ElMessage.success('测试完成')
    } else {
      testResult.value = `测试失败: ${result.error}`
      ElMessage.error('测试失败')
    }
  } catch (error) {
    console.error('Test error:', error)
    testResult.value = '测试过程中发生错误'
    ElMessage.error('测试失败')
  } finally {
    testLoading.value = false
  }
}

// 复制XPath
const copyXPath = async () => {
  if (config.value?.xpath) {
    try {
      await navigator.clipboard.writeText(config.value.xpath)
      ElMessage.success('XPath已复制到剪贴板')
    } catch (error) {
      console.error('Copy error:', error)
      ElMessage.error('复制失败')
    }
  }
}

// 删除
const handleDelete = async () => {
  if (!config.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.value.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const success = await xpathStore.deleteXPathConfig(config.value.id)
    if (success) {
      ElMessage.success('删除成功')
      goBack()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.xpath-detail {
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

.config-content {
  padding: 20px 0;
}

.section {
  margin: 30px 0;
}

.section h3 {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 16px;
  font-weight: 600;
}

.description {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.xpath-container {
  position: relative;
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
}

.xpath-code {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #303133;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.copy-btn {
  position: absolute;
  top: 10px;
  right: 10px;
}

.attr-name {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  background-color: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  color: #e6a23c;
}

.processing-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.test-form {
  padding: 20px 0;
}

.test-actions {
  margin: 20px 0;
  text-align: center;
}

.test-result {
  margin-top: 20px;
}

.test-result h4 {
  margin: 0 0 10px 0;
  color: #606266;
}
</style>