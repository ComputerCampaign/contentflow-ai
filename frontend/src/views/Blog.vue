<template>
  <div class="blog-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1>博客预览</h1>
          <p>浏览和管理采集的博客内容</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showPublishDialog = true">
            <i class="fas fa-plus"></i>
            发布文章
          </el-button>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文章标题或内容"
          prefix-icon="Search"
          style="width: 300px"
          clearable
        />
        <el-select v-model="categoryFilter" placeholder="分类筛选" style="width: 120px">
          <el-option label="全部" value=""></el-option>
          <el-option label="技术" value="tech"></el-option>
          <el-option label="生活" value="life"></el-option>
          <el-option label="教程" value="tutorial"></el-option>
          <el-option label="新闻" value="news"></el-option>
        </el-select>
        <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px">
          <el-option label="全部" value=""></el-option>
          <el-option label="已发布" value="published"></el-option>
          <el-option label="草稿" value="draft"></el-option>
          <el-option label="待审核" value="pending"></el-option>
        </el-select>
      </div>
      <div class="filter-right">
        <el-button-group>
          <el-button
            :type="viewMode === 'grid' ? 'primary' : 'default'"
            @click="viewMode = 'grid'"
          >
            <i class="fas fa-th"></i>
          </el-button>
          <el-button
            :type="viewMode === 'list' ? 'primary' : 'default'"
            @click="viewMode = 'list'"
          >
            <i class="fas fa-list"></i>
          </el-button>
        </el-button-group>
        <el-button @click="refreshBlogs">
          <i class="fas fa-sync-alt"></i>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 博客列表 -->
    <div class="blog-container">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="blog-grid">
        <div
          v-for="blog in filteredBlogs"
          :key="blog.id"
          class="blog-card"
          @click="viewBlog(blog)"
        >
          <div class="blog-image">
            <img v-if="blog.image" :src="blog.image" :alt="blog.title">
            <div v-else class="placeholder-image">
              <i class="fas fa-image"></i>
            </div>
            <div class="blog-overlay">
              <div class="blog-actions">
                <el-button type="primary" size="small" @click.stop="editBlog(blog)">
                  <i class="fas fa-edit"></i>
                </el-button>
                <el-button type="success" size="small" @click.stop="previewBlog(blog)">
                  <i class="fas fa-eye"></i>
                </el-button>
                <el-button type="danger" size="small" @click.stop="deleteBlog(blog)">
                  <i class="fas fa-trash"></i>
                </el-button>
              </div>
            </div>
          </div>
          <div class="blog-content">
            <div class="blog-meta">
              <span class="blog-category" :class="blog.category">
                {{ getCategoryText(blog.category) }}
              </span>
              <span class="blog-date">{{ formatDate(blog.publishedAt) }}</span>
            </div>
            <h3 class="blog-title">{{ blog.title }}</h3>
            <p class="blog-excerpt">{{ blog.excerpt }}</p>
            <div class="blog-footer">
              <div class="blog-stats">
                <span class="stat-item">
                  <i class="fas fa-eye"></i>
                  {{ blog.views }}
                </span>
                <span class="stat-item">
                  <i class="fas fa-heart"></i>
                  {{ blog.likes }}
                </span>
                <span class="stat-item">
                  <i class="fas fa-comment"></i>
                  {{ blog.comments }}
                </span>
              </div>
              <div class="blog-status" :class="blog.status">
                {{ getStatusText(blog.status) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="blog-list">
        <div
          v-for="blog in filteredBlogs"
          :key="blog.id"
          class="blog-item"
          @click="viewBlog(blog)"
        >
          <div class="blog-thumbnail">
            <img v-if="blog.image" :src="blog.image" :alt="blog.title">
            <div v-else class="placeholder-thumbnail">
              <i class="fas fa-image"></i>
            </div>
          </div>
          <div class="blog-info">
            <div class="blog-header">
              <h3 class="blog-title">{{ blog.title }}</h3>
              <div class="blog-actions">
                <el-button type="text" @click.stop="editBlog(blog)">
                  <i class="fas fa-edit"></i>
                </el-button>
                <el-button type="text" @click.stop="previewBlog(blog)">
                  <i class="fas fa-eye"></i>
                </el-button>
                <el-button type="text" @click.stop="deleteBlog(blog)">
                  <i class="fas fa-trash"></i>
                </el-button>
              </div>
            </div>
            <div class="blog-meta">
              <span class="blog-category" :class="blog.category">
                {{ getCategoryText(blog.category) }}
              </span>
              <span class="blog-author">{{ blog.author }}</span>
              <span class="blog-date">{{ formatDate(blog.publishedAt) }}</span>
              <span class="blog-status" :class="blog.status">
                {{ getStatusText(blog.status) }}
              </span>
            </div>
            <p class="blog-excerpt">{{ blog.excerpt }}</p>
            <div class="blog-stats">
              <span class="stat-item">
                <i class="fas fa-eye"></i>
                {{ blog.views }} 阅读
              </span>
              <span class="stat-item">
                <i class="fas fa-heart"></i>
                {{ blog.likes }} 点赞
              </span>
              <span class="stat-item">
                <i class="fas fa-comment"></i>
                {{ blog.comments }} 评论
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredBlogs.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-blog"></i>
        </div>
        <h3>暂无博客文章</h3>
        <p>开始创建您的第一篇博客文章</p>
        <el-button type="primary" @click="showPublishDialog = true">
          发布文章
        </el-button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="filteredBlogs.length > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="totalBlogs"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 博客详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="selectedBlog?.title"
      width="80%"
      top="5vh"
      class="blog-detail-dialog"
    >
      <div v-if="selectedBlog" class="blog-detail">
        <div class="blog-detail-header">
          <div class="blog-detail-meta">
            <span class="category" :class="selectedBlog.category">
              {{ getCategoryText(selectedBlog.category) }}
            </span>
            <span class="author">作者: {{ selectedBlog.author }}</span>
            <span class="date">{{ formatDate(selectedBlog.publishedAt) }}</span>
            <span class="status" :class="selectedBlog.status">
              {{ getStatusText(selectedBlog.status) }}
            </span>
          </div>
          <div class="blog-detail-stats">
            <span class="stat">
              <i class="fas fa-eye"></i>
              {{ selectedBlog.views }}
            </span>
            <span class="stat">
              <i class="fas fa-heart"></i>
              {{ selectedBlog.likes }}
            </span>
            <span class="stat">
              <i class="fas fa-comment"></i>
              {{ selectedBlog.comments }}
            </span>
          </div>
        </div>
        
        <div v-if="selectedBlog.image" class="blog-detail-image">
          <img :src="selectedBlog.image" :alt="selectedBlog.title">
        </div>
        
        <div class="blog-detail-content">
          <div v-html="selectedBlog.content"></div>
        </div>
        
        <div class="blog-detail-tags">
          <el-tag
            v-for="tag in selectedBlog.tags"
            :key="tag"
            type="info"
            size="small"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button type="primary" @click="editBlog(selectedBlog)">
            编辑文章
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 发布文章对话框 -->
    <el-dialog
      v-model="showPublishDialog"
      title="发布新文章"
      width="600px"
      :before-close="handlePublishDialogClose"
    >
      <el-form
        ref="publishFormRef"
        :model="publishForm"
        :rules="publishRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="publishForm.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="publishForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="技术" value="tech"></el-option>
            <el-option label="生活" value="life"></el-option>
            <el-option label="教程" value="tutorial"></el-option>
            <el-option label="新闻" value="news"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="publishForm.author" placeholder="请输入作者名称" />
        </el-form-item>
        <el-form-item label="摘要" prop="excerpt">
          <el-input
            v-model="publishForm.excerpt"
            type="textarea"
            :rows="3"
            placeholder="请输入文章摘要"
          />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="publishForm.tagsInput" placeholder="请输入标签，用逗号分隔" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="publishForm.content"
            type="textarea"
            :rows="8"
            placeholder="请输入文章内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showPublishDialog = false">取消</el-button>
          <el-button @click="saveDraft" :loading="publishing">
            保存草稿
          </el-button>
          <el-button type="primary" @click="publishBlog" :loading="publishing">
            发布文章
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// 响应式数据
const searchQuery = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(12)
const showDetailDialog = ref(false)
const showPublishDialog = ref(false)
const publishing = ref(false)
const selectedBlog = ref(null)

// 发布表单
const publishForm = ref({
  title: '',
  category: '',
  author: '',
  excerpt: '',
  content: '',
  tagsInput: ''
})

const publishFormRef = ref(null)

// 表单验证规则
const publishRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择文章分类', trigger: 'change' }
  ],
  author: [
    { required: true, message: '请输入作者名称', trigger: 'blur' }
  ],
  excerpt: [
    { required: true, message: '请输入文章摘要', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' }
  ]
}

// 模拟博客数据
const blogs = ref([
  {
    id: 1,
    title: 'Vue 3 Composition API 深度解析',
    excerpt: '深入了解 Vue 3 Composition API 的设计理念和最佳实践，掌握现代 Vue 开发技巧。',
    content: '<h2>Vue 3 Composition API 简介</h2><p>Vue 3 引入了全新的 Composition API，为开发者提供了更灵活的组件逻辑组织方式...</p>',
    category: 'tech',
    author: '张三',
    publishedAt: new Date(Date.now() - 86400000),
    status: 'published',
    views: 1234,
    likes: 89,
    comments: 23,
    image: 'https://picsum.photos/400/250?random=1',
    tags: ['Vue', 'JavaScript', '前端开发']
  },
  {
    id: 2,
    title: 'Python 爬虫实战教程',
    excerpt: '从零开始学习 Python 爬虫，掌握数据采集的核心技术和反爬虫策略。',
    content: '<h2>爬虫基础知识</h2><p>网络爬虫是一种自动化程序，用于从网站上提取数据...</p>',
    category: 'tutorial',
    author: '李四',
    publishedAt: new Date(Date.now() - 172800000),
    status: 'published',
    views: 2156,
    likes: 156,
    comments: 45,
    image: 'https://picsum.photos/400/250?random=2',
    tags: ['Python', '爬虫', '数据采集']
  },
  {
    id: 3,
    title: '现代前端开发工具链',
    excerpt: '探索现代前端开发中的工具链配置，包括构建工具、代码质量检查和自动化部署。',
    content: '<h2>前端工具链概述</h2><p>现代前端开发离不开各种工具的支持...</p>',
    category: 'tech',
    author: '王五',
    publishedAt: new Date(Date.now() - 259200000),
    status: 'published',
    views: 987,
    likes: 67,
    comments: 12,
    image: 'https://picsum.photos/400/250?random=3',
    tags: ['前端', '工具链', 'Webpack']
  },
  {
    id: 4,
    title: '人工智能在内容创作中的应用',
    excerpt: 'AI 技术如何改变内容创作行业，探讨机器学习在文本生成和编辑中的实际应用。',
    content: '<h2>AI 内容创作的现状</h2><p>人工智能技术正在革命性地改变内容创作领域...</p>',
    category: 'tech',
    author: '赵六',
    publishedAt: new Date(Date.now() - 345600000),
    status: 'draft',
    views: 0,
    likes: 0,
    comments: 0,
    image: 'https://picsum.photos/400/250?random=4',
    tags: ['AI', '人工智能', '内容创作']
  },
  {
    id: 5,
    title: '远程工作的生活平衡艺术',
    excerpt: '分享远程工作中如何保持工作与生活的平衡，提高工作效率和生活质量。',
    content: '<h2>远程工作的挑战</h2><p>远程工作带来了前所未有的灵活性，但也面临着新的挑战...</p>',
    category: 'life',
    author: '孙七',
    publishedAt: new Date(Date.now() - 432000000),
    status: 'published',
    views: 1567,
    likes: 234,
    comments: 67,
    image: 'https://picsum.photos/400/250?random=5',
    tags: ['远程工作', '生活平衡', '效率']
  },
  {
    id: 6,
    title: 'Docker 容器化部署指南',
    excerpt: '学习如何使用 Docker 进行应用容器化，简化部署流程和环境管理。',
    content: '<h2>Docker 基础概念</h2><p>Docker 是一个开源的容器化平台...</p>',
    category: 'tutorial',
    author: '周八',
    publishedAt: new Date(Date.now() - 518400000),
    status: 'pending',
    views: 0,
    likes: 0,
    comments: 0,
    image: 'https://picsum.photos/400/250?random=6',
    tags: ['Docker', '容器化', 'DevOps']
  }
])

// 计算属性
const filteredBlogs = computed(() => {
  let filtered = blogs.value
  
  if (searchQuery.value) {
    filtered = filtered.filter(blog => 
      blog.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      blog.excerpt.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  if (categoryFilter.value) {
    filtered = filtered.filter(blog => blog.category === categoryFilter.value)
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(blog => blog.status === statusFilter.value)
  }
  
  return filtered
})

const totalBlogs = computed(() => filteredBlogs.value.length)

// 方法
const getCategoryText = (category) => {
  const texts = {
    tech: '技术',
    life: '生活',
    tutorial: '教程',
    news: '新闻'
  }
  return texts[category] || '未分类'
}

const getStatusText = (status) => {
  const texts = {
    published: '已发布',
    draft: '草稿',
    pending: '待审核'
  }
  return texts[status] || '未知状态'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const refreshBlogs = () => {
  ElMessage.success('博客列表已刷新')
  // 这里可以添加实际的刷新逻辑
}

const viewBlog = (blog) => {
  selectedBlog.value = blog
  showDetailDialog.value = true
}

const editBlog = (blog) => {
  ElMessage.info(`编辑文章: ${blog.title}`)
  // 这里可以添加编辑逻辑
}

const previewBlog = (blog) => {
  // 在新窗口中预览博客
  const previewWindow = window.open('', '_blank')
  previewWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>${blog.title}</title>
      <meta charset="utf-8">
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .meta { color: #666; margin-bottom: 20px; }
        .content { margin-top: 30px; }
        img { max-width: 100%; height: auto; }
      </style>
    </head>
    <body>
      <h1>${blog.title}</h1>
      <div class="meta">
        <p><strong>作者:</strong> ${blog.author} | <strong>发布时间:</strong> ${formatDate(blog.publishedAt)} | <strong>分类:</strong> ${getCategoryText(blog.category)}</p>
        <p><strong>摘要:</strong> ${blog.excerpt}</p>
      </div>
      ${blog.image ? `<img src="${blog.image}" alt="${blog.title}" style="width: 100%; margin: 20px 0;">` : ''}
      <div class="content">${blog.content}</div>
    </body>
    </html>
  `)
  previewWindow.document.close()
}

const deleteBlog = async (blog) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文章 "${blog.title}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = blogs.value.findIndex(b => b.id === blog.id)
    if (index > -1) {
      blogs.value.splice(index, 1)
      ElMessage.success('文章删除成功')
    }
  } catch (error) {
    // 用户取消删除
  }
}

const publishBlog = async () => {
  if (!publishFormRef.value) return
  
  try {
    await publishFormRef.value.validate()
    publishing.value = true
    
    // 模拟发布文章
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newBlog = {
      id: Date.now(),
      title: publishForm.value.title,
      excerpt: publishForm.value.excerpt,
      content: publishForm.value.content,
      category: publishForm.value.category,
      author: publishForm.value.author,
      publishedAt: new Date(),
      status: 'published',
      views: 0,
      likes: 0,
      comments: 0,
      image: `https://picsum.photos/400/250?random=${Date.now()}`,
      tags: publishForm.value.tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag)
    }
    
    blogs.value.unshift(newBlog)
    
    ElMessage.success('文章发布成功')
    showPublishDialog.value = false
    resetPublishForm()
  } catch (error) {
    console.error('发布文章失败:', error)
  } finally {
    publishing.value = false
  }
}

const saveDraft = async () => {
  if (!publishFormRef.value) return
  
  try {
    await publishFormRef.value.validate()
    publishing.value = true
    
    // 模拟保存草稿
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newBlog = {
      id: Date.now(),
      title: publishForm.value.title,
      excerpt: publishForm.value.excerpt,
      content: publishForm.value.content,
      category: publishForm.value.category,
      author: publishForm.value.author,
      publishedAt: new Date(),
      status: 'draft',
      views: 0,
      likes: 0,
      comments: 0,
      image: `https://picsum.photos/400/250?random=${Date.now()}`,
      tags: publishForm.value.tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag)
    }
    
    blogs.value.unshift(newBlog)
    
    ElMessage.success('草稿保存成功')
    showPublishDialog.value = false
    resetPublishForm()
  } catch (error) {
    console.error('保存草稿失败:', error)
  } finally {
    publishing.value = false
  }
}

const resetPublishForm = () => {
  publishForm.value = {
    title: '',
    category: '',
    author: '',
    excerpt: '',
    content: '',
    tagsInput: ''
  }
  if (publishFormRef.value) {
    publishFormRef.value.resetFields()
  }
}

const handlePublishDialogClose = () => {
  resetPublishForm()
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
.blog-page {
  padding: 0;
}

// 页面头部
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 40px;
  margin-bottom: 24px;
  color: white;
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .header-left {
    h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
      font-weight: 600;
    }
    
    p {
      margin: 0;
      opacity: 0.9;
      font-size: 16px;
    }
  }
}

