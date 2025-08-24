<template>
  <div class="prompt-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Prompt管理</h1>
        <p class="page-description">管理AI内容生成的提示词模板</p>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          新建Prompt
        </el-button>
        <el-button type="success" :icon="Refresh" @click="loadPrompts" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-card>
        <el-form :model="searchForm" :inline="true">
          <el-form-item label="名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入Prompt名称"
              clearable
              style="width: 200px;"
            />
          </el-form-item>
          <el-form-item label="类型">
            <el-select
              v-model="searchForm.type"
              placeholder="选择类型"
              clearable
              style="width: 150px;"
            >
              <el-option label="内容生成" value="content" />
              <el-option label="标题生成" value="title" />
              <el-option label="摘要生成" value="summary" />
              <el-option label="关键词提取" value="keywords" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="选择状态"
              clearable
              style="width: 120px;"
            >
              <el-option label="启用" value="active" />
              <el-option label="禁用" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- Prompt列表 -->
    <div class="prompt-list">
      <el-card>
        <el-table
          :data="filteredPrompts"
          v-loading="loading"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="name" label="名称" width="200" />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="usageCount" label="使用次数" width="100" />
          <el-table-column prop="updatedAt" label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.updatedAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleView(row)">查看</el-button>
              <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
      


    
    <!-- 创建/编辑Prompt对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑Prompt' : '新建Prompt'"
      width="800px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入Prompt名称" />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-select v-model="formData.type" placeholder="选择类型" style="width: 100%;">
            <el-option label="内容生成" value="content" />
            <el-option label="标题生成" value="title" />
            <el-option label="摘要生成" value="summary" />
            <el-option label="关键词提取" value="keywords" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入Prompt描述"
          />
        </el-form-item>
        
        <el-form-item label="提示词" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="8"
            placeholder="请输入提示词内容，可以使用变量如 {title}, {content} 等"
          />
        </el-form-item>
        
        <el-form-item label="变量说明" prop="variables">
          <el-input
            v-model="formData.variables"
            type="textarea"
            :rows="3"
            placeholder="说明提示词中使用的变量，如：{title} - 文章标题, {content} - 文章内容"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'

interface Prompt {
  id?: number
  name: string
  type: string
  description: string
  content: string
  variables: string
  status: string
  createdAt?: string
  updatedAt?: string
  usageCount?: number
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索和筛选
const searchForm = ref({
  name: '',
  type: '',
  status: ''
})

// 表单数据
const formRef = ref()
const formData = ref<Prompt>({
  name: '',
  type: '',
  description: '',
  content: '',
  variables: '',
  status: 'active'
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入Prompt名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在2到50个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择Prompt类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入Prompt描述', trigger: 'blur' },
    { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入提示词内容', trigger: 'blur' },
    { min: 10, message: '提示词内容至少10个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// Prompt列表
const promptList = ref<Prompt[]>([])

// 类型选项
const typeOptions = [
  { label: '内容生成', value: 'content' },
  { label: '标题生成', value: 'title' },
  { label: '摘要生成', value: 'summary' },
  { label: '关键词提取', value: 'keywords' }
]

// 状态选项
const statusOptions = [
  { label: '全部', value: '' },
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

// 分页
const pagination = ref({
  page: 1,
  size: 10,
  total: 0
})

// 计算属性
const filteredPrompts = computed(() => {
  let filtered = prompts.value
  
  if (searchForm.value.name) {
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(searchForm.value.name.toLowerCase())
    )
  }
  
  if (searchForm.value.type) {
    filtered = filtered.filter(p => p.type === searchForm.value.type)
  }
  
  if (searchForm.value.status) {
    filtered = filtered.filter(p => p.status === searchForm.value.status)
  }
  
  return filtered
})

const paginatedPrompts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPrompts.value.slice(start, end)
})

// 辅助方法
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    content: 'primary',
    title: 'warning',
    summary: 'success',
    keywords: 'danger'
  }
  return typeMap[type] || 'info'
}

const getTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    content: '内容生成',
    title: '标题生成',
    summary: '摘要生成',
    keywords: '关键词提取'
  }
  return labelMap[type] || type
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 搜索Prompt
const handleSearch = () => {
  currentPage.value = 1
  loadPrompts()
}

// 重置搜索
const handleReset = () => {
  searchForm.value = {
    name: '',
    type: '',
    status: ''
  }
  currentPage.value = 1
  loadPrompts()
}

// 创建Prompt
const handleCreate = () => {
  promptForm.value = {
    name: '',
    description: '',
    type: 'content',
    content: '',
    variables: '',
    status: 'active'
  }
  dialogVisible.value = true
  isEditing.value = false
}

