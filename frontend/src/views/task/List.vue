<template>
  <div class="task-list-page">
    <PageHeader title="任务管理" description="管理和监控所有爬虫任务" />
    
    <!-- 数据表格 -->
    <DataTable
      :data="taskStore.tasks"
      :columns="columns"
      :loading="taskStore.loading"
      :total="taskStore.pagination.total"
      :page-size="taskStore.pagination.pageSize"
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
          创建任务
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
        <el-button :icon="VideoPlay" @click="handleBatchStart(selection)">
          批量启动
        </el-button>
        <el-button :icon="VideoPause" @click="handleBatchStop(selection)">
          批量停止
        </el-button>
      </template>
      
      <!-- 状态列 -->
      <template #status="{ row }">
        <el-tag :type="getStatusType(row.status)" size="small">
          {{ getStatusText(row.status) }}
        </el-tag>
      </template>
      
      <!-- 优先级列 -->
      <template #priority="{ row }">
        <el-tag :type="getPriorityType(row.priority)" size="small">
          {{ getPriorityText(row.priority) }}
        </el-tag>
      </template>
      
      <!-- 进度列 -->
      <template #progress="{ row }">
        <el-progress
          :percentage="row.progress || 0"
          :status="row.status === 'failed' ? 'exception' : undefined"
          :stroke-width="6"
        />
      </template>
      
      <!-- 操作列 -->
      <template #actions="{ row }">
        <el-button
          v-if="row.status === 'pending' || row.status === 'paused'"
          type="primary"
          size="small"
          :icon="VideoPlay"
          @click="handleStart(row)"
        >
          启动
        </el-button>
        <el-button
          v-if="row.status === 'running'"
          type="warning"
          size="small"
          :icon="VideoPause"
          @click="handlePause(row)"
        >
          暂停
        </el-button>
        <el-button
          v-if="row.status === 'running' || row.status === 'paused'"
          type="danger"
          size="small"
          :icon="VideoPause"
          @click="handleStop(row)"
        >
          停止
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
              <el-dropdown-item :icon="CopyDocument" @click="handleClone(row)">
                克隆
              </el-dropdown-item>
              <el-dropdown-item :icon="Download" @click="handleExportSingle(row)">
                导出结果
              </el-dropdown-item>
              <el-dropdown-item :icon="Delete" divided @click="handleDelete(row)">
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </DataTable>
    
    <!-- 任务详情抽屉 -->
    <TaskDetailDrawer
      v-model="detailVisible"
      :task="currentTask"
      @refresh="handleRefresh"
    />
    
    <!-- 任务创建/编辑对话框 -->
    <TaskFormDialog
      v-model="formVisible"
      :task="currentTask"
      :mode="formMode"
      @success="handleFormSuccess"
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
  VideoPlay,
  VideoPause,
  View,
  Edit,
  More,
  CopyDocument
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import PageHeader from '@/components/common/PageHeader.vue'
import DataTable from '@/components/common/DataTable.vue'
import TaskDetailDrawer from './components/TaskDetailDrawer.vue'
import TaskFormDialog from './components/TaskFormDialog.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'

// 状态管理
const taskStore = useTaskStore()

// 响应式数据
const detailVisible = ref(false)
const formVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const currentTask = ref<any>(null)
const selectedTasks = ref<any[]>([])

// 表格列配置
const columns: TableColumn[] = [
  {
    prop: 'name',
    label: '任务名称',
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    slot: 'status'
  },
  {
    prop: 'priority',
    label: '优先级',
    width: 100,
    slot: 'priority'
  },
  {
    prop: 'progress',
    label: '进度',
    width: 150,
    slot: 'progress'
  },
  {
    prop: 'crawlerConfig.name',
    label: '爬虫配置',
    minWidth: 150,
    showOverflowTooltip: true
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
    pending: 'info',
    running: 'success',
    paused: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getPriorityType = (priority: string) => {
  const priorityMap: Record<string, string> = {
    low: 'info',
    medium: 'warning',
    high: 'danger'
  }
  return priorityMap[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const priorityMap: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return priorityMap[priority] || priority
}

// 事件处理方法
const handleRefresh = () => {
  taskStore.fetchTasks()
}

const handleSearch = (keyword: string) => {
  taskStore.setFilter({ keyword })
  taskStore.fetchTasks()
}

const handleSelectionChange = (selection: any[]) => {
  selectedTasks.value = selection
}

const handleSizeChange = (size: number) => {
  taskStore.setPagination({ pageSize: size, page: 1 })
  taskStore.fetchTasks()
}

const handleCurrentChange = (page: number) => {
  taskStore.setPagination({ page })
  taskStore.fetchTasks()
}

const handleCreate = () => {
  currentTask.value = null
  formMode.value = 'create'
  formVisible.value = true
}

const handleEdit = (task: any) => {
  currentTask.value = task
  formMode.value = 'edit'
  formVisible.value = true
}

const handleView = (task: any) => {
  currentTask.value = task
  detailVisible.value = true
}

const handleStart = async (task: any) => {
  try {
    await taskStore.startTask(task.id)
    ElMessage.success('任务启动成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('任务启动失败')
  }
}

const handlePause = async (task: any) => {
  try {
    await taskStore.pauseTask(task.id)
    ElMessage.success('任务暂停成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('任务暂停失败')
  }
}

const handleStop = async (task: any) => {
  try {
    await taskStore.stopTask(task.id)
    ElMessage.success('任务停止成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('任务停止失败')
  }
}

const handleDelete = async (task: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.name}" 吗？`,
      '确认删除',
      {
        type: 'warning'
      }
    )
    
    await taskStore.deleteTask(task.id)
    ElMessage.success('删除成功')
    handleRefresh()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleClone = async (task: any) => {
  try {
    await taskStore.cloneTask(task.id)
    ElMessage.success('克隆成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('克隆失败')
  }
}

const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中')
}

const handleExportSingle = (task: any) => {
  // TODO: 实现单个任务结果导出
  ElMessage.info('导出功能开发中')
}

const handleBatchDelete = async (selection: any[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selection.length} 个任务吗？`,
      '确认批量删除',
      {
        type: 'warning'
      }
    )
    
    const ids = selection.map(task => task.id)
    await taskStore.batchDeleteTasks(ids)
    ElMessage.success('批量删除成功')
    handleRefresh()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBatchStart = async (selection: any[]) => {
  try {
    const ids = selection.map(task => task.id)
    await taskStore.batchStartTasks(ids)
    ElMessage.success('批量启动成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('批量启动失败')
  }
}

const handleBatchStop = async (selection: any[]) => {
  try {
    const ids = selection.map(task => task.id)
    await taskStore.batchStopTasks(ids)
    ElMessage.success('批量停止成功')
    handleRefresh()
  } catch (error) {
    ElMessage.error('批量停止失败')
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  handleRefresh()
}

// 生命周期
onMounted(() => {
  handleRefresh()
})
</script>

<style lang="scss" scoped>
.task-list-page {
  padding: 24px;
  
  .el-progress {
    width: 100%;
  }
}
</style>