// 筛选区域
.filter-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: var(--shadow-light);
  
  .filter-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .filter-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

// 博客容器
.blog-container {
  margin-bottom: 24px;
}

// 网格视图
.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.blog-card {
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-base);
    
    .blog-overlay {
      opacity: 1;
    }
  }
}

.blog-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }
  
  .placeholder-image {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-placeholder);
    font-size: 48px;
  }
  
  .blog-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    
    .blog-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.blog-content {
  padding: 20px;
}

.blog-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 12px;
  
  .blog-category {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 500;
    
    &.tech {
      background: rgba(64, 158, 255, 0.1);
      color: var(--primary-color);
    }
    
    &.life {
      background: rgba(103, 194, 58, 0.1);
      color: var(--success-color);
    }
    
    &.tutorial {
      background: rgba(230, 162, 60, 0.1);
      color: var(--warning-color);
    }
    
    &.news {
      background: rgba(245, 108, 108, 0.1);
      color: var(--danger-color);
    }
  }
  
  .blog-date {
    color: var(--text-secondary);
  }
}

.blog-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-excerpt {
  color: var(--text-regular);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .blog-stats {
    display: flex;
    gap: 16px;
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: var(--text-secondary);
      
      i {
        font-size: 11px;
      }
    }
  }
  
  .blog-status {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    
    &.published {
      background: rgba(103, 194, 58, 0.1);
      color: var(--success-color);
    }
    
    &.draft {
      background: rgba(144, 147, 153, 0.1);
      color: var(--info-color);
    }
    
    &.pending {
      background: rgba(230, 162, 60, 0.1);
      color: var(--warning-color);
    }
  }
}

