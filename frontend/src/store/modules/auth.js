import api from '../../api/auth'

const state = {
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  status: ''
}

const getters = {
  isAuthenticated: state => !!state.token,
  authStatus: state => state.status,
  currentUser: state => state.user,
  isAdmin: state => state.user && state.user.group && state.user.group.name === 'admin'
}

const actions = {
  // 用户登录
  async login({ commit }, user) {
    commit('auth_request')
    try {
      const response = await api.login(user)
      const token = response.data.token
      const userData = response.data.user
      
      // 保存令牌到本地存储
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // 设置API请求头的认证令牌
      api.setAuthHeader(token)
      
      commit('auth_success', { token, user: userData })
      return response
    } catch (error) {
      commit('auth_error')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      return Promise.reject(error)
    }
  },
  
  // 用户注册
  async register({ commit }, user) {
    commit('auth_request')
    try {
      const response = await api.register(user)
      return response
    } catch (error) {
      commit('auth_error')
      return Promise.reject(error)
    }
  },
  
  // 获取当前用户信息
  async getUserInfo({ commit }) {
    commit('auth_request')
    try {
      const response = await api.getUserInfo()
      const userData = response.data.user
      
      // 更新本地存储中的用户信息
      localStorage.setItem('user', JSON.stringify(userData))
      
      commit('set_user', userData)
      return response
    } catch (error) {
      commit('auth_error')
      return Promise.reject(error)
    }
  },
  
  // 用户登出
  logout({ commit }) {
    return new Promise(resolve => {
      commit('logout')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 移除API请求头的认证令牌
      api.removeAuthHeader()
      resolve()
    })
  }
}

const mutations = {
  auth_request(state) {
    state.status = 'loading'
  },
  auth_success(state, { token, user }) {
    state.status = 'success'
    state.token = token
    state.user = user
  },
  auth_error(state) {
    state.status = 'error'
  },
  set_user(state, user) {
    state.user = user
  },
  logout(state) {
    state.status = ''
    state.token = ''
    state.user = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}