<template>
  <div v-loading="loading" class="order-detail-container">
    <el-card v-if="order">
      <div slot="header" class="order-header">
        <h3>订单详情</h3>
        <el-button size="small" @click="$router.back()">返回</el-button>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag type="success">已完成</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总积分">
          <span class="points-text">{{ order.total_points }} 积分</span>
        </el-descriptions-item>
        <el-descriptions-item label="兑换时间">{{ formatDate(order.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ order.shipping_address }}</el-descriptions-item>
        <el-descriptions-item label="联系电话" :span="2">{{ order.shipping_phone }}</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin: 30px 0 15px 0">订单明细</h4>
      <el-table :data="order.items" border style="width: 100%">
        <el-table-column label="产品名称" prop="product_name" min-width="200" />
        <el-table-column label="单价" width="120">
          <template slot-scope="scope">
            <span class="points-text">{{ scope.row.points_per_item }} 积分</span>
          </template>
        </el-table-column>
        <el-table-column label="数量" prop="quantity" width="100" />
        <el-table-column label="小计" width="120">
          <template slot-scope="scope">
            <span class="points-text">{{ scope.row.subtotal_points }} 积分</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'OrderDetail',
  data() {
    return {
      loading: false
    }
  },
  computed: {
    order() {
      return this.$store.state.order.orderDetail
    }
  },
  mounted() {
    this.loadOrder()
  },
  methods: {
    async loadOrder() {
      this.loading = true
      try {
        await this.$store.dispatch('order/getOrderDetail', this.$route.params.id)
      } catch (error) {
        console.error('Failed to load order:', error)
        this.$message.error('加载订单失败')
        this.$router.back()
      } finally {
        this.loading = false
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.order-detail-container {
  padding: 20px 0;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-header h3 {
  margin: 0;
}

.points-text {
  color: #F56C6C;
  font-weight: bold;
}
</style>
