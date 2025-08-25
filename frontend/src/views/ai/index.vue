<template>
  <div class="prompt-list">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>提示词管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建提示词
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :model="searchForm" inline class="search-form">
          <el-form-item label="提示词名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入提示词名称"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select 
              v-model="searchForm.status" 
              placeholder="选择状态" 
              clearable
              style="width: 120px"
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
      </div>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="提示词名称" min-width="150">
          <template #default="{ row }">
            <div>
              <el-link type="primary" @click="handleView(row)">
                {{ row.name }}
              </el-link>
              <div class="prompt-key">{{ row.key }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="system" label="系统提示词" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="prompt-preview">{{ row.system || '未设置' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="user_template" label="用户模板" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="template-preview">{{ row.user_template || '未设置' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.usage_count || 0" :max="999" class="usage-badge" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="warning" size="small">
              默认
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click">
              <el-button size="small" :icon="More" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleEdit(row)">
                    编辑
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleToggleStatus(row)">
                    {{ row.status === 'active' ? '禁用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleSetDefault(row)" v-if="!row.is_default">
                    设为默认
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleDelete(row)">
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, More } from '@element-plus/icons-vue'
import { useAIStore } from '@/stores/ai'
import { formatDate } from '@/utils/date'

const router = useRouter()
const aiStore = useAIStore()

const loading = ref(false)
const tableData = ref<any[]>([])
const selectedRows = ref<any[]>([])

const searchForm = reactive({
  name: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    await aiStore.fetchPromptsConfig()
    
    // 将prompts对象转换为数组格式
    const prompts = aiStore.promptsConfig.prompts || {}
    let promptList = Object.entries(prompts).map(([key, value]: [string, any]) => ({
      key,
      name: key,
      system: value.system,
      user_template: value.user_template,
      status: 'active', // 默认状态
      usage_count: 0, // 默认使用次数
      is_default: key === aiStore.promptsConfig.default_prompt,
      created_at: new Date().toISOString() // 默认创建时间
    }))
    
    // 应用搜索过滤
    if (searchForm.name) {
      promptList = promptList.filter(item => 
        item.name.toLowerCase().includes(searchForm.name.toLowerCase())
      )
    }
    
    if (searchForm.status) {
      promptList = promptList.filter(item => item.status === searchForm.status)
    }
    
    // 分页处理
    pagination.total = promptList.length
    const start = (pagination.page - 1) * pagination.pageSize
    const end = start + pagination.pageSize
    tableData.value = promptList.slice(start, end)
    
  } catch (error) {
    console.error('Fetch data error:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    status: ''
  })
  pagination.page = 1
  fetchData()
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 分页变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchData()
}

// 新建
const handleCreate = () => {
  router.push('/ai/prompt/create')
}

// 查看
const handleView = (row: any) => {
  router.push(`/ai/prompt/${row.key}`)
}

// 编辑
const handleEdit = (row: any) => {
  router.push(`/ai/prompt/edit/${row.key}`)
}

// 切换状态
const handleToggleStatus = async (row: any) => {
  try {
    const newStatus = row.status === 'active' ? 'inactive' : 'active'
    // 这里需要实现状态切换的逻辑
    ElMessage.success(`${newStatus === 'active' ? '启用' : '禁用'}成功`)
    fetchData()
  } catch (error) {
    console.error('Toggle status error:', error)
    ElMessage.error(`${row.status === 'active' ? '禁用' : '启用'}失败`)
  }
}

// 设为默认
const handleSetDefault = async (row: any) => {
  try {
    aiStore.promptsConfig.default_prompt = row.key
    await aiStore.savePromptsConfig(aiStore.promptsConfig)
    ElMessage.success('设置默认成功')
    fetchData()
  } catch (error) {
    console.error('Set default error:', error)
    ElMessage.error('设置默认失败')
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除提示词 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    delete aiStore.promptsConfig.prompts[row.key]
    
    // 如果删除的是默认提示词，清空默认设置
    if (aiStore.promptsConfig.default_prompt === row.key) {
      aiStore.promptsConfig.default_prompt = ''
    }
    
    await aiStore.savePromptsConfig(aiStore.promptsConfig)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.prompt-list {
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

.card-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}

.search-form .el-form-item {
  margin-bottom: 0;
}

.search-form .el-select {
  min-width: 120px;
}

.prompt-key {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.prompt-preview,
.template-preview {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: #666;
}

.usage-badge :deep(.el-badge__content) {
  background-color: #409eff;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>