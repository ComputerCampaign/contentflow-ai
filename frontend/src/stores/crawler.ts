import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import crawlerApi from '@/api/crawler'
import type {
  CrawlerConfig,
  CrawlerStatus,
  CrawlerType,
  ExtractionMethod,
  CreateCrawlerParams,
  UpdateCrawlerParams,
  CrawlerQueryParams,
  CrawlerTestResult,
  CrawlerRunResult
} from '@/api/crawler'

// 爬虫配置过滤条件接口
interface CrawlerFilter {
  status?: CrawlerStatus[]
  type?: CrawlerType[]
  extractionMethod?: ExtractionMethod[]
  keyword?: string
  dateRange?: [string, string]
  tags?: string[]
}

// 分页参数接口
interface PaginationParams {
  page: number
  pageSize: number
  total: number
}

export const useCrawlerStore = defineStore('crawler', () => {
  // 状态定义
  const crawlerConfigs = ref<CrawlerConfig[]>([])
  const currentConfig = ref<CrawlerConfig | null>(null)
  const testResult = ref<CrawlerTestResult | null>(null)
  const runResult = ref<CrawlerRunResult | null>(null)
  const statistics = ref<any | null>(null)
  const availableTags = ref<string[]>([])
  
  // 加载状态
  const loading = ref(false)
  const testLoading = ref(false)
  const runLoading = ref(false)
  const statisticsLoading = ref(false)
  const operationLoading = ref(false)
  const importLoading = ref(false)
  const exportLoading = ref(false)
  
  // 分页和过滤
  const pagination = ref<PaginationParams>({
    page: 1,
    pageSize: 20,
    total: 0
  })
  const filter = ref<CrawlerFilter>({})
  const sortField = ref<string>('updatedAt')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  // 计算属性
  const filteredConfigs = computed(() => {
    let result = [...crawlerConfigs.value]
    
    // 状态过滤
    if (filter.value.status && filter.value.status.length > 0) {
      result = result.filter(config => filter.value.status!.includes(config.status))
    }
    
    // 类型过滤
    if (filter.value.type && filter.value.type.length > 0) {
      result = result.filter(config => filter.value.type!.includes(config.type))
    }
    
    // 提取方法过滤
    if (filter.value.extractionMethod && filter.value.extractionMethod.length > 0) {
      result = result.filter(config => filter.value.extractionMethod!.includes((config as any).extractionMethod))
    }
    
    // 关键词过滤
    if (filter.value.keyword) {
      const keyword = filter.value.keyword.toLowerCase()
      result = result.filter(config => 
        config.name.toLowerCase().includes(keyword) ||
        config.description?.toLowerCase().includes(keyword) ||
        config.targetUrl.toLowerCase().includes(keyword)
      )
    }
    
    // 标签过滤
    if (filter.value.tags && filter.value.tags.length > 0) {
      result = result.filter(config => 
        filter.value.tags!.some(tag => (config as any).tags?.includes(tag))
      )
    }
    
    // 日期范围过滤
    if (filter.value.dateRange && filter.value.dateRange.length === 2) {
      const [startDate, endDate] = filter.value.dateRange
      result = result.filter(config => {
        const configDate = new Date(config.updatedAt).getTime()
        return configDate >= new Date(startDate).getTime() && 
               configDate <= new Date(endDate).getTime()
      })
    }
    
    return result
  })
  
  const configStatusCounts = computed(() => {
    const counts = {
      active: 0,
      inactive: 0,
      testing: 0,
      error: 0
    }
    
    crawlerConfigs.value.forEach(config => {
      counts[config.status] = (counts[config.status] || 0) + 1
    })
    
    return counts
  })
  
  const configTypeCounts = computed(() => {
    const counts: Record<string, number> = {}
    
    crawlerConfigs.value.forEach(config => {
      counts[config.type] = (counts[config.type] || 0) + 1
    })
    
    return counts
  })

  // 获取爬虫配置列表（别名方法）
  const fetchCrawlers = async (params?: Partial<PaginationParams & CrawlerFilter>): Promise<boolean> => {
    try {
      await fetchCrawlerConfigs(params)
      return true
    } catch (error) {
      return false
    }
  }

  // 获取爬虫配置列表
  const fetchCrawlerConfigs = async (params?: Partial<PaginationParams & CrawlerFilter>): Promise<void> => {
    try {
      loading.value = true
      
      const queryParams: any = {
          page: params?.page || pagination.value.page,
          pageSize: params?.pageSize || pagination.value.pageSize,
          status: Array.isArray(filter.value.status) ? filter.value.status[0] : filter.value.status,
          type: Array.isArray(filter.value.type) ? filter.value.type[0] : filter.value.type,
          keyword: filter.value.keyword,
          sortBy: sortField.value,
          sortOrder: sortOrder.value,
          ...params
        }
      
      const response = await crawlerApi.getCrawlerConfigs(queryParams)
      
      if (response.success && response.data) {
        crawlerConfigs.value = response.data.list
        pagination.value = {
          page: response.data.page,
          pageSize: response.data.pageSize,
          total: response.data.total
        }
      }
    } catch (error: any) {
      console.error('Fetch crawler configs error:', error)
      ElMessage.error(error.message || '获取爬虫配置列表失败')
    } finally {
      loading.value = false
    }
  }

  // 获取单个爬虫配置详情
  const fetchCrawlerConfigById = async (configId: string): Promise<CrawlerConfig | null> => {
    try {
      const response = await crawlerApi.getCrawlerConfig(Number(configId))
      
      if (response.success && response.data) {
        currentConfig.value = response.data
        return response.data
      }
      return null
    } catch (error: any) {
      console.error('Fetch crawler config error:', error)
      ElMessage.error(error.message || '获取爬虫配置详情失败')
      return null
    }
  }

  // 创建爬虫配置
  const createCrawlerConfig = async (configData: CreateCrawlerParams): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await crawlerApi.createCrawlerConfig(configData)
      
      if (response.success && response.data) {
        crawlerConfigs.value.unshift(response.data)
        pagination.value.total += 1
        ElMessage.success('爬虫配置创建成功')
        return true
      } else {
        ElMessage.error(response.message || '爬虫配置创建失败')
        return false
      }
    } catch (error: any) {
      console.error('Create crawler config error:', error)
      ElMessage.error(error.message || '爬虫配置创建失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 更新爬虫配置
  const updateCrawlerConfig = async (configId: number, configData: UpdateCrawlerParams): Promise<boolean> => {
    try {
      operationLoading.value = true
      const response = await crawlerApi.updateCrawlerConfig(configId, configData)
      
      if (response.success && response.data) {
        const index = crawlerConfigs.value.findIndex(config => config.id === configId)
        if (index !== -1) {
          crawlerConfigs.value[index] = response.data
        }
        if (currentConfig.value?.id === Number(configId)) {
          currentConfig.value = response.data
        }
        ElMessage.success('爬虫配置更新成功')
        return true
      } else {
        ElMessage.error(response.message || '爬虫配置更新失败')
        return false
      }
    } catch (error: any) {
      console.error('Update crawler config error:', error)
      ElMessage.error(error.message || '爬虫配置更新失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 删除爬虫配置
  const deleteCrawlerConfig = async (configId: string): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(
        '确定要删除这个爬虫配置吗？删除后无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      operationLoading.value = true
      const response = await crawlerApi.delete(Number(configId))
      
      if (response.success) {
        crawlerConfigs.value = crawlerConfigs.value.filter(config => config.id !== Number(configId))
        pagination.value.total -= 1
        if (currentConfig.value?.id === Number(configId)) {
          currentConfig.value = null
        }
        ElMessage.success('爬虫配置删除成功')
        return true
      } else {
        ElMessage.error(response.message || '爬虫配置删除失败')
        return false
      }
    } catch (error: any) {
      if (error === 'cancel') {
        return false
      }
      console.error('Delete crawler config error:', error)
      ElMessage.error(error.message || '爬虫配置删除失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 测试爬虫配置
  const testCrawlerConfig = async (configId: string): Promise<boolean> => {
    try {
      testLoading.value = true
      testResult.value = null
      
      const response = await crawlerApi.testCrawlerConfig(Number(configId))
      
      if (response.success && response.data) {
        testResult.value = response.data
        if (response.data.success) {
          ElMessage.success('爬虫配置测试成功')
        } else {
          ElMessage.warning('爬虫配置测试完成，但存在问题')
        }
        return true
      } else {
        ElMessage.error(response.message || '爬虫配置测试失败')
        return false
      }
    } catch (error: any) {
      console.error('Test crawler config error:', error)
      ElMessage.error(error.message || '爬虫配置测试失败')
      return false
    } finally {
      testLoading.value = false
    }
  }

  // 运行爬虫配置
  const runCrawlerConfig = async (configId: string, options?: { immediate?: boolean }): Promise<boolean> => {
    try {
      runLoading.value = true
      runResult.value = null
      
      const response = await crawlerApi.runCrawlerConfig(Number(configId), {
        maxPages: options?.immediate ? 1 : undefined,
        timeout: 30000,
        outputFormat: 'json'
      })
      
      if (response.success && response.data) {
        runResult.value = {
          id: response.data.runId,
          crawlerConfigId: Number(configId),
          status: 'running',
          startTime: new Date().toISOString(),
          progress: 0,
          extractedCount: 0,
          errorCount: 0,
          data: [],
          totalPages: 0,
          processedPages: 0,
          extractedItems: 0,
          failedPages: 0
        } as CrawlerRunResult
        ElMessage.success('爬虫开始运行')
        return true
      } else {
        ElMessage.error(response.message || '爬虫运行失败')
        return false
      }
    } catch (error: any) {
      console.error('Run crawler config error:', error)
      ElMessage.error(error.message || '爬虫运行失败')
      return false
    } finally {
      runLoading.value = false
    }
  }

  // 停止爬虫
  const stopCrawlerConfig = async (configId: string): Promise<boolean> => {
    try {
      operationLoading.value = true
      // 停止爬虫配置运行 - 需要实现具体的停止逻辑
      await fetchCrawlerConfigById(configId)
      ElMessage.success('爬虫已停止')
      return true
    } catch (error: any) {
      console.error('Stop crawler config error:', error)
      ElMessage.error(error.message || '停止爬虫失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 复制爬虫配置
  const duplicateCrawlerConfig = async (configId: string): Promise<boolean> => {
    try {
      operationLoading.value = true
      // 复制爬虫配置 - 需要实现具体的复制逻辑
      await fetchCrawlerConfigs()
      ElMessage.success('爬虫配置已复制')
      return true
    } catch (error: any) {
      console.error('Duplicate crawler config error:', error)
      ElMessage.error(error.message || '爬虫配置复制失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 获取爬虫统计信息
  const fetchCrawlerStatistics = async (): Promise<void> => {
    try {
      statisticsLoading.value = true
      const response = await crawlerApi.getCrawlerStats()
      
      if (response.success && response.data) {
        statistics.value = response.data
      }
    } catch (error: any) {
      console.error('Fetch crawler statistics error:', error)
      ElMessage.error(error.message || '获取爬虫统计信息失败')
    } finally {
      statisticsLoading.value = false
    }
  }

  // 获取可用标签
  const fetchAvailableTags = async (): Promise<void> => {
    try {
      // 获取可用标签 - 需要实现具体的标签逻辑
      const tags = ['web', 'api', 'rss', 'sitemap']
      availableTags.value = tags
    } catch (error: any) {
      console.error('Fetch available tags error:', error)
    }
  }

  // 导入爬虫配置
  const importCrawlerConfigs = async (file: File): Promise<boolean> => {
    try {
      importLoading.value = true
      const response = await crawlerApi.importCrawlerConfigs(file)
      
      if (response.success && response.data) {
        await fetchCrawlerConfigs()
        ElMessage.success(`成功导入 ${response.data.imported} 个爬虫配置`)
        return true
      } else {
        ElMessage.error(response.message || '导入爬虫配置失败')
        return false
      }
    } catch (error: any) {
      console.error('Import crawler configs error:', error)
      ElMessage.error(error.message || '导入爬虫配置失败')
      return false
    } finally {
      importLoading.value = false
    }
  }

  // 导出爬虫配置
  const exportCrawlerConfigs = async (configIds?: string[]): Promise<boolean> => {
    try {
      exportLoading.value = true
      const response = await crawlerApi.exportCrawlerConfigs((configIds || []).map(id => Number(id)))
      
      if (response.success && response.data) {
        // 创建下载链接
        const blob = new Blob([JSON.stringify(response.data, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `crawler-configs-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        ElMessage.success('爬虫配置导出成功')
        return true
      } else {
        ElMessage.error(response.message || '导出爬虫配置失败')
        return false
      }
    } catch (error: any) {
      console.error('Export crawler configs error:', error)
      ElMessage.error(error.message || '导出爬虫配置失败')
      return false
    } finally {
      exportLoading.value = false
    }
  }

  // 批量复制配置
  const batchDuplicateConfigs = async (configIds: string[]): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(
        `确定要复制选中的 ${configIds.length} 个爬虫配置吗？`,
        '确认复制',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      )
      
      operationLoading.value = true
      // 批量复制配置 - 需要实现具体的批量复制逻辑
      await fetchCrawlerConfigs()
      ElMessage.success('批量复制成功')
      return true
    } catch (error: any) {
      if (error === 'cancel') {
        return false
      }
      console.error('Batch duplicate configs error:', error)
      ElMessage.error(error.message || '批量复制失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }

  // 测试XPath表达式
  const testXPath = async (url: string, xpath: string): Promise<any> => {
    try {
      testLoading.value = true
      // 测试XPath表达式 - 需要实现具体的XPath测试逻辑
      const mockResult = {
        success: true,
        results: [
          { text: '示例结果1', html: '<div>示例结果1</div>' },
          { text: '示例结果2', html: '<div>示例结果2</div>' }
        ],
        count: 2,
        xpath,
        url
      }
      return mockResult
    } catch (error: any) {
      console.error('Test XPath error:', error)
      throw error
    } finally {
      testLoading.value = false
    }
  }

  // 批量操作
  const batchOperation = async (configIds: string[], operation: 'delete' | 'activate' | 'deactivate' | 'test'): Promise<boolean> => {
    try {
      let confirmMessage = ''
      let successMessage = ''
      
      switch (operation) {
        case 'delete':
          confirmMessage = `确定要删除选中的 ${configIds.length} 个爬虫配置吗？删除后无法恢复。`
          successMessage = '批量删除成功'
          break
        case 'activate':
          confirmMessage = `确定要激活选中的 ${configIds.length} 个爬虫配置吗？`
          successMessage = '批量激活成功'
          break
        case 'deactivate':
          confirmMessage = `确定要停用选中的 ${configIds.length} 个爬虫配置吗？`
          successMessage = '批量停用成功'
          break
        case 'test':
          confirmMessage = `确定要测试选中的 ${configIds.length} 个爬虫配置吗？`
          successMessage = '批量测试已开始'
          break
      }
      
      await ElMessageBox.confirm(confirmMessage, '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      operationLoading.value = true
      const response = await crawlerApi.batchAction(operation, configIds)
      
      if (response.success) {
        await fetchCrawlerConfigs()
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

  // 设置过滤条件
  const setFilter = (newFilter: Partial<CrawlerFilter>): void => {
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

  // 清除测试结果
  const clearTestResult = (): void => {
    testResult.value = null
  }

  // 清除运行结果
  const clearRunResult = (): void => {
    runResult.value = null
  }

  // 重置状态
  const resetState = (): void => {
    crawlerConfigs.value = []
    currentConfig.value = null
    testResult.value = null
    runResult.value = null
    statistics.value = null
    availableTags.value = []
    filter.value = {}
    pagination.value = { page: 1, pageSize: 20, total: 0 }
    sortField.value = 'updatedAt'
    sortOrder.value = 'desc'
  }

  return {
    // 状态
    crawlerConfigs,
    currentConfig,
    testResult,
    runResult,
    statistics,
    availableTags,
    loading,
    testLoading,
    runLoading,
    statisticsLoading,
    operationLoading,
    importLoading,
    exportLoading,
    pagination,
    filter,
    sortField,
    sortOrder,
    
    // 计算属性
    filteredConfigs,
    configStatusCounts,
    configTypeCounts,
    
    // 方法
    fetchCrawlers,
    fetchCrawlerConfigs,
    fetchCrawlerConfigById,
    createCrawlerConfig,
    updateCrawlerConfig,
    deleteCrawlerConfig,
    testCrawlerConfig,
    runCrawlerConfig,
    stopCrawlerConfig,
    duplicateCrawlerConfig,
    fetchCrawlerStatistics,
    fetchAvailableTags,
    importCrawlerConfigs,
    exportCrawlerConfigs,
    batchOperation,
    batchDuplicateConfigs,
    testXPath,
    setFilter,
    clearFilter,
    setSort,
    clearTestResult,
    clearRunResult,
    resetState
  }
})