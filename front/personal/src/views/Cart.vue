<template>
  <div class="cart-container">
    <el-card>
      <div slot="header" class="cart-header">
        <h3>购物车</h3>
        <el-button v-if="cartItems.length > 0" type="danger" size="small" @click="handleClearCart">清空购物车</el-button>
      </div>
      <div v-loading="loading">
        <el-table v-if="cartItems.length > 0" :data="cartItems" style="width: 100%">
          <el-table-column label="产品" min-width="300">
            <template slot-scope="scope">
              <div class="product-info">
                <img :src="getImageUrl(scope.row.product_thumbnail)" class="product-thumbnail">
                <span>{{ scope.row.product_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template slot-scope="scope">
              <span class="points-text">{{ scope.row.points_per_item }} 积分</span>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="180">
            <template slot-scope="scope">
              <el-input-number
                v-model="scope.row.quantity"
                :min="1"
                :max="100"
                size="small"
                @change="handleUpdateQuantity(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template slot-scope="scope">
              <span class="points-text">{{ scope.row.subtotal_points }} 积分</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template slot-scope="scope">
              <el-button type="text" size="small" @click="handleRemove(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="购物车是空的" />
      </div>
      <div v-if="cartItems.length > 0" class="cart-footer">
        <div class="cart-summary">
          <div class="summary-item">
            <span>总数量：</span>
            <span class="summary-value">{{ totalQuantity }} 件</span>
          </div>
          <div class="summary-item">
            <span>总积分：</span>
            <span class="summary-value points-text">{{ totalPoints }} 积分</span>
          </div>
          <div class="summary-item">
            <span>当前余额：</span>
            <span class="summary-value" :class="{ 'insufficient': userPoints < totalPoints }">
              {{ userPoints }} 积分
            </span>
          </div>
        </div>
        <el-button
          type="primary"
          size="large"
          :disabled="userPoints < totalPoints"
          @click="handleCheckout"
        >
          {{ userPoints < totalPoints ? '积分不足' : '去结算' }}
        </el-button>
      </div>
    </el-card>
    
    <el-dialog title="确认收货信息" :visible.sync="checkoutDialogVisible" width="500px">
      <el-form ref="checkoutForm" :model="checkoutForm" :rules="checkoutRules" label-width="100px">
        <el-form-item label="收货地址" prop="shipping_address">
          <el-input v-model="checkoutForm.shipping_address" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="联系电话" prop="shipping_phone">
          <el-input v-model="checkoutForm.shipping_phone" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="checkoutDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitOrder">确认兑换</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAddress } from '@/api/profile'
import { getImageUrl } from '@/utils/image'

export default {
  name: 'Cart',
  data() {
    return {
      loading: false,
      checkoutDialogVisible: false,
      submitting: false,
      checkoutForm: {
        shipping_address: '',
        shipping_phone: ''
      },
      checkoutRules: {
        shipping_address: [{ required: true, message: '请输入收货地址', trigger: 'blur' }],
        shipping_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
      }
    }
  },
  computed: {
    cartItems() {
      return this.$store.state.cart.cartItems
    },
    totalQuantity() {
      return this.$store.state.cart.totalQuantity
    },
    totalPoints() {
      return this.$store.state.cart.totalPoints
    },
    userPoints() {
      return this.$store.state.user.userInfo?.points || 0
    }
  },
  mounted() {
    this.loadCart()
  },
  methods: {
    async loadCart() {
      this.loading = true
      try {
        await this.$store.dispatch('cart/getCart')
      } catch (error) {
        console.error('Failed to load cart:', error)
      } finally {
        this.loading = false
      }
    },
    async handleUpdateQuantity(item) {
      try {
        await this.$store.dispatch('cart/updateCartItem', {
          product_id: item.product_id,
          quantity: item.quantity
        })
      } catch (error) {
        console.error('Failed to update cart item:', error)
        this.loadCart()
      }
    },
    async handleRemove(item) {
      try {
        await this.$confirm('确定要删除该商品吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await this.$store.dispatch('cart/removeFromCart', item.product_id)
        this.$message.success('已删除')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to remove cart item:', error)
        }
      }
    },
    async handleClearCart() {
      try {
        await this.$confirm('确定要清空购物车吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await this.$store.dispatch('cart/clearCart')
        this.$message.success('已清空')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to clear cart:', error)
        }
      }
    },
    async handleCheckout() {
      try {
        const address = await getAddress()
        if (address) {
          this.checkoutForm.shipping_address = address.address
          this.checkoutForm.shipping_phone = address.phone
        }
      } catch (error) {
        console.error('Failed to load address:', error)
      }
      this.checkoutDialogVisible = true
    },
    handleSubmitOrder() {
      this.$refs.checkoutForm.validate(async valid => {
        if (!valid) return
        
        this.submitting = true
        try {
          const order = await this.$store.dispatch('order/createOrder', this.checkoutForm)
          this.$message.success('兑换成功')
          this.checkoutDialogVisible = false
          await this.$store.dispatch('user/getCurrentUser')
          await this.$store.dispatch('cart/getCart')
          this.$router.push(`/orders/${order.id}`)
        } catch (error) {
          console.error('Failed to create order:', error)
        } finally {
          this.submitting = false
        }
      })
    }
  }
}
</script>

<style scoped>
.cart-container {
  padding: 20px 0;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-header h3 {
  margin: 0;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.product-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.points-text {
  color: #F56C6C;
  font-weight: bold;
}

.cart-footer {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.cart-summary {
  display: flex;
  gap: 30px;
}

.summary-item {
  font-size: 16px;
}

.summary-value {
  font-weight: bold;
  margin-left: 10px;
}

.insufficient {
  color: #F56C6C;
}
</style>
