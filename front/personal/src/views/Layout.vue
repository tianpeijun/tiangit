<template>
  <div class="layout-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2 @click="$router.push('/')">AWSomeShop</h2>
        </div>
        <div class="header-center">
          <el-menu :default-active="activeMenu" mode="horizontal" router>
            <el-menu-item index="/products">产品列表</el-menu-item>
            <el-menu-item index="/cart">
              购物车
              <el-badge v-if="cartCount > 0" :value="cartCount" class="cart-badge" />
            </el-menu-item>
            <el-menu-item index="/orders">我的订单</el-menu-item>
            <el-menu-item index="/points">积分明细</el-menu-item>
          </el-menu>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <i class="el-icon-user"></i>
              {{ userInfo.real_name }}
              <span class="points-badge">{{ userInfo.points }} 积分</span>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="address">收货地址</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'Layout',
  data() {
    return {
      activeMenu: this.$route.path
    }
  },
  computed: {
    userInfo() {
      return this.$store.state.user.userInfo || {}
    },
    cartCount() {
      return this.$store.state.cart.totalQuantity
    }
  },
  watch: {
    $route(to) {
      this.activeMenu = to.path
    }
  },
  mounted() {
    this.loadUserData()
    this.loadCart()
  },
  methods: {
    async loadUserData() {
      try {
        await this.$store.dispatch('user/getCurrentUser')
      } catch (error) {
        console.error('Failed to load user data:', error)
      }
    },
    async loadCart() {
      try {
        await this.$store.dispatch('cart/getCart')
      } catch (error) {
        console.error('Failed to load cart:', error)
      }
    },
    handleCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
      } else if (command === 'profile') {
        this.$router.push('/profile')
      } else if (command === 'address') {
        this.$router.push('/address')
      }
    },
    async handleLogout() {
      try {
        await this.$store.dispatch('user/logout')
        this.$message.success('退出成功')
        this.$router.push('/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left h2 {
  color: #409EFF;
  cursor: pointer;
  margin: 0;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-center .el-menu {
  border-bottom: none;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.points-badge {
  background-color: #67C23A;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.cart-badge {
  margin-left: 5px;
}

.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
