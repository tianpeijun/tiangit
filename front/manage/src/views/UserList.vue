<template>
  <div class="user-list-container">
    <el-card>
      <div slot="header" class="card-header">
        <h3>用户管理</h3>
        <el-button type="primary" icon="el-icon-plus" @click="handleCreate">创建用户</el-button>
      </div>
      <div class="filter-bar">
        <el-input v-model="searchKeyword" placeholder="搜索用户名、姓名、工号" clearable style="width: 300px" @keyup.enter.native="loadUsers" />
        <el-select v-model="filterRole" placeholder="角色" clearable style="width: 150px; margin-left: 10px" @change="loadUsers">
          <el-option label="员工" value="employee" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-button type="primary" icon="el-icon-search" @click="loadUsers">搜索</el-button>
      </div>
      <el-table v-loading="loading" :data="users" style="width: 100%; margin-top: 20px">
        <el-table-column label="用户名" prop="username" width="120" />
        <el-table-column label="姓名" prop="real_name" width="100" />
        <el-table-column label="工号" prop="employee_id" width="120" />
        <el-table-column label="部门" prop="department" width="150" />
        <el-table-column label="角色" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
              {{ scope.row.role === 'admin' ? '管理员' : '员工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="积分" prop="points" width="100" />
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="text" size="small" @click="handleToggleStatus(scope.row)">
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button type="text" size="small" @click="handleResetPassword(scope.row)">重置密码</el-button>
            <el-button type="text" size="small" style="color: #F56C6C" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > 0"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 20px; text-align: center"
        @current-change="handlePageChange"
      />
    </el-card>
    
    <user-edit-dialog ref="userEditDialog" @success="loadUsers" />
    <user-create-dialog ref="userCreateDialog" @success="loadUsers" />
  </div>
</template>

<script>
import { deleteUser, toggleUserStatus, resetPassword } from '@/api/user'
import UserEditDialog from '@/components/UserEditDialog.vue'
import UserCreateDialog from '@/components/UserCreateDialog.vue'

export default {
  name: 'UserList',
  components: {
    UserEditDialog,
    UserCreateDialog
  },
  data() {
    return {
      searchKeyword: '',
      filterRole: '',
      loading: false
    }
  },
  computed: {
    users() {
      return this.$store.state.manageUser.users
    },
    total() {
      return this.$store.state.manageUser.total
    },
    page() {
      return this.$store.state.manageUser.page
    },
    pageSize() {
      return this.$store.state.manageUser.pageSize
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers(page = 1) {
      this.loading = true
      try {
        const params = { page, page_size: this.pageSize }
        if (this.searchKeyword) params.keyword = this.searchKeyword
        if (this.filterRole) params.role = this.filterRole
        await this.$store.dispatch('manageUser/getUsers', params)
      } catch (error) {
        console.error('Failed to load users:', error)
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.loadUsers(page)
    },
    handleCreate() {
      this.$refs.userCreateDialog.open()
    },
    handleEdit(user) {
      this.$refs.userEditDialog.open(user)
    },
    async handleToggleStatus(user) {
      try {
        await this.$confirm(`确定要${user.is_active ? '禁用' : '启用'}该用户吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await toggleUserStatus(user.id, { is_active: !user.is_active })
        this.$message.success('操作成功')
        this.loadUsers(this.page)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to toggle user status:', error)
        }
      }
    },
    async handleResetPassword(user) {
      try {
        const { value } = await this.$prompt('请输入新密码（6-8位，包含数字和字母）', '重置密码', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^(?=.*[0-9])(?=.*[a-zA-Z]).{6,8}$/,
          inputErrorMessage: '密码格式不正确'
        })
        await resetPassword(user.id, { new_password: value })
        this.$message.success('密码重置成功')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to reset password:', error)
        }
      }
    },
    async handleDelete(user) {
      try {
        await this.$confirm('确定要删除该用户吗？此操作不可恢复', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deleteUser(user.id)
        this.$message.success('删除成功')
        this.loadUsers(this.page)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete user:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
.user-list-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.filter-bar {
  display: flex;
  align-items: center;
}
</style>
