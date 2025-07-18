import api from '../../api/user'

const state = {
  users: [],
  groups: [],
  currentUser: null,
  loading: false,
  error: null
}

const getters = {
  allUsers: state => state.users,
  allGroups: state => state.groups,
  currentUser: state => state.currentUser,
  isLoading: state => state.loading,
  error: state => state.error
}

const actions = {
  // 获取所有用户列表（仅管理员）
  async fetchUsers({ commit }) {
    commit('setLoading', true)
    try {
      const response = await api.getUsers()
      commit('setUsers', response.data.users)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取用户列表失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 获取用户详情（仅管理员）
  async fetchUserDetail({ commit }, userId) {
    commit('setLoading', true)
    try {
      const response = await api.getUserDetail(userId)
      commit('setCurrentUser', response.data)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取用户详情失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 更新用户信息（仅管理员）
  async updateUser({ commit }, { userId, userData }) {
    commit('setLoading', true)
    try {
      const response = await api.updateUser(userId, userData)
      // 更新成功后刷新用户列表
      commit('updateUserInList', { id: userId, ...userData })
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '更新用户信息失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 获取所有用户组
  async fetchGroups({ commit }) {
    commit('setLoading', true)
    try {
      const response = await api.getGroups()
      commit('setGroups', response.data.groups)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '获取用户组列表失败')
      return Promise.reject(error)
    } finally {
      commit('setLoading', false)
    }
  },
  
  // 创建新的用户组（仅管理员）
  async createGroup({ commit }, groupData) {
    commit('setLoading', true)
    try {
      const response = await api.createGroup(groupData)
      // 创建成功后刷新用户组列表
      const newGroup = {
        id: response.data.id,
        name: response.data.name,
        ...groupData
      }
      commit('addGroup', newGroup)
      return response
    } catch (error) {
      commit('setError', error.response?.data?.error || '创建用户组失败')
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
  setUsers(state, users) {
    state.users = users
  },
  setCurrentUser(state, user) {
    state.currentUser = user
  },
  updateUserInList(state, updatedUser) {
    const index = state.users.findIndex(user => user.id === updatedUser.id)
    if (index !== -1) {
      state.users.splice(index, 1, { ...state.users[index], ...updatedUser })
    }
  },
  setGroups(state, groups) {
    state.groups = groups
  },
  addGroup(state, group) {
    state.groups.push(group)
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