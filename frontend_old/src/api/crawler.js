import request from '@/utils/request'

// 爬虫配置相关API接口
export const crawlerAPI = {
  // 获取爬虫配置列表
  getConfigs(params = {}) {
    return request.get('/crawler/configs', { params })
  },

  // 创建新爬虫配置
  createConfig(data) {
    return request.post('/crawler/configs', data)
  },

  // 获取单个爬虫配置详情
  getConfig(configId) {
    return request.get(`/crawler/configs/${configId}`)
  },

  // 更新爬虫配置
  updateConfig(configId, data) {
    return request.put(`/crawler/configs/${configId}`, data)
  },

  // 删除爬虫配置
  deleteConfig(configId) {
    return request.delete(`/crawler/configs/${configId}`)
  },

  // 测试爬虫配置
  testConfig(data) {
    return request.post('/crawler/test', data)
  },

  // 验证爬虫配置
  validateConfig(data) {
    return request.post('/crawler/validate', data)
  },

  // 获取爬虫结果
  getResults(configId, params = {}) {
    return request.get(`/crawler/configs/${configId}/results`, { params })
  },

  // 批量操作配置
  batchOperation(data) {
    return request.post('/crawler/configs/batch', data)
  },

  // 导出配置
  exportConfigs(params = {}) {
    return request.get('/crawler/configs/export', { params, responseType: 'blob' })
  },

  // 导入配置
  importConfigs(data) {
    return request.post('/crawler/configs/import', data)
  },

  // 获取配置统计信息
  getStats(params = {}) {
    return request.get('/crawler/stats', { params })
  },

  // 克隆配置
  cloneConfig(configId) {
    return request.post(`/crawler/configs/${configId}/clone`)
  },

  // 生成爬虫命令
  getCommand(configId, params = {}) {
    return request.get(`/crawler/configs/${configId}/command`, { params })
  },

  // 直接URL调用，避免参数序列化问题
  getCommandDirect(url) {
    return request.get(url)
  }
}

export default crawlerAPI