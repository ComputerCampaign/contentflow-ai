import api from './index'

export default {
  // 获取用户的爬虫任务列表
  getTasks() {
    return api.get('/crawler/tasks')
  },
  
  // 获取任务详情
  getTaskDetail(taskId) {
    return api.get(`/crawler/tasks/${taskId}`)
  },
  
  // 创建新的爬虫任务
  createTask(taskData) {
    return api.post('/crawler/tasks', taskData)
  },
  
  // 获取可用的博客模板
  getTemplates() {
    return api.get('/crawler/templates')
  }
}