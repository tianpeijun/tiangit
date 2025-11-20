import { getProducts } from '@/api/product'

const state = {
  products: [],
  total: 0,
  page: 1,
  pageSize: 20
}

const mutations = {
  SET_PRODUCTS(state, data) {
    state.products = data.items
    state.total = data.total
    state.page = data.page
    state.pageSize = data.page_size
  }
}

const actions = {
  async getProducts({ commit }, params) {
    const data = await getProducts(params)
    commit('SET_PRODUCTS', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
