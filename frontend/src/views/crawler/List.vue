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
        <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
          {{ row.enabled ? '启用' : '禁用' }}
        </el-tag>
      </template>
      
      <!-- 提取规则列 -->
      <template #rules="{ row }">
        <div v-if="!row.rule_ids || (typeof row.rule_ids === 'string' && !row.rule_ids.trim())" class="text-gray-400">
          -
        </div>
        <div v-else class="rules-container">
          <el-tag
            v-for="rule in getRulesList(row.rule_ids)"
            :key="rule"
            size="small"
            type="info"
            class="rule-tag"
          >
            {{ rule }}
          </el-tag>
        </div>
      </template>
      
      <!-- 操作列 -->
      <template #actions="{ row }">

        <el-dropdown trigger="click">
          <el-button size="small" :icon="More" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :icon="Edit" @click="handleEdit(row)">
                编辑
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
  Edit,
  More,
  CopyDocument
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
    minWidth: 150, /* 调整宽度 */
    showOverflowTooltip: true
  },
  {
    prop: 'enable',
    label: '状态',
    width: 100,
    slot: 'status'
  },
  {
    prop: 'rule_ids',
    label: '提取规则',
    width: 250, /* 增加宽度 */
    slot: 'rules'
  },
  {
    prop: 'created_at',
    label: '创建时间',
    width: 180,
    formatter: (row: any) => {
      if (!row.created_at) return '-'
      return new Date(row.created_at).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  },
  {
    prop: 'updated_at',
    label: '更新时间',
    width: 180,
    formatter: (row: any) => {
      if (!row.updated_at) return '-'
      return new Date(row.updated_at).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  }
]



// 辅助方法
const getRulesList = (ruleIds: string | string[]) => {
  if (!ruleIds) return []
  if (Array.isArray(ruleIds)) return ruleIds
  return ruleIds.split(',').map(rule => rule.trim()).filter(rule => rule)
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



const handleImport = () => {
  importVisible.value = true
}

const handleExport = () => {
  // TODO: 实现导出功能
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

.rules-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 180px;
}

.rule-tag {
  /* 移除固定宽度限制，让标签自适应内容 */
  /* overflow: hidden; */
  /* text-overflow: ellipsis; */
  /* white-space: nowrap; */
  background-color: #e0f7fa; /* 淡蓝色背景 */
  color: #00796b; /* 深一点的文字颜色 */
  border-color: #b2ebf2; /* 边框颜色 */
}

.text-gray-400 {
  color: #9ca3af;
}
</style>