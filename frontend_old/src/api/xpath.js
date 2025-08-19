import request from '@/utils/request'

export const xpathAPI = {
  // 获取XPath规则列表
  getRules(params = {}) {
    return request.get('/xpath/rules', { params })
  },

  // 获取单个XPath规则
  getRule(ruleId) {
    return request.get(`/xpath/rules/${ruleId}`)
  },

  // 创建XPath规则
  createRule(data) {
    return request.post('/xpath/rules', data)
  },

  // 更新XPath规则
  updateRule(ruleId, data) {
    return request.put(`/xpath/rules/${ruleId}`, data)
  },

  // 删除XPath规则
  deleteRule(ruleId) {
    return request.delete(`/xpath/rules/${ruleId}`)
  },

  // 验证XPath规则
  validateRule(data) {
    return request.post('/xpath/rules/validate', data)
  },

  // 测试XPath规则
  testRule(data) {
    return request.post('/xpath/rules/test', data)
  },

  // 获取XPath规则统计信息
  getStats() {
    return request.get('/xpath/stats')
  },

  // 同步规则到JSON文件
  syncToJson() {
    return request.post('/xpath/sync/to-json')
  },

  // 从JSON文件同步规则
  syncFromJson() {
    return request.post('/xpath/sync/from-json')
  },

  // 双向同步规则
  syncBidirectional() {
    return request.post('/xpath/sync/bidirectional')
  },

  // 获取JSON文件信息
  getJsonInfo() {
    return request.get('/xpath/sync/json-info')
  }
}

export default xpathAPI