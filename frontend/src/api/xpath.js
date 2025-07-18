import api from './index'

export default {
  // 获取用户的XPath规则列表
  getUserRules() {
    return api.get('/xpath/rules')
  },
  
  // 获取系统预设的XPath规则列表
  getSystemRules() {
    return api.get('/xpath/system-rules')
  },
  
  // 获取规则详情
  getRuleDetail(ruleId) {
    return api.get(`/xpath/rules/${ruleId}`)
  },
  
  // 创建新的XPath规则
  createRule(ruleData) {
    return api.post('/xpath/rules', ruleData)
  },
  
  // 更新XPath规则
  updateRule(ruleId, ruleData) {
    return api.put(`/xpath/rules/${ruleId}`, ruleData)
  },
  
  // 删除XPath规则
  deleteRule(ruleId) {
    return api.delete(`/xpath/rules/${ruleId}`)
  }
}