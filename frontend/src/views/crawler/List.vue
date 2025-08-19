<template>
  <div class="crawler-list-page">
    <PageHeader title="爬虫配置" description="管理和配置网站爬虫规则" />
    
    <!-- 数据表格 -->
    <DataTable
      :data="crawlerStore.crawlerConfigs"
      :columns="columns"
      :loading="crawlerStore.loading"
      :total="crawlerStore.pagination.total"
      :page-size="crawlerStore.pagination.pageSize"
      selectable
      @refresh="handleRefresh"
      @search="handleSearch"
      @selection-change="handleSelectionChange"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    >
      <!-- 工具栏左侧 -->
      <template #toolbar-left>
        <el-button type="primary" :icon="Plus" @click="handleCreate">
          创建配置
        </el-button>
        <el-button :icon="Upload" @click="handleImport">
          导入
        </el-button>
        <el-button :icon="Download" @click="handleExport">
          导出
        </el-button>
      </template>
      
      <!-- 批量操作 -->
      <template #batch-actions="{ selection }">
        <el-button type="danger" :icon="Delete" @click="handleBatchDelete(selection)">
          批量删除
        </el-button>
        <el-button :icon="CopyDocument" @click="handleBatchDuplicate(selection)">
          批量复制
        </el-button>
      </template>
      
      <!-- 状态列 -->
      <template #status="{ row }">
        <el-tag :type="getStatusType(row.status)" size="small">
          {{ getStatusText(row.status) }}
        </el-tag>
      </template>
      
      <!-- 类型列 -->
      <template #type="{ row }">
        <el-tag type="info" size="small">
          {{ getTypeText(row.type) }}
        </el-tag>
      </template>
      
      <!-- URL列 -->
      <template #url="{ row }">
        <el-link :href="row.url" target="_blank" type="primary">
          {{ row.url }}
        </el-link>
      </template>
      
      <!-- 操作列 -->
      <template #actions="{ row }">
        <el-button
          type="primary"
          size="small"
          :icon="VideoPlay"
          @click="handleTest(row)"
        >
          测试
        </el-button>
        <el-button
          size="small"
          :icon="View"
          @click="handleView(row)"
        >
          查看
        </el-button>
        <el-dropdown trigger="click">
          <el-button size="small" :icon="More" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :icon="Edit" @click="handleEdit(row)">
                编辑
              </el-dropdown-item>
              <el-dropdown-item :icon="CopyDocument" @click="handleDuplicate(row)">
                复制
              </el-dropdown-item>
              <el-dropdown-item :icon="Setting" @click="handleConfigure(row)">
                配置XPath
              </el-dropdown-item>
              <el-dropdown-item :icon="Download" @click="handleExportSingle(row)">
                导出配置
              </el-dropdown-item>
              <el-dropdown-item :icon="Delete" divided @click="handleDelete(row)">
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </DataTable>
    
    <!-- 配置详情抽屉 -->
    <CrawlerDetailDrawer
      v-model="detailVisible"
      :config="currentConfig"
      @refresh="handleRefresh"
    />
    
    <!-- 配置表单对话框 -->
    <CrawlerFormDialog
      v-model="formVisible"
      :config="currentConfig"
      :mode="formMode"
      @success="handleFormSuccess"
    />
    
    <!-- 测试结果对话框 -->
    <TestResultDialog
      v-model="testVisible"
      :config="currentConfig"
      :test-result="testResult"
    />
    
    <!-- 导入对话框 -->
    <ImportDialog
      v-model="importVisible"
      @success="handleImportSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  Download,
  Upload,
  VideoPlay,
  View,
  Edit,
  More,
  CopyDocument,
  Setting
} from '@element-plus/icons-vue'
import { useCrawlerStore } from '@/stores/crawler'
import PageHeader from '@/components/common/PageHeader.vue'
import DataTable from '@/components/common/DataTable.vue'
import CrawlerDetailDrawer from './components/CrawlerDetailDrawer.vue'
import CrawlerFormDialog from './components/CrawlerFormDialog.vue'
import TestResultDialog from './components/TestResultDialog.vue'
import ImportDialog from './components/ImportDialog.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'

// 状态管理
const crawlerStore = useCrawlerStore()

