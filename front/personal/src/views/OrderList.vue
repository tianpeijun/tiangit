<template>
  <div class="order-list-container">
    <el-card>
      <div slot="header">
        <h3>我的订单</h3>
      </div>
      <div v-loading="loading">
        <el-table v-if="orders.length > 0" :data="orders" style="width: 100%">
          <el-table-column label="订单号" prop="order_no" min-width="180" />
          <el-table-column label="总积分" width="120">
            <template slot-scope="scope">
              <span class="points-text">{{ scope.row.total_points }} 积分</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template slot-scope="scope">
              <el-tag type="success">已完成</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="收货地址" prop="shipping_address" min-width="200" show-overflow-tooltip />
          <el-table-column label="联系电话" prop="shipping_phone" width="130" />
          <el-table-column label="兑换时间" width="180">
            <template slot-scope="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template slot-scope="scope">
              <el-button type="text" size="small" @click="goToDetail(scope.row.id)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无订单" />
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
  name: 'OrderList',
  data() {
    return {
      loading: false
    }
  },
  computed: {
    orders() {
      return this.$store.state.order.orders
    },
    total() {
      return this.$store.state.order.total
    },
    page() {
      return this.$store.state.order.page
    },
    pageSize() {
      return this.$store.state.order.pageSize
    }
  },
  mounted() {
    this.loadOrders()
  },
  methods: {
    async loadOrders(page = 1) {
      this.loading = true
      try {
        await this.$store.dispatch('order/getOrders', { page, page_size: this.pageSize })
      } catch (error) {
        console.error('Failed to load orders:', error)
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.loadOrders(page)
    },
    goToDetail(id) {
      this.$router.push(`/orders/${id}`)
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.order-list-container {
  padding: 20px 0;
}

.points-text {
  color: #F56C6C;
  font-weight: bold;
}
</style>
