import { getProducts, getProductDetail, searchProducts, getCategories } from '@/api/product'

const state = {
  products: [],
  productDetail: null,
  categories: [],
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
  },
  SET_PRODUCT_DETAIL(state, product) {
    state.productDetail = product
  },
  SET_CATEGORIES(state, categories) {
    state.categories = categories
  }
}

const actions = {
  async getProducts({ commit }, params) {
    const data = await getProducts(params)
    commit('SET_PRODUCTS', data)
    return data
  },
  
  async getProductDetail({ commit }, id) {
    const data = await getProductDetail(id)
    commit('SET_PRODUCT_DETAIL', data)
    return data
  },
  
  async searchProducts({ commit }, params) {
    const data = await searchProducts(params)
    commit('SET_PRODUCTS', data)
    return data
  },
  
  async getCategories({ commit }) {
    const data = await getCategories()
    commit('SET_CATEGORIES', data)
    return data
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
