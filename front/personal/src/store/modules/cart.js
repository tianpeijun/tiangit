import { getCart, addToCart, updateCartItem, removeFromCart, clearCart } from '@/api/cart'

const state = {
  cartItems: [],
  totalQuantity: 0,
  totalPoints: 0
}

const mutations = {
  SET_CART(state, data) {
    state.cartItems = data.items
    state.totalQuantity = data.total_quantity
    state.totalPoints = data.total_points
  }
}

const actions = {
  async getCart({ commit }) {
    const data = await getCart()
    commit('SET_CART', data)
    return data
  },
  
  async addToCart({ dispatch }, payload) {
    await addToCart(payload)
    await dispatch('getCart')
  },
  
  async updateCartItem({ dispatch }, payload) {
    await updateCartItem(payload)
    await dispatch('getCart')
  },
  
  async removeFromCart({ dispatch }, productId) {
    await removeFromCart(productId)
    await dispatch('getCart')
  },
  
  async clearCart({ dispatch }) {
    await clearCart()
    await dispatch('getCart')
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
