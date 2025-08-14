import request from '@/utils/request'

// 任务管理相关API接口
export const tasksAPI = {
  // 获取任务列表
  getTasks(params = {}) {
    return request.get('/tasks', { params })
  },

  // 创建新任务
  createTask(data) {
    return request.post('/tasks', data)
  },

  // 获取单个任务详情
  getTask(taskId) {
    return request.get(`/tasks/${taskId}`)
  },

  // 更新任务信息
  updateTask(taskId, data) {
    return request.put(`/tasks/${taskId}`, data)
  },

  // 删除任务
  deleteTask(taskId) {
    return request.delete(`/tasks/${taskId}`)
  },

  // 执行任务
  executeTask(taskId) {
    return request.post(`/tasks/${taskId}/execute`)
  },

  // 重试任务
  retryTask(taskId) {
    return request.post(`/tasks/${taskId}/retry`)
  },

  // 暂停任务
  pauseTask(taskId) {
    return request.post(`/tasks/${taskId}/pause`)
  },

  // 继续任务
  resumeTask(taskId) {
    return request.post(`/tasks/${taskId}/resume`)
  },

  // 停止任务
  stopTask(taskId) {
    return request.post(`/tasks/${taskId}/stop`)
  },

  // 获取任务执行日志
  getTaskLogs(taskId, params = {}) {
    return request.get(`/tasks/${taskId}/logs`, { params })
  },

  // 导出任务数据
  exportTasks(params = {}) {
    return request.get('/tasks/export', { params, responseType: 'blob' })
  },

  // 克隆任务
  cloneTask(taskId) {
    return request.post(`/tasks/${taskId}/clone`)
  },

  // 批量操作任务
  batchOperation(data) {
    return request.post('/tasks/batch', data)
  },

  // 获取任务统计信息
  getTaskStats(params = {}) {
    return request.get('/tasks/stats', { params })
  },

  // 创建爬虫任务
  createCrawlerTask(data) {
    return request.post('/tasks/crawler', data)
  },

  // 创建内容生成任务
  createContentGenerationTask(data) {
    return request.post('/tasks/content-generation', data)
  },

  // 创建组合任务
  createCombinedTask(data) {
    return request.post('/tasks/combined', data)
  },

  // 获取任务模板
  getTaskTemplates(params = {}) {
    return request.get('/tasks/templates', { params })
  },

  // 创建任务模板
  createTaskTemplate(data) {
    return request.post('/tasks/templates', data)
  },

  // 更新任务模板
  updateTaskTemplate(templateId, data) {
    return request.put(`/tasks/templates/${templateId}`, data)
  },

  // 删除任务模板
  deleteTaskTemplate(templateId) {
    return request.delete(`/tasks/templates/${templateId}`)
  },

  // 获取任务执行命令
  getTaskCommand(taskId) {
    return request.get(`/tasks/${taskId}/command`)
  }
}

export default tasksAPI