// 响应式数据
const detailVisible = ref(false)
const formVisible = ref(false)
const testVisible = ref(false)
const importVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const currentConfig = ref<any>(null)
const testResult = ref<any>(null)
const selectedConfigs = ref<any[]>([])

// 表格列配置
const columns: TableColumn[] = [
  {
    prop: 'name',
    label: '配置名称',
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: 'url',
    label: '目标URL',
    minWidth: 300,
    slot: 'url',
    showOverflowTooltip: true
  },
  {
    prop: 'type',
    label: '类型',
    width: 100,
    slot: 'type'
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    slot: 'status'
  },
  {
    prop: 'extractionRules',
    label: '提取规则',
    width: 120,
    formatter: (row: any) => row.extractionRules?.length || 0
  },
  {
    prop: 'createdAt',
    label: '创建时间',
    width: 180,
    formatter: (row: any) => new Date(row.createdAt).toLocaleString()
  },
  {
    prop: 'updatedAt',
    label: '更新时间',
    width: 180,
    formatter: (row: any) => new Date(row.updatedAt).toLocaleString()
  }
]

// 状态相关方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    error: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '启用',
    inactive: '禁用',
    error: '错误'
  }
  return statusMap[status] || status
}

const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    list: '列表页',
    detail: '详情页',
    search: '搜索页',
    category: '分类页'
  }
  return typeMap[type] || type
}

// 事件处理方法
const handleRefresh = () => {
  crawlerStore.fetchCrawlerConfigs()
}

const handleSearch = (keyword: string) => {
  crawlerStore.setFilter({ keyword })
  crawlerStore.fetchCrawlerConfigs()
}

const handleSelectionChange = (selection: any[]) => {
  selectedConfigs.value = selection
}

const handleSizeChange = (size: number) => {
  crawlerStore.pagination.pageSize = size
  crawlerStore.pagination.page = 1
  crawlerStore.fetchCrawlerConfigs()
}

const handleCurrentChange = (page: number) => {
  crawlerStore.pagination.page = page
  crawlerStore.fetchCrawlerConfigs()
}

const handleCreate = () => {
  currentConfig.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleEdit = (config: any) => {
  currentConfig.value = config
  formMode.value = 'edit'
  formVisible.value = true
}

const handleView = (config: any) => {
  currentConfig.value = config
  detailVisible.value = true
}

const handleTest = async (config: any) => {
  try {
    currentConfig.value = config
    const result = await crawlerStore.testCrawlerConfig(config.id)
    testResult.value = result
    testVisible.value = true
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

const handleConfigure = (config: any) => {
  // 跳转到XPath配置页面
  // TODO: 实现路由跳转
  ElMessage.info('XPath配置功能开发中')
}

const handleDelete = async (config: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.name}" 吗？`,
      '确认删除',
      {
        type: 'warning'
      }
    )
    
    await crawlerStore.deleteCrawlerConfig(config.id)
    ElMessage.success('删除成功')
    handleRefresh()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleDuplicate = async (config: any) => {
  try {
    await crawlerStore.duplicateCrawlerConfig(config.id)
    ElMessage.success('复制成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleImport = () => {
  importVisible.value = true
}

const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中')
}

const handleExportSingle = (config: any) => {
  // TODO: 实现单个配置导出
  ElMessage.info('导出功能开发中')
}

const handleBatchDelete = async (selection: any[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selection.length} 个配置吗？`,
      '确认批量删除',
      {
        type: 'warning'
      }
    )
    
    const ids = selection.map(config => config.id)
    await crawlerStore.batchOperation(ids, 'delete')
    ElMessage.success('批量删除成功')
    handleRefresh()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBatchDuplicate = async (selection: any[]) => {
  try {
    const ids = selection.map(config => config.id)
    await crawlerStore.batchDuplicateConfigs(ids)
    ElMessage.success('批量复制成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('批量复制失败')
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleRefresh()
}

const handleImportSuccess = () => {
  importVisible.value = false
  handleRefresh()
}

// 生命周期
onMounted(() => {
  handleRefresh()
})
</script>

<style lang="scss" scoped>
.crawler-list-page {
  padding: 24px;
}
</style>