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
        <el-form :model="searchForm" inline>
          <el-form-item label="配置名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入配置名称"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
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
        <el-table-column prop="name" label="配置名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="field_name" label="字段名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="xpath" label="XPath表达式" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="xpath-code">{{ row.xpath }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="extractType" label="提取类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getExtractTypeTag(row.extractType)">
              {{ getExtractTypeText(row.extractType) }}
            </el-tag>
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleTest(row)">测试</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

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

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      ...searchForm
    }
    
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
  router.push('/xpath/create')
}

// 查看
const handleView = (row: any) => {
  router.push(`/xpath/${row.id}`)
}

// 编辑
const handleEdit = (row: any) => {
  router.push(`/xpath/${row.id}/edit`)
}

// 测试
const handleTest = (row: any) => {
  testForm.xpath = row.xpath
  testForm.url = ''
  testResult.value = ''
  testDialogVisible.value = true
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
      xpath: testForm.xpath
    })
    
    if (result.success) {
      testResult.value = result.data || '无匹配结果'
      ElMessage.success('测试完成')
    } else {
      testResult.value = `测试失败: ${result.message}`
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
  background-color: #f8f9fa;
  border-radius: 4px;
}

.xpath-code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 2px;
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