import request from '@/utils/request'

export const aiConfigAPI = {
  // 获取提示词配置
  getPrompts() {
    return request.get('/ai-config/prompts')
  },

  // 更新提示词配置
  updatePrompts(data) {
    return request.put('/ai-config/prompts', data)
  },

  // 获取模型配置
  getModels() {
    return request.get('/ai-config/models')
  },

  // 更新模型配置
  updateModels(data) {
    return request.put('/ai-config/models', data)
  },

  // 验证配置格式
  validateConfig(type, data) {
    return request.post(`/ai-config/validate/${type}`, data)
  }
}

export default aiConfigAPI