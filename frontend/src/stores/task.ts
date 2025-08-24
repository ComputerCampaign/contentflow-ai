import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import taskApi from '@/api/task'
import type {
  Task,
  TaskStatus,
  TaskType,
  TaskPriority,
  CreateTaskParams,
  UpdateTaskParams,
  TaskQueryParams,
  TaskStats,
  TaskLog
} from '@/api/task'

// 任务过滤条件接口
interface TaskFilter {
  status?: TaskStatus[]
  type?: TaskType[]
  priority?: TaskPriority[]
  keyword?: string
  dateRange?: [string, string]
  crawlerConfigId?: string
  task_type?: string
}

// 分页参数接口
interface PaginationParams {
  page: number
  pageSize: number
  total: number
}

export const useTaskStore = defineStore('task', () => {
  // 状态定义
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const taskLogs = ref<TaskLog[]>([])
  const taskResults = ref<any>(null)
  const taskStatistics = ref<TaskStats | null>(null)
  const taskTemplates = ref<any[]>([])
  const runningTasks = ref<Task[]>([])
  
  // 加载状态
  const loading = ref(false)
  const logsLoading = ref(false)
  const resultsLoading = ref(false)
  const statisticsLoading = ref(false)
  const templatesLoading = ref(false)
  const operationLoading = ref(false)
  
  // 分页和过滤
  const pagination = ref<PaginationParams>({
    page: 1,
    pageSize: 20,
    total: 0
  })
  const filter = ref<TaskFilter>({})
  const sortField = ref<string>('createdAt')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  // 计算属性
  const filteredTasks = computed(() => {
    let result = [...tasks.value]
    
    // 状态过滤
    if (filter.value.status && filter.value.status.length > 0) {
      result = result.filter(task => filter.value.status!.includes(task.status))
    }
    
    // 类型过滤
    if (filter.value.type && filter.value.type.length > 0) {
      result = result.filter(task => filter.value.type!.includes(task.type))
    }
    
    // 优先级过滤
    if (filter.value.priority && filter.value.priority.length > 0) {
      result = result.filter(task => filter.value.priority!.includes(task.priority))
    }
    
    // 关键词过滤
    if (filter.value.keyword) {
      const keyword = filter.value.keyword.toLowerCase()
      result = result.filter(task => 
        task.name.toLowerCase().includes(keyword) ||
        task.description?.toLowerCase().includes(keyword)
      )
    }
    
    // 日期范围过滤
    if (filter.value.dateRange && filter.value.dateRange.length === 2) {
      const [startDate, endDate] = filter.value.dateRange
      result = result.filter(task => {
        const taskDate = new Date(task.createdAt).getTime()
        return taskDate >= new Date(startDate).getTime() && 
               taskDate <= new Date(endDate).getTime()
      })
    }
    
    return result
  })
  
  const taskStatusCounts = computed(() => {
    const counts = {
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0,
      paused: 0,
      cancelled: 0
    }
    
    tasks.value.forEach(task => {
      counts[task.status] = (counts[task.status] || 0) + 1
    })
    
    return counts
  })
  
  const hasRunningTasks = computed(() => runningTasks.value.length > 0)

  // 获取任务列表
  const fetchTasks = async (params?: Partial<PaginationParams & TaskFilter>): Promise<void> => {
    try {
      loading.value = true
      
      const queryParams: TaskQueryParams = {
        page: params?.page || pagination.value.page,
        pageSize: params?.pageSize || pagination.value.pageSize,
        status: filter.value.status?.[0],
        type: filter.value.type?.[0],
        priority: filter.value.priority?.[0],
        keyword: filter.value.keyword,
        sortBy: sortField.value as any,
        sortOrder: sortOrder.value,
        task_type: params?.task_type || filter.value.task_type
      }
      
      console.log('🔍 发送给后端的queryParams:', queryParams)
      
      const response = await taskApi.getTasks(queryParams)
      
      console.log('📥 后端返回的原始response:', response)
      console.log('📊 response.data的结构:', response.data)
      
      if (response.success && response.data) {
        console.log('✅ 最终赋值给tasks.value的数据:', response.data.tasks)
        tasks.value = response.data.tasks || []
        pagination.value = {
          page: response.data.pagination?.page || 1,
          pageSize: response.data.pagination?.per_page || 20,
          total: response.data.pagination?.total || 0
        }
      } else {
        console.error('❌ 响应失败:', response.message)
      }
    } catch (error: any) {
      console.error('Fetch tasks error:', error)
      ElMessage.error(error.message || '获取任务列表失败')
    } finally {
      loading.value = false
    }
  }

  // 根据ID获取任务详情
  const fetchTaskById = async (taskId: number): Promise<Task | null> => {
    try {
      const response = await taskApi.getTask(taskId)
      
      if (response.success && response.data) {
        currentTask.value = response.data
        return response.data
      }
      return null
    } catch (error: any) {
      console.error('Fetch task error:', error)
      ElMessage.error(error.message || '获取任务详情失败')
      return null
    }
  }

  // 创建任务
  const createTask = async (taskData: CreateTaskParams): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.createTask(taskData)
      
      if (response.success && response.data) {
        tasks.value.unshift(response.data)
        pagination.value.total += 1
        ElMessage.success('任务创建成功')
        return true
      } else {
        ElMessage.error(response.message || '任务创建失败')
        return false
      }
    } catch (error: any) {
      console.error('Create task error:', error)
      ElMessage.error(error.message || '任务创建失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 更新任务
  const updateTask = async (taskId: number, taskData: UpdateTaskParams): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.updateTask(taskId, taskData)
      
      if (response.success && response.data) {
        const index = tasks.value.findIndex(task => task.id === taskId)
        if (index !== -1) {
          tasks.value[index] = response.data
        }
        if (currentTask.value?.id === taskId) {
          currentTask.value = response.data
        }
        ElMessage.success('任务更新成功')
        return true
      } else {
        ElMessage.error(response.message || '任务更新失败')
        return false
      }
    } catch (error: any) {
      console.error('Update task error:', error)
      ElMessage.error(error.message || '任务更新失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 删除任务
  const deleteTask = async (taskId: number): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(
        '确定要删除这个任务吗？删除后无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      operationLoading.value = true
      const response = await taskApi.deleteTask(taskId)
      
      if (response.success) {
        tasks.value = tasks.value.filter(task => task.id !== taskId)
        pagination.value.total -= 1
        if (currentTask.value?.id === taskId) {
          currentTask.value = null
        }
        ElMessage.success('任务删除成功')
        return true
      } else {
        ElMessage.error(response.message || '任务删除失败')
        return false
      }
    } catch (error: any) {
      if (error === 'cancel') {
        return false
      }
      console.error('Delete task error:', error)
      ElMessage.error(error.message || '任务删除失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 执行任务
  const executeTask = async (taskId: number): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.executeTask(taskId)
      
      if (response.success) {
        await fetchTaskById(taskId)
        await fetchRunningTasks()
        ElMessage.success('任务开始执行')
        return true
      } else {
        ElMessage.error(response.message || '任务执行失败')
        return false
      }
    } catch (error: any) {
      console.error('Execute task error:', error)
      ElMessage.error(error.message || '任务执行失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 暂停任务
  const pauseTask = async (taskId: number): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.pauseTask(taskId)
      
      if (response.success) {
        await fetchTaskById(taskId)
        await fetchRunningTasks()
        ElMessage.success('任务已暂停')
        return true
      } else {
        ElMessage.error(response.message || '任务暂停失败')
        return false
      }
    } catch (error: any) {
      console.error('Pause task error:', error)
      ElMessage.error(error.message || '任务暂停失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 恢复任务
  const resumeTask = async (taskId: number): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.resumeTask(taskId)
      
      if (response.success) {
        await fetchTaskById(taskId)
        await fetchRunningTasks()
        ElMessage.success('任务已恢复')
        return true
      } else {
        ElMessage.error(response.message || '任务恢复失败')
        return false
      }
    } catch (error: any) {
      console.error('Resume task error:', error)
      ElMessage.error(error.message || '任务恢复失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 取消任务
  const cancelTask = async (taskId: number): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(
        '确定要取消这个任务吗？',
        '确认取消',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      operationLoading.value = true
      const response = await taskApi.cancelTask(taskId)
      
      if (response.success) {
        await fetchTaskById(taskId)
        await fetchRunningTasks()
        ElMessage.success('任务已取消')
        return true
      } else {
        ElMessage.error(response.message || '任务取消失败')
        return false
      }
    } catch (error: any) {
      if (error === 'cancel') {
        return false
      }
      console.error('Cancel task error:', error)
      ElMessage.error(error.message || '任务取消失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 重试任务
  const retryTask = async (taskId: number): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.retryTask(taskId)
      
      if (response.success) {
        await fetchTaskById(taskId)
        await fetchRunningTasks()
        ElMessage.success('任务重试成功')
        return true
      } else {
        ElMessage.error(response.message || '任务重试失败')
        return false
      }
    } catch (error: any) {
      console.error('Retry task error:', error)
      ElMessage.error(error.message || '任务重试失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 复制任务
  const duplicateTask = async (taskId: number): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.duplicateTask(taskId)
      
      if (response.success && response.data) {
        tasks.value.unshift(response.data)
        pagination.value.total += 1
        ElMessage.success('任务复制成功')
        return true
      } else {
        ElMessage.error(response.message || '任务复制失败')
        return false
      }
    } catch (error: any) {
      console.error('Duplicate task error:', error)
      ElMessage.error(error.message || '任务复制失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 获取任务日志
  const fetchTaskLogs = async (taskId: number, params?: { page?: number; pageSize?: number }): Promise<void> => {
    try {
      logsLoading.value = true
      const response = await taskApi.getTaskLogs(taskId, params)
      
      if (response.success && response.data) {
        taskLogs.value = response.data.list
      }
    } catch (error: any) {
      console.error('Fetch task logs error:', error)
      ElMessage.error(error.message || '获取任务日志失败')
    } finally {
      logsLoading.value = false
    }
  }

  // 获取任务结果
  const fetchTaskResults = async (taskId: number, params?: { page?: number; pageSize?: number }): Promise<void> => {
    try {
      resultsLoading.value = true
      const response = await taskApi.getTaskResults(taskId, params)
      
      if (response.success && response.data) {
        taskResults.value = response.data
      }
    } catch (error: any) {
      console.error('Fetch task results error:', error)
      ElMessage.error(error.message || '获取任务结果失败')
    } finally {
      resultsLoading.value = false
    }
  }

  // 获取任务统计
  const fetchTaskStatistics = async (): Promise<void> => {
    try {
      statisticsLoading.value = true
      const response = await taskApi.getTaskStats()
      
      if (response.success && response.data) {
        taskStatistics.value = response.data
      }
    } catch (error: any) {
      console.error('Fetch task statistics error:', error)
      ElMessage.error(error.message || '获取任务统计失败')
    } finally {
      statisticsLoading.value = false
    }
  }

  // 获取正在运行的任务
  const fetchRunningTasks = async (): Promise<void> => {
    try {
      const response = await taskApi.getRunningTasks()
      
      if (response.success && response.data) {
        runningTasks.value = response.data
      }
    } catch (error: any) {
      console.error('Fetch running tasks error:', error)
    }
  }

  // 获取任务模板
  const fetchTaskTemplates = async (): Promise<void> => {
    try {
      templatesLoading.value = true
      const response = await taskApi.getTaskTemplates()
      
      if (response.success && response.data) {
        taskTemplates.value = response.data
      }
    } catch (error: any) {
      console.error('Fetch task templates error:', error)
      ElMessage.error(error.message || '获取任务模板失败')
    } finally {
      templatesLoading.value = false
    }
  }

  // 导出任务日志
  const exportTaskLogs = async (params: any): Promise<void> => {
    try {
      // 创建导出数据
      const exportData = {
        logs: taskLogs.value,
        filters: params,
        exportTime: new Date().toISOString()
      }
      
      // 创建下载链接
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `task-logs-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error: any) {
      console.error('Export task logs error:', error)
      ElMessage.error(error.message || '导出任务日志失败')
    }
  }

  // 启动任务
  const startTask = async (taskId: number): Promise<boolean> => {
    return await executeTask(taskId)
  }

  // 停止任务
  const stopTask = async (taskId: number): Promise<boolean> => {
    return await cancelTask(taskId)
  }

  // 批量启动任务
  const batchStartTasks = async (taskIds: string[]): Promise<boolean> => {
    return await batchOperation(taskIds, 'execute')
  }

  // 批量停止任务
  const batchStopTasks = async (taskIds: string[]): Promise<boolean> => {
    return await batchOperation(taskIds, 'cancel')
  }

  // 批量操作
  const batchOperation = async (taskIds: string[], operation: 'delete' | 'execute' | 'pause' | 'cancel'): Promise<boolean> => {
    try {
      let confirmMessage = ''
      let successMessage = ''
      
      switch (operation) {
        case 'delete':
          confirmMessage = `确定要删除选中的 ${taskIds.length} 个任务吗？删除后无法恢复。`
          successMessage = '批量删除成功'
          break
        case 'execute':
          confirmMessage = `确定要执行选中的 ${taskIds.length} 个任务吗？`
          successMessage = '批量执行成功'
          break
        case 'pause':
          confirmMessage = `确定要暂停选中的 ${taskIds.length} 个任务吗？`
          successMessage = '批量暂停成功'
          break
        case 'cancel':
          confirmMessage = `确定要取消选中的 ${taskIds.length} 个任务吗？`
          successMessage = '批量取消成功'
          break
      }
      
      await ElMessageBox.confirm(confirmMessage, '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      operationLoading.value = true
      const response = await taskApi.batchAction(operation, taskIds)
      
      if (response.success) {
        await fetchTasks()
        await fetchRunningTasks()
        ElMessage.success(successMessage)
        return true
      } else {
        ElMessage.error(response.message || '批量操作失败')
        return false
      }
    } catch (error: any) {
      if (error === 'cancel') {
        return false
      }
      console.error('Batch operation error:', error)
      ElMessage.error(error.message || '批量操作失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 设置分页
  const setPagination = (newPagination: Partial<{ page: number; pageSize: number; total: number }>): void => {
    pagination.value = { ...pagination.value, ...newPagination }
  }

  // 克隆任务
  const cloneTask = async (taskId: number): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await taskApi.duplicateTask(taskId)
      
      if (response.success && response.data) {
        tasks.value.unshift(response.data)
        pagination.value.total += 1
        ElMessage.success('任务克隆成功')
        return true
      } else {
        ElMessage.error(response.message || '任务克隆失败')
        return false
      }
    } catch (error: any) {
      console.error('Clone task error:', error)
      ElMessage.error(error.message || '任务克隆失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 批量删除任务
  const batchDeleteTasks = async (taskIds: string[]): Promise<boolean> => {
    return await batchOperation(taskIds, 'delete')
  }

  // 设置过滤条件
  const setFilter = (newFilter: Partial<TaskFilter>): void => {
    filter.value = { ...filter.value, ...newFilter }
    pagination.value.page = 1
  }

  // 清除过滤条件
  const clearFilter = (): void => {
    filter.value = {}
    pagination.value.page = 1
  }

  // 设置排序
  const setSort = (field: string, order: 'asc' | 'desc'): void => {
    sortField.value = field
    sortOrder.value = order
    pagination.value.page = 1
  }

  // 重置状态
  const resetState = (): void => {
    tasks.value = []
    currentTask.value = null
    taskLogs.value = []
    taskStatistics.value = null
    taskTemplates.value = []
    runningTasks.value = []
    filter.value = {}
    pagination.value = { page: 1, pageSize: 20, total: 0 }
    sortField.value = 'createdAt'
    sortOrder.value = 'desc'
  }

  return {
    // 状态
    tasks,
    currentTask,
    taskLogs,
    taskResults,
    taskStatistics,
    taskTemplates,
    runningTasks,
    loading,
    logsLoading,
    resultsLoading,
    statisticsLoading,
    templatesLoading,
    operationLoading,
    pagination,
    filter,
    sortField,
    sortOrder,
    
    // 计算属性
    filteredTasks,
    taskStatusCounts,
    hasRunningTasks,
    
    // 方法
    fetchTasks,
    fetchTaskById,
    createTask,
    updateTask,
    deleteTask,
    executeTask,
    pauseTask,
    resumeTask,
    cancelTask,
    retryTask,
    duplicateTask,
    startTask,
    stopTask,
    batchStartTasks,
    batchStopTasks,
    batchOperation,
    setPagination,
    cloneTask,
    batchDeleteTasks,
    fetchTaskLogs,
    fetchTaskResults,
    fetchTaskStatistics,
    fetchRunningTasks,
    fetchTaskTemplates,
    exportTaskLogs,
    setFilter,
    clearFilter,
    setSort,
    resetState
  }
})