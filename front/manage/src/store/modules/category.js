import { getCategories } from '@/api/category'

const state = {
  categories: []
}

const mutations = {
  SET_CATEGORIES(state, categories) {
    state.categories = categories
  }
}

const actions = {
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
