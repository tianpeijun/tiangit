import { getUsers } from '@/api/user'

const state = {
  users: [],
  total: 0,
  page: 1,
  pageSize: 20
}

const mutations = {
  SET_USERS(state, data) {
    state.users = data.items
    state.total = data.total
    state.page = data.page
    state.pageSize = data.page_size
  }
}

const actions = {
  async getUsers({ commit }, params) {
    const data = await getUsers(params)
    commit('SET_USERS', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
