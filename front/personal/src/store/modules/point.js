import { getPointsBalance, getPointsTransactions } from '@/api/point'

const state = {
  balance: 0,
  transactions: [],
  total: 0,
  page: 1,
  pageSize: 20
}

const mutations = {
  SET_BALANCE(state, balance) {
    state.balance = balance
  },
  SET_TRANSACTIONS(state, data) {
    state.transactions = data.items
    state.total = data.total
    state.page = data.page
    state.pageSize = data.page_size
  }
}

const actions = {
  async getPointsBalance({ commit }) {
    const data = await getPointsBalance()
    commit('SET_BALANCE', data.balance)
    return data
  },
  
  async getPointsTransactions({ commit }, params) {
    const data = await getPointsTransactions(params)
    commit('SET_TRANSACTIONS', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
