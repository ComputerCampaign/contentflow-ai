import api from '../../api/crawler'

const state = {
  tasks: [],
  currentTask: null,
  templates: [],
  loading: false,
  error: null
}

const getters = {
  allTasks: state => state.tasks,
  currentTask: state => state.currentTask,
  availableTemplates: state => state.templates,
  isLoading: state => state.loading,
  error: state => state.error
}

const actions = {
  // 获取用户的爬虫任务列表
  async fetchTasks({ commit }) {
    commit('setLoading', true)
    try {
      const response = await api.getTasks()
      commit('setTasks', response.data.tasks)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取任务列表失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 获取任务详情
  async fetchTaskDetail({ commit }, taskId) {
    commit('setLoading', true)
    try {
      const response = await api.getTaskDetail(taskId)
      commit('setCurrentTask', response.data)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取任务详情失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 创建新的爬虫任务
  async createTask({ commit }, taskData) {
    commit('setLoading', true)
    try {
      const response = await api.createTask(taskData)
      // 创建成功后刷新任务列表
      commit('addTask', response.data)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '创建任务失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 获取可用的博客模板
  async fetchTemplates({ commit }) {
    commit('setLoading', true)
    try {
      const response = await api.getTemplates()
      commit('setTemplates', response.data.templates)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取模板列表失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 清除错误信息
  clearError({ commit }) {
    commit('setError', null)
  }
}

const mutations = {
  setTasks(state, tasks) {
    state.tasks = tasks
  },
  setCurrentTask(state, task) {
    state.currentTask = task
  },
  addTask(state, task) {
    state.tasks.unshift(task)
  },
  setTemplates(state, templates) {
    state.templates = templates
  },
  setLoading(state, status) {
    state.loading = status
  },
  setError(state, error) {
    state.error = error
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}