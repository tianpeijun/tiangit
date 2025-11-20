<template>
  <div class="point-transactions-container">
    <el-card>
      <div slot="header">
        <h3>积分明细</h3>
        <div class="balance-info">
          <span>当前余额：</span>
          <span class="balance-value">{{ userPoints }} 积分</span>
        </div>
      </div>
      <div v-loading="loading">
        <el-table v-if="transactions.length > 0" :data="transactions" style="width: 100%">
          <el-table-column label="时间" width="180">
            <template slot-scope="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="类型" width="100">
            <template slot-scope="scope">
              <el-tag :type="scope.row.transaction_type === 'grant' ? 'success' : 'danger'">
                {{ scope.row.transaction_type === 'grant' ? '获得' : '消费' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="积分变动" width="150">
            <template slot-scope="scope">
              <span :class="scope.row.transaction_type === 'grant' ? 'grant-points' : 'consume-points'">
                {{ scope.row.transaction_type === 'grant' ? '+' : '-' }}{{ scope.row.amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="余额" width="120">
            <template slot-scope="scope">
              <span class="balance-text">{{ scope.row.balance_after }}</span>
            </template>
          </el-table-column>
          <el-table-column label="说明" min-width="200">
            <template slot-scope="scope">
              <span v-if="scope.row.description">{{ scope.row.description }}</span>
              <span v-else-if="scope.row.transaction_type === 'grant'">
                管理员发放（{{ scope.row.admin_name }}）
              </span>
              <span v-else>订单消费</span>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无积分明细" />
      </div>
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
  </div>
</template>

<script>
export default {
  name: 'PointTransactions',
  data() {
    return {
      loading: false
    }
  },
  computed: {
    userPoints() {
      return this.$store.state.user.userInfo?.points || 0
    },
    transactions() {
      return this.$store.state.point.transactions
    },
    total() {
      return this.$store.state.point.total
    },
    page() {
      return this.$store.state.point.page
    },
    pageSize() {
      return this.$store.state.point.pageSize
    }
  },
  mounted() {
    this.loadTransactions()
  },
  methods: {
    async loadTransactions(page = 1) {
      this.loading = true
      try {
        await this.$store.dispatch('point/getPointsTransactions', { page, page_size: this.pageSize })
      } catch (error) {
        console.error('Failed to load transactions:', error)
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.loadTransactions(page)
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.point-transactions-container {
  padding: 20px 0;
}

.balance-info {
  font-size: 18px;
  margin-top: 10px;
}

.balance-value {
  color: #67C23A;
  font-weight: bold;
  font-size: 24px;
}

.grant-points {
  color: #67C23A;
  font-weight: bold;
}

.consume-points {
  color: #F56C6C;
  font-weight: bold;
}

.balance-text {
  font-weight: bold;
}
</style>
