import { getLogs } from '@/api/log'

const state = {
  logs: [],
  total: 0,
  page: 1,
  pageSize: 20
}

const mutations = {
  SET_LOGS(state, data) {
    state.logs = data.items
    state.total = data.total
    state.page = data.page
    state.pageSize = data.page_size
  }
}

const actions = {
  async getLogs({ commit }, params) {
    const data = await getLogs(params)
    commit('SET_LOGS', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
