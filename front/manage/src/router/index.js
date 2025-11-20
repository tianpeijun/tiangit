import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/users',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/UserList.vue')
      },
      {
        path: 'products',
        name: 'ProductList',
        component: () => import('@/views/ProductList.vue')
      },
      {
        path: 'products/edit/:id?',
        name: 'ProductEdit',
        component: () => import('@/views/ProductEdit.vue')
      },
      {
        path: 'categories',
        name: 'CategoryList',
        component: () => import('@/views/CategoryList.vue')
      },
      {
        path: 'points',
        name: 'PointGrant',
        component: () => import('@/views/PointGrant.vue')
      },
      {
        path: 'logs',
        name: 'AdminLogList',
        component: () => import('@/views/AdminLogList.vue')
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: '/manage/',
  routes
})

// 解决 NavigationDuplicated 错误
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => {
    if (err.name !== 'NavigationDuplicated') {
      throw err
    }
  })
}

router.beforeEach((to, from, next) => {
  const sessionId = localStorage.getItem('session_id')
  const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
  
  if (to.meta.requiresAuth !== false && !sessionId) {
    next('/login')
  } else if (to.meta.requiresAuth !== false && userInfo.role !== 'admin') {
    next('/login')
  } else if (to.path === '/login' && sessionId && userInfo.role === 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router
