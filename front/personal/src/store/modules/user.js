import { login, logout, getCurrentUser } from '@/api/auth'

const state = {
  userInfo: JSON.parse(localStorage.getItem('user_info')) || null,
  sessionId: localStorage.getItem('session_id') || ''
}

const mutations = {
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
    if (userInfo) {
      localStorage.setItem('user_info', JSON.stringify(userInfo))
    } else {
      localStorage.removeItem('user_info')
    }
  },
  SET_SESSION_ID(state, sessionId) {
    state.sessionId = sessionId
    if (sessionId) {
      localStorage.setItem('session_id', sessionId)
    } else {
      localStorage.removeItem('session_id')
    }
  }
}

const actions = {
  async login({ commit }, loginForm) {
    const data = await login(loginForm)
    commit('SET_SESSION_ID', data.session_id)
    commit('SET_USER_INFO', data.user)
    return data
  },
  
  async logout({ commit }) {
    await logout()
    commit('SET_SESSION_ID', '')
    commit('SET_USER_INFO', null)
  },
  
  async getCurrentUser({ commit }) {
    const data = await getCurrentUser()
    commit('SET_USER_INFO', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
