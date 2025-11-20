import { createOrder, getOrders, getOrderDetail } from '@/api/order'

const state = {
  orders: [],
  orderDetail: null,
  total: 0,
  page: 1,
  pageSize: 20
}

const mutations = {
  SET_ORDERS(state, data) {
    state.orders = data.items
    state.total = data.total
    state.page = data.page
    state.pageSize = data.page_size
  },
  SET_ORDER_DETAIL(state, order) {
    state.orderDetail = order
  }
}

const actions = {
  async createOrder({ dispatch }, payload) {
    const data = await createOrder(payload)
    return data
  },
  
  async getOrders({ commit }, params) {
    const data = await getOrders(params)
    commit('SET_ORDERS', data)
    return data
  },
  
  async getOrderDetail({ commit }, id) {
    const data = await getOrderDetail(id)
    commit('SET_ORDER_DETAIL', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
