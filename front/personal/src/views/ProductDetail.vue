<template>
  <div v-loading="loading" class="product-detail-container">
    <el-card v-if="product">
      <el-row :gutter="40">
        <el-col :span="12">
          <el-carousel v-if="product.images && product.images.length > 0" height="400px">
            <el-carousel-item v-for="image in product.images" :key="image.id">
              <img :src="image.image_url" :alt="product.name" class="carousel-image">
            </el-carousel-item>
          </el-carousel>
          <div v-else class="placeholder-image">
            <img src="/static/placeholder.png" alt="No image">
          </div>
        </el-col>
        <el-col :span="12">
          <h2>{{ product.name }}</h2>
          <div class="product-meta">
            <el-tag v-if="product.status === 'active'" type="success">已上架</el-tag>
            <el-tag v-else type="info">已下架</el-tag>
          </div>
          <div class="product-points">
            <span class="points-label">所需积分：</span>
            <span class="points-value">{{ product.points_required }}</span>
          </div>
          <div class="product-description">
            <h4>产品描述</h4>
            <p>{{ product.description || '暂无描述' }}</p>
          </div>
          <div class="product-categories" v-if="product.categories && product.categories.length > 0">
            <h4>产品分类</h4>
            <el-tag v-for="category in product.categories" :key="category.id" size="small" style="margin-right: 8px">
              {{ category.name }}
            </el-tag>
          </div>
          <div class="product-actions">
            <el-input-number v-model="quantity" :min="1" :max="100" />
            <el-button type="primary" size="large" :disabled="product.status !== 'active'" @click="handleAddToCart">
              加入购物车
            </el-button>
            <el-button size="large" @click="$router.back()">返回</el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'ProductDetail',
  data() {
    return {
      loading: false,
      quantity: 1
    }
  },
  computed: {
    product() {
      return this.$store.state.product.productDetail
    }
  },
  mounted() {
    this.loadProduct()
  },
  methods: {
    async loadProduct() {
      this.loading = true
      try {
        await this.$store.dispatch('product/getProductDetail', this.$route.params.id)
      } catch (error) {
        console.error('Failed to load product:', error)
        this.$message.error('加载产品失败')
        this.$router.back()
      } finally {
        this.loading = false
      }
    },
    async handleAddToCart() {
      try {
        await this.$store.dispatch('cart/addToCart', {
          product_id: this.product.id,
          quantity: this.quantity
        })
        this.$message.success('已加入购物车')
        this.quantity = 1
      } catch (error) {
        console.error('Failed to add to cart:', error)
      }
    }
  }
}
</script>

<style scoped>
.product-detail-container {
  padding: 20px 0;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.placeholder-image {
  width: 100%;
  height: 400px;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-image img {
  max-width: 100%;
  max-height: 100%;
}

.product-meta {
  margin: 15px 0;
}

.product-points {
  margin: 20px 0;
  font-size: 24px;
}

.points-label {
  color: #606266;
}

.points-value {
  color: #F56C6C;
  font-weight: bold;
  font-size: 32px;
}

.product-description,
.product-categories {
  margin: 20px 0;
}

.product-description h4,
.product-categories h4 {
  margin-bottom: 10px;
  color: #303133;
}

.product-description p {
  color: #606266;
  line-height: 1.6;
}

.product-actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  align-items: center;
}
</style>
