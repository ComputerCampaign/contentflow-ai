<template>
  <div class="crawler-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>爬虫配置</h1>
        <p>配置和管理爬虫规则</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <i class="fas fa-plus"></i>
          新建配置
        </el-button>
      </div>
    </div>

    <!-- 配置列表 -->
    <div class="config-grid">
      <div
        v-for="config in configs"
        :key="config.id"
        class="config-card"
      >
        <div class="config-header">
          <h3>{{ config.name }}</h3>
          <el-switch
            v-model="config.enabled"
            @change="toggleConfig(config)"
          />
        </div>
        <p class="config-description">{{ config.description }}</p>
        <div class="config-details">
          <div class="detail-item">
            <span class="label">目标网站:</span>
            <span class="value">{{ config.targetUrl }}</span>
          </div>
          <div class="detail-item">
            <span class="label">采集频率:</span>
            <span class="value">{{ config.frequency }}</span>
          </div>
          <div class="detail-item">
            <span class="label">最后运行:</span>
            <span class="value">{{ formatTime(config.lastRun) }}</span>
          </div>
        </div>
        <div class="config-actions">
          <el-button size="small" @click="editConfig(config)">
            <i class="fas fa-edit"></i>
            编辑
          </el-button>
          <el-button size="small" @click="testConfig(config)">
            <i class="fas fa-play"></i>
            测试
          </el-button>
          <el-button size="small" type="danger" @click="deleteConfig(config)">
            <i class="fas fa-trash"></i>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 创建配置对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建爬虫配置"
      width="600px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        label-width="100px"
      >
        <el-form-item label="配置名称">
          <el-input v-model="createForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="目标网站">
          <el-input v-model="createForm.targetUrl" placeholder="请输入目标网站URL" />
        </el-form-item>
        <el-form-item label="采集频率">
          <el-select v-model="createForm.frequency" style="width: 100%">
            <el-option label="每小时" value="hourly"></el-option>
            <el-option label="每天" value="daily"></el-option>
            <el-option label="每周" value="weekly"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="配置描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createConfig">
            创建配置
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const showCreateDialog = ref(false)
const createFormRef = ref(null)

const createForm = ref({
  name: '',
  targetUrl: '',
  frequency: '',
  description: ''
})

const configs = ref([
  {
    id: 1,
    name: '技术博客采集',
    description: '采集主流技术博客的最新文章',
    targetUrl: 'https://example-blog.com',
    frequency: '每天',
    enabled: true,
    lastRun: new Date(Date.now() - 3600000)
  },
  {
    id: 2,
    name: '新闻资讯采集',
    description: '采集科技新闻和资讯',
    targetUrl: 'https://example-news.com',
    frequency: '每小时',
    enabled: false,
    lastRun: new Date(Date.now() - 86400000)
  }
])

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

const toggleConfig = (config) => {
  ElMessage.success(`配置 "${config.name}" 已${config.enabled ? '启用' : '禁用'}`)
}

const editConfig = (config) => {
  ElMessage.info(`编辑配置: ${config.name}`)
}

const testConfig = (config) => {
  ElMessage.success(`正在测试配置: ${config.name}`)
}

const deleteConfig = (config) => {
  const index = configs.value.findIndex(c => c.id === config.id)
  if (index > -1) {
    configs.value.splice(index, 1)
    ElMessage.success('配置删除成功')
  }
}

const createConfig = () => {
  const newConfig = {
    id: Date.now(),
    ...createForm.value,
    enabled: true,
    lastRun: new Date()
  }
  configs.value.push(newConfig)
  ElMessage.success('配置创建成功')
  showCreateDialog.value = false
  createForm.value = {
    name: '',
    targetUrl: '',
    frequency: '',
    description: ''
  }
}
</script>

<style lang="scss" scoped>
.crawler-page {
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

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.config-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  .config-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
  
  .config-description {
    color: var(--text-regular);
    font-size: 14px;
    margin-bottom: 16px;
  }
  
  .config-details {
    margin-bottom: 16px;
    
    .detail-item {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      font-size: 13px;
      
      .label {
        width: 80px;
        color: var(--text-secondary);
      }
      
      .value {
        color: var(--text-primary);
      }
    }
  }
  
  .config-actions {
    display: flex;
    gap: 8px;
  }
}
</style>