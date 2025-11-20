<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>AWSomeShop</h2>
        <p>管理端</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/users">
          <i class="el-icon-user"></i>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <i class="el-icon-goods"></i>
          <span>产品管理</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <i class="el-icon-menu"></i>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/points">
          <i class="el-icon-coin"></i>
          <span>积分发放</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <i class="el-icon-document"></i>
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <i class="el-icon-user-solid"></i>
              {{ userInfo.real_name }}
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
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
    }
  },
  watch: {
    $route(to) {
      this.activeMenu = to.path
    }
  },
  mounted() {
    this.loadUserData()
  },
  methods: {
    async loadUserData() {
      try {
        await this.$store.dispatch('user/getCurrentUser')
      } catch (error) {
        console.error('Failed to load user data:', error)
      }
    },
    handleCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
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

.sidebar {
  background-color: #304156;
  overflow-x: hidden;
}

.logo {
  padding: 20px;
  text-align: center;
  color: #fff;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  margin: 0 0 5px 0;
  font-size: 20px;
}

.logo p {
  margin: 0;
  font-size: 12px;
  color: #bfcbd9;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.main-content {
  padding: 20px;
}
</style>