// 列表视图
.blog-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.blog-item {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  gap: 20px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  .blog-thumbnail {
    width: 120px;
    height: 80px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .placeholder-thumbnail {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-placeholder);
      font-size: 24px;
    }
  }
  
  .blog-info {
    flex: 1;
    
    .blog-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 8px;
      
      .blog-title {
        margin: 0;
        font-size: 18px;
        flex: 1;
      }
      
      .blog-actions {
        display: flex;
        gap: 4px;
        margin-left: 16px;
      }
    }
    
    .blog-meta {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 12px;
      font-size: 12px;
      
      .blog-category {
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 500;
      }
      
      .blog-author,
      .blog-date {
        color: var(--text-secondary);
      }
      
      .blog-status {
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 500;
      }
    }
    
    .blog-excerpt {
      margin-bottom: 12px;
      -webkit-line-clamp: 2;
    }
    
    .blog-stats {
      display: flex;
      gap: 16px;
      
      .stat-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
}

// 空状态
.empty-state {
  text-align: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 64px;
    color: var(--text-placeholder);
    margin-bottom: 16px;
  }
  
  h3 {
    margin: 0 0 8px 0;
    color: var(--text-primary);
  }
  
  p {
    margin: 0 0 24px 0;
    color: var(--text-secondary);
  }
}

