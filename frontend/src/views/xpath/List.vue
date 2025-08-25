<template>
  <div class="xpath-list">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>XPath配置管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建配置
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :model="searchForm" inline class="search-form">
          <el-form-item label="配置名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入配置名称"
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
          <el-form-item label="规则类型">
            <el-select 
              v-model="searchForm.rule_type" 
              placeholder="选择规则类型" 
              clearable
              style="width: 140px"
            >
              <el-option label="文本" value="text" />
              <el-option label="图片" value="image" />
              <el-option label="链接" value="link" />
              <el-option label="数据" value="data" />
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
        <el-table-column prop="name" label="配置名称" min-width="150">
          <template #default="{ row }">
            <div>
              <el-link type="primary" @click="handleView(row)">
                {{ row.name }}
              </el-link>
              <div class="rule-id">{{ row.rule_id }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="field_name" label="字段名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="domain_patterns" label="域名模式" min-width="150">
          <template #default="{ row }">
            <el-tag
              v-for="domain in row.domain_patterns.slice(0, 2)"
              :key="domain"
              size="small"
              class="domain-tag"
            >
              {{ domain }}
            </el-tag>
            <span v-if="row.domain_patterns.length > 2" class="more-domains">
              +{{ row.domain_patterns.length - 2 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="xpath" label="XPath表达式" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="xpath-code">{{ row.xpath }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="rule_type" label="规则类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getRuleTypeTag(row.rule_type)">
              {{ getRuleTypeText(row.rule_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.usage_count" :max="999" class="usage-badge" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
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
import { useXPathStore } from '@/stores/xpath'
import type { XPathConfig } from '@/stores/xpath'
import { formatDate } from '@/utils/date'

const router = useRouter()
const xpathStore = useXPathStore()

const loading = ref(false)
const tableData = ref<XPathConfig[]>([])
const selectedRows = ref<XPathConfig[]>([])

const searchForm = reactive({
  name: '',
  status: '',
  rule_type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})



// 获取规则类型标签颜色
const getRuleTypeTag = (type: string) => {
  const tagMap: Record<string, string> = {
    text: 'primary',
    image: 'info',
    link: 'success',
    data: 'warning'
  }
  return tagMap[type] || 'default'
}

// 获取规则类型文本
const getRuleTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    text: '文本',
    image: '图片',
    link: '链接',
    data: '数据'
  }
  return textMap[type] || type
}

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      name: searchForm.name,
      status: searchForm.status,
      rule_type: searchForm.rule_type
    }
    
    console.log('Sending params:', params) // 调试日志
    
    const success = await xpathStore.fetchXPathConfigs(params)
    if (success) {
      tableData.value = xpathStore.paginatedConfigs
      pagination.total = xpathStore.total
    }
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
    status: '',
    rule_type: ''
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
  router.push('/xpath/create')
}

// 查看
const handleView = (row: any) => {
  router.push(`/xpath/${row.id}`)
}

// 编辑
const handleEdit = (row: any) => {
  router.push(`/xpath/edit/${row.id}`)
}



// 切换状态
const handleToggleStatus = async (row: any) => {
  try {
    const newStatus = row.status === 'active' ? 'inactive' : 'active'
    const success = await xpathStore.toggleXPathConfigStatus(row.id, newStatus)
    if (success) {
      ElMessage.success(`${newStatus === 'active' ? '启用' : '禁用'}成功`)
      fetchData()
    }
  } catch (error) {
    console.error('Toggle status error:', error)
    ElMessage.error(`${row.status === 'active' ? '禁用' : '启用'}失败`)
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const success = await xpathStore.deleteXPathConfig(row.id)
    if (success) {
      ElMessage.success('删除成功')
      fetchData()
    }
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
.xpath-list {
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

.xpath-code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 2px;
}

.rule-id {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.domain-tag {
  margin-right: 4px;
  margin-bottom: 2px;
}

.more-domains {
  font-size: 12px;
  color: #666;
  margin-left: 4px;
}

.usage-badge :deep(.el-badge__content) {
  background-color: #409eff;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
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