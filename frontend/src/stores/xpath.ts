import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/utils/request'
import { ElMessage } from 'element-plus'

export interface XPathConfig {
  id: string
  name: string
  description?: string
  xpath: string
  extractType: 'text' | 'html' | 'attr' | 'href'
  attrName?: string
  status: 'active' | 'inactive'
  processing: string[]
  createdAt: string
  updatedAt: string
  usageCount?: number
}

export interface XPathTestConfig {
  url: string
  xpath: string
  extractType?: 'text' | 'html' | 'attr' | 'href'
  attrName?: string
  processing?: string[]
}

export interface XPathTestResult {
  success: boolean
  data?: string
  count?: number
  error?: string
  message?: string
}

export const useXPathStore = defineStore('xpath', () => {
  // State
  const xpathConfigs = ref<XPathConfig[]>([])
  const loading = ref(false)
  const currentConfig = ref<XPathConfig | null>(null)
  
  // Pagination
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  
  // Filters
  const searchKeyword = ref('')
  const statusFilter = ref('')
  const extractTypeFilter = ref('')
  
  // Sort
  const sortField = ref('createdAt')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  // Computed
  const filteredConfigs = computed(() => {
    let result = [...xpathConfigs.value]
    
    // 状态过滤
    if (statusFilter.value) {
      result = result.filter(config => config.status === statusFilter.value)
    }
    
    // 提取类型过滤
    if (extractTypeFilter.value) {
      result = result.filter(config => config.extractType === extractTypeFilter.value)
    }
    
    // 关键词过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      result = result.filter(config => 
        config.name.toLowerCase().includes(keyword) ||
        config.description?.toLowerCase().includes(keyword) ||
        config.xpath.toLowerCase().includes(keyword)
      )
    }
    
    return result
  })
  
  const paginatedConfigs = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return filteredConfigs.value.slice(start, end)
  })

  // Actions
  const fetchXPathConfigs = async (params?: any) => {
    try {
      loading.value = true
      const response = await apiClient.get('/api/xpath/configs', {
        page: currentPage.value,
        pageSize: pageSize.value,
        search: searchKeyword.value,
        status: statusFilter.value,
        extractType: extractTypeFilter.value,
        sortField: sortField.value,
        sortOrder: sortOrder.value,
        ...params
      })
      
      if (response.success) {
        xpathConfigs.value = response.data.configs || []
        total.value = response.data.total || 0
        return true
      } else {
        ElMessage.error(response.message || '获取XPath配置失败')
        return false
      }
    } catch (error) {
      console.error('Fetch xpath configs error:', error)
      ElMessage.error('获取XPath配置失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  const getXPathConfig = async (id: string) => {
    try {
      const response = await apiClient.get(`/api/xpath/configs/${id}`)
      
      if (response.success) {
        currentConfig.value = response.data
        return response.data
      } else {
        ElMessage.error(response.message || '获取XPath配置失败')
        return null
      }
    } catch (error) {
      console.error('Get xpath config error:', error)
      ElMessage.error('获取XPath配置失败')
      return null
    }
  }
  
  const createXPathConfig = async (configData: Partial<XPathConfig>) => {
    try {
      const response = await apiClient.post('/api/xpath/configs', configData)
      
      if (response.success) {
        await fetchXPathConfigs()
        return true
      } else {
        ElMessage.error(response.message || '创建XPath配置失败')
        return false
      }
    } catch (error) {
      console.error('Create xpath config error:', error)
      ElMessage.error('创建XPath配置失败')
      return false
    }
  }
  
  const updateXPathConfig = async (id: string, configData: Partial<XPathConfig>) => {
    try {
      const response = await apiClient.put(`/api/xpath/configs/${id}`, configData)
      
      if (response.success) {
        await fetchXPathConfigs()
        return true
      } else {
        ElMessage.error(response.message || '更新XPath配置失败')
        return false
      }
    } catch (error) {
      console.error('Update xpath config error:', error)
      ElMessage.error('更新XPath配置失败')
      return false
    }
  }
  
  const deleteXPathConfig = async (id: string) => {
    try {
      const response = await apiClient.delete(`/api/xpath/configs/${id}`)
      
      if (response.success) {
        await fetchXPathConfigs()
        ElMessage.success('删除成功')
        return true
      } else {
        ElMessage.error(response.message || '删除XPath配置失败')
        return false
      }
    } catch (error) {
      console.error('Delete xpath config error:', error)
      ElMessage.error('删除XPath配置失败')
      return false
    }
  }
  
  const batchDeleteXPathConfigs = async (ids: string[]) => {
    try {
      const response = await apiClient.post('/api/xpath/configs/batch-delete', { ids })
      
      if (response.success) {
        await fetchXPathConfigs()
        ElMessage.success(`成功删除 ${ids.length} 个配置`)
        return true
      } else {
        ElMessage.error(response.message || '批量删除失败')
        return false
      }
    } catch (error) {
      console.error('Batch delete xpath configs error:', error)
      ElMessage.error('批量删除失败')
      return false
    }
  }
  
  const testXPath = async (testConfig: XPathTestConfig): Promise<XPathTestResult> => {
    try {
      const response = await apiClient.post('/api/xpath/test', testConfig)
      
      if (response.success) {
        return {
          success: true,
          data: JSON.stringify(response.data.results, null, 2),
          count: response.data.count
        }
      } else {
        return {
          success: false,
          error: response.message || '测试失败'
        }
      }
    } catch (error) {
      console.error('Test xpath error:', error)
      return {
        success: false,
        error: '测试过程中发生错误'
      }
    }
  }
  
  const duplicateXPathConfig = async (id: string) => {
    try {
      const response = await apiClient.post(`/api/xpath/configs/${id}/duplicate`)
      
      if (response.success) {
        await fetchXPathConfigs()
        ElMessage.success('复制成功')
        return true
      } else {
        ElMessage.error(response.message || '复制XPath配置失败')
        return false
      }
    } catch (error) {
      console.error('Duplicate xpath config error:', error)
      ElMessage.error('复制XPath配置失败')
      return false
    }
  }
  
  const toggleXPathConfigStatus = async (id: string, status: 'active' | 'inactive') => {
    try {
      const response = await apiClient.put(`/api/xpath/configs/${id}/status`, { status })
      
      if (response.success) {
        await fetchXPathConfigs()
        ElMessage.success(`${status === 'active' ? '启用' : '禁用'}成功`)
        return true
      } else {
        ElMessage.error(response.message || '状态更新失败')
        return false
      }
    } catch (error) {
      console.error('Toggle xpath config status error:', error)
      ElMessage.error('状态更新失败')
      return false
    }
  }
  
  // Pagination
  const setPagination = (page: number, size?: number) => {
    currentPage.value = page
    if (size) {
      pageSize.value = size
    }
  }
  
  // Filters
  const setFilter = (filters: {
    search?: string
    status?: string
    extractType?: string
  }) => {
    if (filters.search !== undefined) {
      searchKeyword.value = filters.search
    }
    if (filters.status !== undefined) {
      statusFilter.value = filters.status
    }
    if (filters.extractType !== undefined) {
      extractTypeFilter.value = filters.extractType
    }
    currentPage.value = 1 // Reset to first page when filtering
  }
  
  const clearFilter = () => {
    searchKeyword.value = ''
    statusFilter.value = ''
    extractTypeFilter.value = ''
    currentPage.value = 1
  }
  
  // Sort
  const setSort = (field: string, order: 'asc' | 'desc') => {
    sortField.value = field
    sortOrder.value = order
  }
  
  // Reset state
  const resetState = () => {
    xpathConfigs.value = []
    currentConfig.value = null
    currentPage.value = 1
    pageSize.value = 20
    total.value = 0
    clearFilter()
    sortField.value = 'createdAt'
    sortOrder.value = 'desc'
  }

  return {
    // State
    xpathConfigs,
    loading,
    currentConfig,
    currentPage,
    pageSize,
    total,
    searchKeyword,
    statusFilter,
    extractTypeFilter,
    sortField,
    sortOrder,
    
    // Computed
    filteredConfigs,
    paginatedConfigs,
    
    // Actions
    fetchXPathConfigs,
    getXPathConfig,
    createXPathConfig,
    updateXPathConfig,
    deleteXPathConfig,
    batchDeleteXPathConfigs,
    testXPath,
    duplicateXPathConfig,
    toggleXPathConfigStatus,
    setPagination,
    setFilter,
    clearFilter,
    setSort,
    resetState
  }
})