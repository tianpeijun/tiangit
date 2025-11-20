<template>
  <el-card>
    <div slot="header">
      <h3>操作日志</h3>
    </div>
    <div class="filter-bar">
      <el-select v-model="filterType" placeholder="操作类型" clearable style="width: 150px" @change="loadLogs">
        <el-option label="登录" value="LOGIN" />
        <el-option label="登出" value="LOGOUT" />
        <el-option label="创建" value="CREATE" />
        <el-option label="更新" value="UPDATE" />
        <el-option label="删除" value="DELETE" />
        <el-option label="发放积分" value="GRANT_POINTS" />
        <el-option label="重置密码" value="RESET_PASSWORD" />
      </el-select>
      <el-select v-model="filterModule" placeholder="操作模块" clearable style="width: 150px; margin-left: 10px" @change="loadLogs">
        <el-option label="用户" value="USER" />
        <el-option label="产品" value="PRODUCT" />
        <el-option label="分类" value="CATEGORY" />
        <el-option label="积分" value="POINTS" />
      </el-select>
    </div>
    <el-table v-loading="loading" :data="logs" style="width: 100%; margin-top: 20px">
      <el-table-column label="操作时间" width="180">
        <template slot-scope="scope">
          {{ new Date(scope.row.created_at).toLocaleString('zh-CN') }}
        </template>
      </el-table-column>
      <el-table-column label="操作人" prop="admin_name" width="120" />
      <el-table-column label="操作类型" width="120">
        <template slot-scope="scope">
          <el-tag :type="getTypeColor(scope.row.operation_type)">
            {{ getTypeLabel(scope.row.operation_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作模块" width="100">
        <template slot-scope="scope">
          {{ getModuleLabel(scope.row.operation_module) }}
        </template>
      </el-table-column>
      <el-table-column label="操作描述" prop="operation_desc" min-width="200" show-overflow-tooltip />
      <el-table-column label="IP地址" prop="ip_address" width="150" />
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
</template>

<script>
export default {
  name: 'AdminLogList',
  data() {
    return {
      loading: false,
      filterType: '',
      filterModule: ''
    }
  },
  computed: {
    logs() {
      return this.$store.state.log.logs
    },
    total() {
      return this.$store.state.log.total
    },
    page() {
      return this.$store.state.log.page
    },
    pageSize() {
      return this.$store.state.log.pageSize
    }
  },
  mounted() {
    this.loadLogs()
  },
  methods: {
    async loadLogs(page = 1) {
      this.loading = true
      try {
        const params = { page, page_size: this.pageSize }
        if (this.filterType) params.operation_type = this.filterType
        if (this.filterModule) params.operation_module = this.filterModule
        await this.$store.dispatch('log/getLogs', params)
      } catch (error) {
        console.error('Failed to load logs:', error)
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.loadLogs(page)
    },
    getTypeColor(type) {
      const colors = {
        LOGIN: 'success',
        LOGOUT: 'info',
        CREATE: 'success',
        UPDATE: 'warning',
        DELETE: 'danger',
        GRANT_POINTS: 'success',
        RESET_PASSWORD: 'warning'
      }
      return colors[type] || 'info'
    },
    getTypeLabel(type) {
      const labels = {
        LOGIN: '登录',
        LOGOUT: '登出',
        CREATE: '创建',
        UPDATE: '更新',
        DELETE: '删除',
        GRANT_POINTS: '发放积分',
        RESET_PASSWORD: '重置密码'
      }
      return labels[type] || type
    },
    getModuleLabel(module) {
      const labels = {
        USER: '用户',
        PRODUCT: '产品',
        CATEGORY: '分类',
        POINTS: '积分'
      }
      return labels[module] || module
    }
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
}
</style>
