<template>
  <div class="content-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>内容生成</h1>
        <p>基于爬取数据生成高质量内容</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showGenerateDialog = true">
          <i class="fas fa-magic"></i>
          生成内容
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalGenerated }}</h3>
          <p>总生成数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.todayGenerated }}</h3>
          <p>今日生成</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.successRate }}%</h3>
          <p>成功率</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-star"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.avgQuality }}</h3>
          <p>平均质量</p>
        </div>
      </div>
    </div>

    <!-- 内容列表 -->
    <div class="content-section">
      <div class="section-header">
        <h2>生成历史</h2>
        <div class="filters">
          <el-select v-model="filterType" placeholder="内容类型" style="width: 120px">
            <el-option label="全部" value=""></el-option>
            <el-option label="文章" value="article"></el-option>
            <el-option label="摘要" value="summary"></el-option>
            <el-option label="标题" value="title"></el-option>
          </el-select>
          <el-select v-model="filterStatus" placeholder="状态" style="width: 100px">
            <el-option label="全部" value=""></el-option>
            <el-option label="成功" value="success"></el-option>
            <el-option label="失败" value="failed"></el-option>
          </el-select>
        </div>
      </div>
      
      <div class="content-list">
        <div
          v-for="item in filteredContent"
          :key="item.id"
          class="content-item"
        >
          <div class="item-header">
            <div class="item-info">
              <h3>{{ item.title }}</h3>
              <div class="item-meta">
                <el-tag :type="getTypeColor(item.type)" size="small">
                  {{ getTypeName(item.type) }}
                </el-tag>
                <el-tag :type="getStatusColor(item.status)" size="small">
                  {{ getStatusName(item.status) }}
                </el-tag>
                <span class="time">{{ formatTime(item.createdAt) }}</span>
              </div>
            </div>
            <div class="item-actions">
              <el-button size="small" @click="previewContent(item)">
                <i class="fas fa-eye"></i>
                预览
              </el-button>
              <el-button size="small" @click="editContent(item)">
                <i class="fas fa-edit"></i>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="deleteContent(item)">
                <i class="fas fa-trash"></i>
                删除
              </el-button>
            </div>
          </div>
          <p class="item-preview">{{ item.preview }}</p>
          <div class="item-stats">
            <span>字数: {{ item.wordCount }}</span>
            <span>质量评分: {{ item.qualityScore }}/10</span>
            <span>来源: {{ item.source }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成内容对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="生成内容"
      width="600px"
    >
      <el-form
        ref="generateFormRef"
        :model="generateForm"
        label-width="100px"
      >
        <el-form-item label="内容类型">
          <el-select v-model="generateForm.type" style="width: 100%">
            <el-option label="文章" value="article"></el-option>
            <el-option label="摘要" value="summary"></el-option>
            <el-option label="标题" value="title"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="generateForm.source" style="width: 100%">
            <el-option label="技术博客" value="tech-blog"></el-option>
            <el-option label="新闻资讯" value="news"></el-option>
            <el-option label="学术论文" value="paper"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="generateForm.keywords"
            placeholder="请输入关键词，多个关键词用逗号分隔"
          />
        </el-form-item>
        <el-form-item label="内容长度">
          <el-slider
            v-model="generateForm.length"
            :min="100"
            :max="2000"
            :step="100"
            show-stops
            show-input
          />
        </el-form-item>
        <el-form-item label="生成要求">
          <el-input
            v-model="generateForm.requirements"
            type="textarea"
            :rows="3"
            placeholder="请输入特殊要求或指导"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showGenerateDialog = false">取消</el-button>
          <el-button type="primary" @click="generateContent" :loading="generating">
            {{ generating ? '生成中...' : '开始生成' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 内容预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="previewItem?.title"
      width="800px"
    >
      <div v-if="previewItem" class="preview-content">
        <div class="preview-meta">
          <el-tag :type="getTypeColor(previewItem.type)">
            {{ getTypeName(previewItem.type) }}
          </el-tag>
          <span>{{ formatTime(previewItem.createdAt) }}</span>
          <span>质量评分: {{ previewItem.qualityScore }}/10</span>
        </div>
        <div class="preview-text">
          {{ previewItem.content }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const showGenerateDialog = ref(false)
const showPreviewDialog = ref(false)
const generating = ref(false)
const generateFormRef = ref(null)
const previewItem = ref(null)
const filterType = ref('')
const filterStatus = ref('')

const generateForm = ref({
  type: '',
  source: '',
  keywords: '',
  length: 500,
  requirements: ''
})

const stats = ref({
  totalGenerated: 1247,
  todayGenerated: 23,
  successRate: 94,
  avgQuality: 8.6
})

const contentList = ref([
  {
    id: 1,
    title: 'Vue 3 组合式API最佳实践',
    type: 'article',
    status: 'success',
    preview: 'Vue 3 引入的组合式API为开发者提供了更灵活的代码组织方式...',
    content: 'Vue 3 引入的组合式API为开发者提供了更灵活的代码组织方式，本文将详细介绍如何在实际项目中应用组合式API的最佳实践。',
    wordCount: 1200,
    qualityScore: 9.2,
    source: '技术博客',
    createdAt: new Date(Date.now() - 3600000)
  },
  {
    id: 2,
    title: 'AI技术发展趋势分析',
    type: 'summary',
    status: 'success',
    preview: '人工智能技术在2024年呈现出快速发展的态势...',
    content: '人工智能技术在2024年呈现出快速发展的态势，特别是在大语言模型、计算机视觉和自动驾驶等领域取得了重大突破。',
    wordCount: 800,
    qualityScore: 8.8,
    source: '新闻资讯',
    createdAt: new Date(Date.now() - 7200000)
  }
])

const filteredContent = computed(() => {
  return contentList.value.filter(item => {
    const typeMatch = !filterType.value || item.type === filterType.value
    const statusMatch = !filterStatus.value || item.status === filterStatus.value
    return typeMatch && statusMatch
  })
})

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

const getTypeName = (type) => {
  const typeMap = {
    article: '文章',
    summary: '摘要',
    title: '标题'
  }
  return typeMap[type] || type
}

const getTypeColor = (type) => {
  const colorMap = {
    article: 'primary',
    summary: 'success',
    title: 'warning'
  }
  return colorMap[type] || ''
}

const getStatusName = (status) => {
  const statusMap = {
    success: '成功',
    failed: '失败',
    pending: '处理中'
  }
  return statusMap[status] || status
}

const getStatusColor = (status) => {
  const colorMap = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return colorMap[status] || ''
}

const generateContent = async () => {
  generating.value = true
  try {
    // 模拟生成过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const newContent = {
      id: Date.now(),
      title: `生成的${getTypeName(generateForm.value.type)}`,
      type: generateForm.value.type,
      status: 'success',
      preview: '这是一段生成的内容预览...',
      content: '这是完整的生成内容...',
      wordCount: generateForm.value.length,
      qualityScore: (Math.random() * 2 + 8).toFixed(1),
      source: generateForm.value.source,
      createdAt: new Date()
    }
    
    contentList.value.unshift(newContent)
    ElMessage.success('内容生成成功')
    showGenerateDialog.value = false
    
    // 重置表单
    generateForm.value = {
      type: '',
      source: '',
      keywords: '',
      length: 500,
      requirements: ''
    }
  } catch (error) {
    ElMessage.error('内容生成失败')
  } finally {
    generating.value = false
  }
}

const previewContent = (item) => {
  previewItem.value = item
  showPreviewDialog.value = true
}

const editContent = (item) => {
  ElMessage.info(`编辑内容: ${item.title}`)
}

const deleteContent = (item) => {
  const index = contentList.value.findIndex(c => c.id === item.id)
  if (index > -1) {
    contentList.value.splice(index, 1)
    ElMessage.success('内容删除成功')
  }
}
</script>

<style lang="scss" scoped>
.content-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: var(--shadow-light);
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    
    i {
      font-size: 20px;
      color: white;
    }
  }
  
  .stat-content {
    h3 {
      margin: 0 0 4px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      font-size: 14px;
      color: var(--text-secondary);
    }
  }
}

.content-section {
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .filters {
      display: flex;
      gap: 12px;
    }
  }
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-item {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  .item-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12px;
    
    .item-info {
      flex: 1;
      
      h3 {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .item-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .time {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
    
    .item-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .item-preview {
    color: var(--text-regular);
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 12px;
  }
  
  .item-stats {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.preview-content {
  .preview-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-light);
    font-size: 14px;
    color: var(--text-secondary);
  }
  
  .preview-text {
    line-height: 1.8;
    color: var(--text-primary);
  }
}
</style>