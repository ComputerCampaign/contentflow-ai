import api from '../../api/xpath'

const state = {
  userRules: [],
  systemRules: [],
  currentRule: null,
  loading: false,
  error: null
}

const getters = {
  userRules: state => state.userRules,
  systemRules: state => state.systemRules,
  allRules: state => [...state.userRules, ...state.systemRules],
  currentRule: state => state.currentRule,
  isLoading: state => state.loading,
  error: state => state.error
}

const actions = {
  // 获取用户的XPath规则列表
  async fetchUserRules({ commit }) {
    commit('setLoading', true)
    try {
      const response = await api.getUserRules()
      commit('setUserRules', response.data.rules)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取用户规则列表失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 获取系统预设的XPath规则列表
  async fetchSystemRules({ commit }) {
    commit('setLoading', true)
    try {
      const response = await api.getSystemRules()
      commit('setSystemRules', response.data.rules)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取系统规则列表失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 获取规则详情
  async fetchRuleDetail({ commit }, ruleId) {
    commit('setLoading', true)
    try {
      const response = await api.getRuleDetail(ruleId)
      commit('setCurrentRule', response.data)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取规则详情失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 创建新的XPath规则
  async createRule({ commit }, ruleData) {
    commit('setLoading', true)
    try {
      const response = await api.createRule(ruleData)
      // 创建成功后刷新规则列表
      const newRule = {
        id: response.data.id,
        rule_name: response.data.rule_name,
        ...ruleData
      }
      commit('addUserRule', newRule)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '创建规则失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 更新XPath规则
  async updateRule({ commit }, { ruleId, ruleData }) {
    commit('setLoading', true)
    try {
      const response = await api.updateRule(ruleId, ruleData)
      // 更新成功后刷新规则列表
      commit('updateUserRule', { id: ruleId, ...ruleData })
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '更新规则失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 删除XPath规则
  async deleteRule({ commit }, ruleId) {
    commit('setLoading', true)
    try {
      const response = await api.deleteRule(ruleId)
      // 删除成功后从列表中移除
      commit('removeUserRule', ruleId)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '删除规则失败')
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
  setUserRules(state, rules) {
    state.userRules = rules
  },
  setSystemRules(state, rules) {
    state.systemRules = rules
  },
  setCurrentRule(state, rule) {
    state.currentRule = rule
  },
  addUserRule(state, rule) {
    state.userRules.unshift(rule)
  },
  updateUserRule(state, updatedRule) {
    const index = state.userRules.findIndex(rule => rule.id === updatedRule.id)
    if (index !== -1) {
      state.userRules.splice(index, 1, { ...state.userRules[index], ...updatedRule })
    }
  },
  removeUserRule(state, ruleId) {
    state.userRules = state.userRules.filter(rule => rule.id !== ruleId)
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