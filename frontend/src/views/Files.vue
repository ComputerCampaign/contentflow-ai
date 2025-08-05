<template>
  <div class="files-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>文件管理</h1>
        <p>管理爬取的文件和生成的内容</p>
      </div>
      <div class="header-right">
        <el-upload
          :show-file-list="false"
          :before-upload="handleUpload"
          multiple
        >
          <el-button type="primary">
            <i class="fas fa-upload"></i>
            上传文件
          </el-button>
        </el-upload>
      </div>
    </div>

    <!-- 文件统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-file"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalFiles }}</h3>
          <p>总文件数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-hdd"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatSize(stats.totalSize) }}</h3>
          <p>总大小</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-download"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.todayDownloads }}</h3>
          <p>今日下载</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-folder"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.folders }}</h3>
          <p>文件夹数</p>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文件..."
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <i class="fas fa-search"></i>
          </template>
        </el-input>
        <el-select v-model="filterType" placeholder="文件类型" style="width: 120px">
          <el-option label="全部" value=""></el-option>
          <el-option label="图片" value="image"></el-option>
          <el-option label="文档" value="document"></el-option>
          <el-option label="视频" value="video"></el-option>
          <el-option label="其他" value="other"></el-option>
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-button-group>
          <el-button
            :type="viewMode === 'grid' ? 'primary' : ''"
            @click="viewMode = 'grid'"
          >
            <i class="fas fa-th"></i>
          </el-button>
          <el-button
            :type="viewMode === 'list' ? 'primary' : ''"
            @click="viewMode = 'list'"
          >
            <i class="fas fa-list"></i>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="files-container">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="files-grid">
        <div
          v-for="file in filteredFiles"
          :key="file.id"
          class="file-card"
          @click="selectFile(file)"
          :class="{ selected: selectedFiles.includes(file.id) }"
        >
          <div class="file-preview">
            <i :class="getFileIcon(file.type)" :style="{ color: getFileColor(file.type) }"></i>
          </div>
          <div class="file-info">
            <h4>{{ file.name }}</h4>
            <p>{{ formatSize(file.size) }}</p>
            <p>{{ formatTime(file.createdAt) }}</p>
          </div>
          <div class="file-actions">
            <el-button size="small" @click.stop="downloadFile(file)">
              <i class="fas fa-download"></i>
            </el-button>
            <el-button size="small" @click.stop="deleteFile(file)" type="danger">
              <i class="fas fa-trash"></i>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="files-table">
        <el-table
          :data="filteredFiles"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="file-name">
                <i :class="getFileIcon(row.type)" :style="{ color: getFileColor(row.type) }"></i>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ getTypeName(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="150">
            <template #default="{ row }">
              {{ formatTime(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="downloadFile(row)">
                <i class="fas fa-download"></i>
              </el-button>
              <el-button size="small" type="danger" @click="deleteFile(row)">
                <i class="fas fa-trash"></i>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="filteredFiles.length"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const searchKeyword = ref('')
const filterType = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedFiles = ref([])

const stats = ref({
  totalFiles: 1247,
  totalSize: 2.5 * 1024 * 1024 * 1024, // 2.5GB
  todayDownloads: 156,
  folders: 23
})

const fileList = ref([
  {
    id: 1,
    name: 'article_001.pdf',
    type: 'document',
    size: 2.5 * 1024 * 1024,
    createdAt: new Date(Date.now() - 3600000),
    url: '/files/article_001.pdf'
  },
  {
    id: 2,
    name: 'screenshot_001.png',
    type: 'image',
    size: 1.2 * 1024 * 1024,
    createdAt: new Date(Date.now() - 7200000),
    url: '/files/screenshot_001.png'
  },
  {
    id: 3,
    name: 'data_export.xlsx',
    type: 'document',
    size: 856 * 1024,
    createdAt: new Date(Date.now() - 10800000),
    url: '/files/data_export.xlsx'
  },
  {
    id: 4,
    name: 'video_tutorial.mp4',
    type: 'video',
    size: 45 * 1024 * 1024,
    createdAt: new Date(Date.now() - 14400000),
    url: '/files/video_tutorial.mp4'
  }
])

const filteredFiles = computed(() => {
  return fileList.value.filter(file => {
    const nameMatch = !searchKeyword.value || 
      file.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    const typeMatch = !filterType.value || file.type === filterType.value
    return nameMatch && typeMatch
  })
})

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

const getFileIcon = (type) => {
  const iconMap = {
    image: 'fas fa-image',
    document: 'fas fa-file-alt',
    video: 'fas fa-video',
    audio: 'fas fa-music',
    archive: 'fas fa-file-archive',
    other: 'fas fa-file'
  }
  return iconMap[type] || iconMap.other
}

const getFileColor = (type) => {
  const colorMap = {
    image: '#67C23A',
    document: '#409EFF',
    video: '#E6A23C',
    audio: '#F56C6C',
    archive: '#909399',
    other: '#909399'
  }
  return colorMap[type] || colorMap.other
}

const getTypeName = (type) => {
  const nameMap = {
    image: '图片',
    document: '文档',
    video: '视频',
    audio: '音频',
    archive: '压缩包',
    other: '其他'
  }
  return nameMap[type] || nameMap.other
}

const selectFile = (file) => {
  const index = selectedFiles.value.indexOf(file.id)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(file.id)
  }
}

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection.map(item => item.id)
}

const handleUpload = (file) => {
  const newFile = {
    id: Date.now(),
    name: file.name,
    type: getFileTypeFromName(file.name),
    size: file.size,
    createdAt: new Date(),
    url: URL.createObjectURL(file)
  }
  fileList.value.unshift(newFile)
  ElMessage.success(`文件 "${file.name}" 上传成功`)
  return false // 阻止自动上传
}

const getFileTypeFromName = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(ext)) {
    return 'image'
  } else if (['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'].includes(ext)) {
    return 'document'
  } else if (['mp4', 'avi', 'mov', 'wmv', 'flv'].includes(ext)) {
    return 'video'
  } else if (['mp3', 'wav', 'flac', 'aac'].includes(ext)) {
    return 'audio'
  } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
    return 'archive'
  }
  return 'other'
}

const downloadFile = (file) => {
  // 模拟下载
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  link.click()
  ElMessage.success(`开始下载 "${file.name}"`)
}

const deleteFile = (file) => {
  const index = fileList.value.findIndex(f => f.id === file.id)
  if (index > -1) {
    fileList.value.splice(index, 1)
    ElMessage.success(`文件 "${file.name}" 删除成功`)
  }
}
</script>

<style lang="scss" scoped>
.files-page {
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

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  
  .toolbar-left {
    display: flex;
    gap: 12px;
  }
}

.files-container {
  margin-bottom: 20px;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.file-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  &.selected {
    border-color: var(--primary-color);
  }
  
  .file-preview {
    margin-bottom: 12px;
    
    i {
      font-size: 48px;
    }
  }
  
  .file-info {
    margin-bottom: 12px;
    
    h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
      word-break: break-all;
    }
    
    p {
      margin: 0;
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
  
  .file-actions {
    display: flex;
    gap: 8px;
    justify-content: center;
  }
}

.files-table {
  .file-name {
    display: flex;
    align-items: center;
    gap: 8px;
    
    i {
      font-size: 16px;
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
}
</style>