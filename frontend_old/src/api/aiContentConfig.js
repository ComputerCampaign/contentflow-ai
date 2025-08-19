import request from '@/utils/request'

// AI内容配置相关API接口
export const aiContentConfigAPI = {
  // 获取AI内容配置列表
  getConfigs(params = {}) {
    return request.get('/ai-content/configs', { params })
  },

  // 创建新AI内容配置
  createConfig(data) {
    return request.post('/ai-content/configs', data)
  },

  // 获取单个AI内容配置详情
  getConfig(configId) {
    return request.get(`/ai-content/configs/${configId}`)
  },

  // 更新AI内容配置
  updateConfig(configId, data) {
    return request.put(`/ai-content/configs/${configId}`, data)
  },

  // 删除AI内容配置
  deleteConfig(configId) {
    return request.delete(`/ai-content/configs/${configId}`)
  },

  // 批量操作配置
  batchOperation(data) {
    return request.post('/ai-content/configs/batch', data)
  },

  // 导出配置
  exportConfigs(params = {}) {
    return request.get('/ai-content/configs/export', { params })
  },

  // 导入配置
  importConfigs(data) {
    return request.post('/ai-content/configs/import', data)
  },

  // 获取统计信息
  getStats(params = {}) {
    return request.get('/ai-content/configs/stats', { params })
  },

  // 克隆配置
  cloneConfig(configId) {
    return request.post(`/ai-content/configs/${configId}/clone`)
  }
}

export default aiContentConfigAPI