// 编辑Prompt
const handleEdit = (prompt: Prompt) => {
  promptForm.value = { ...prompt }
  dialogVisible.value = true
  isEditing.value = true
}

const handleDelete = async (prompt: Prompt) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Prompt "${prompt.name}" 吗？此操作不可撤销。`,
      '确认删除',
      {
        type: 'warning'
      }
    )
    
    // 调用删除API
    const response = await fetch(`http://localhost:5002/api/prompts/${prompt.id}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    ElMessage.success('删除成功')
    await loadPrompts()
  } catch (error: any) {
    if (error.message !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

const handleDialogClose = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    const url = isEdit.value 
      ? `http://localhost:5002/api/prompts/${formData.value.id}`
      : 'http://localhost:5002/api/prompts'
    
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    handleDialogClose()
    await loadPrompts()
  } catch (error: any) {
    ElMessage.error(`${isEdit.value ? '更新' : '创建'}失败: ${error.message}`)
  } finally {
    submitting.value = false
  }
}

const loadPrompts = async () => {
  try {
    loading.value = true
    
    const response = await fetch('http://localhost:5002/api/prompts')
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    promptList.value = data.data || []
    total.value = data.total || 0
  } catch (error: any) {
    ElMessage.error(`加载Prompt列表失败: ${error.message}`)
    // 添加一些模拟数据用于演示
    promptList.value = [
      {
        id: 1,
        name: '文章内容生成',
        type: 'content',
        description: '根据标题和关键词生成文章内容',
        content: '请根据标题"{title}"和关键词"{keywords}"生成一篇详细的文章内容。',
        variables: '{title} - 文章标题, {keywords} - 关键词',
        status: 'active',
        createdAt: '2024-01-01 10:00:00',
        usageCount: 15
      },
      {
        id: 2,
        name: '标题优化',
        type: 'title',
        description: '优化文章标题使其更吸引人',
        content: '请为以下内容生成3个吸引人的标题："{content}"',
        variables: '{content} - 文章内容摘要',
        status: 'active',
        createdAt: '2024-01-02 14:30:00',
        usageCount: 8
      }
    ]
  } finally {
    loading.value = false
  }
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadPrompts()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadPrompts()
}

// 组件挂载
onMounted(() => {
  loadPrompts()
})
</script>

<style lang="scss" scoped>
.prompt-management-container {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    
    .header-left {
      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 8px 0;
      }
      
      .page-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 0;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .search-section {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    
    .search-form {
      :deep(.el-form-item) {
        margin-bottom: 0;
      }
    }
    
    .search-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 16px;
    }
  }
  
  .prompt-table {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 12px;
    overflow: hidden;
    
    :deep(.el-table) {
      .el-table__header {
        background: var(--el-fill-color-lighter);
      }
      
      .status-tag {
        &.active {
          background: var(--el-color-success-light-9);
          color: var(--el-color-success);
          border-color: var(--el-color-success-light-5);
        }
        
        &.inactive {
          background: var(--el-color-info-light-9);
          color: var(--el-color-info);
          border-color: var(--el-color-info-light-5);
        }
      }
      
      .type-tag {
        &.content {
          background: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
          border-color: var(--el-color-primary-light-5);
        }
        
        &.title {
          background: var(--el-color-warning-light-9);
          color: var(--el-color-warning);
          border-color: var(--el-color-warning-light-5);
        }
        
        &.summary {
          background: var(--el-color-success-light-9);
          color: var(--el-color-success);
          border-color: var(--el-color-success-light-5);
        }
        
        &.keywords {
          background: var(--el-color-danger-light-9);
          color: var(--el-color-danger);
          border-color: var(--el-color-danger-light-5);
        }
      }
    }
    
    .table-pagination {
      padding: 20px;
      display: flex;
      justify-content: flex-end;
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }
  
  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--el-text-color-secondary);
    
    .empty-icon {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.5;
    }
    
    .empty-text {
      font-size: 16px;
      margin-bottom: 8px;
    }
    
    .empty-description {
      font-size: 14px;
      opacity: 0.8;
    }
  }
}

// 对话框样式
:deep(.el-dialog) {
  .el-dialog__header {
    padding: 20px 20px 0;
    
    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
    }
  }
  
  .el-dialog__body {
    padding: 20px;
    
    .el-form-item {
      margin-bottom: 20px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .el-textarea {
      .el-textarea__inner {
        resize: vertical;
      }
    }
  }
  
  .el-dialog__footer {
    padding: 0 20px 20px;
    
    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }
}
</style>