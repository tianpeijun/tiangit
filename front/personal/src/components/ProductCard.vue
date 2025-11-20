<template>
  <el-card class="product-card" :body-style="{ padding: '0px' }" shadow="hover" @click.native="$emit('click')">
    <div class="product-image">
      <img :src="getImageUrl(product.thumbnail_url)" :alt="product.name">
    </div>
    <div class="product-info">
      <h4 class="product-name">{{ product.name }}</h4>
      <p class="product-desc">{{ product.description || '暂无描述' }}</p>
      <div class="product-footer">
        <span class="product-points">{{ product.points_required }} 积分</span>
        <el-button type="primary" size="small" @click.stop="handleAddToCart">加入购物车</el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import { getImageUrl } from '@/utils/image'

export default {
  name: 'ProductCard',
  props: {
    product: {
      type: Object,
      required: true
    }
  },
  methods: {
    getImageUrl,
    async handleAddToCart() {
      try {
        await this.$store.dispatch('cart/addToCart', {
          product_id: this.product.id,
          quantity: 1
        })
        this.$message.success('已加入购物车')
      } catch (error) {
        console.error('Failed to add to cart:', error)
      }
    }
  }
}
</script>

<style scoped>
.product-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background-color: #f5f5f5;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 16px;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  font-size: 12px;
  color: #909399;
  margin: 0 0 12px 0;
  height: 36px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-points {
  font-size: 18px;
  font-weight: bold;
  color: #F56C6C;
}
</style>