// 分页
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

// 博客详情
.blog-detail {
  .blog-detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-light);
    
    .blog-detail-meta {
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 13px;
      
      .category {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
      }
      
      .author,
      .date {
        color: var(--text-secondary);
      }
      
      .status {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
      }
    }
    
    .blog-detail-stats {
      display: flex;
      gap: 16px;
      
      .stat {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: var(--text-secondary);
      }
    }
  }
  
  .blog-detail-image {
    margin-bottom: 24px;
    
    img {
      width: 100%;
      max-height: 400px;
      object-fit: cover;
      border-radius: 8px;
    }
  }
  
  .blog-detail-content {
    line-height: 1.8;
    color: var(--text-primary);
    margin-bottom: 24px;
    
    :deep(h1),
    :deep(h2),
    :deep(h3),
    :deep(h4),
    :deep(h5),
    :deep(h6) {
      margin: 24px 0 16px 0;
      color: var(--text-primary);
    }
    
    :deep(p) {
      margin: 16px 0;
    }
    
    :deep(img) {
      max-width: 100%;
      height: auto;
      border-radius: 4px;
    }
    
    :deep(code) {
      background: var(--bg-secondary);
      padding: 2px 4px;
      border-radius: 3px;
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 0.9em;
    }
    
    :deep(pre) {
      background: var(--bg-secondary);
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      
      code {
        background: none;
        padding: 0;
      }
    }
  }
  
  .blog-detail-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

// 对话框样式
:deep(.blog-detail-dialog) {
  .el-dialog__body {
    padding: 20px 24px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    .header-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
  }
  
  .filter-section {
    flex-direction: column;
    gap: 16px;
    
    .filter-left,
    .filter-right {
      width: 100%;
      justify-content: space-between;
    }
  }
  
  .blog-grid {
    grid-template-columns: 1fr;
  }
  
  .blog-item {
    flex-direction: column;
    
    .blog-thumbnail {
      width: 100%;
      height: 150px;
    }
    
    .blog-info {
      .blog-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
        
        .blog-actions {
          margin-left: 0;
        }
      }
      
      .blog-meta {
        flex-wrap: wrap;
      }
    }
  }
  
  .blog-detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    
    .blog-detail-meta {
      flex-wrap: wrap;
    }
  }
}
</style>