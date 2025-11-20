import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import manageUser from './modules/manageUser'
import product from './modules/product'
import category from './modules/category'
import log from './modules/log'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user,
    manageUser,
    product,
    category,
    log
  }
})
