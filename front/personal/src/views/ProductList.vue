<template>
  <div class="product-list-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="filter-card">
          <div slot="header">产品筛选</div>
          <div class="filter-section">
            <h4>搜索</h4>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索产品名称"
              clearable
              @keyup.enter.native="handleSearch"
            >
              <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
            </el-input>
          </div>
          <div class="filter-section">
            <h4>分类</h4>
            <el-tree
              :data="categories"
              :props="{ label: 'name', children: 'children' }"
              node-key="id"
              show-checkbox
              @check="handleCategoryChange"
            />
          </div>
          <div class="filter-section">
            <h4>排序</h4>
            <el-radio-group v-model="sortBy" @change="loadProducts">
              <el-radio label="created_desc">最新上架</el-radio>
              <el-radio label="points_asc">积分从低到高</el-radio>
            </el-radio-group>
          </div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <div v-loading="loading" class="products-grid">
          <product-card
            v-for="product in products"
            :key="product.id"
            :product="product"
            @click="goToDetail(product.id)"
          />
          <el-empty v-if="!loading && products.length === 0" description="暂无产品" />
        </div>
        <el-pagination
          v-if="total > 0"
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import ProductCard from '@/components/ProductCard.vue'

export default {
  name: 'ProductList',
  components: {
    ProductCard
  },
  data() {
    return {
      searchKeyword: '',
      selectedCategories: [],
      sortBy: 'created_desc',
      loading: false
    }
  },
  computed: {
    products() {
      return this.$store.state.product.products
    },
    categories() {
      return this.$store.state.product.categories
    },
    total() {
      return this.$store.state.product.total
    },
    page() {
      return this.$store.state.product.page
    },
    pageSize() {
      return this.$store.state.product.pageSize
    }
  },
  mounted() {
    this.loadCategories()
    this.loadProducts()
  },
  methods: {
    async loadCategories() {
      try {
        await this.$store.dispatch('product/getCategories')
      } catch (error) {
        console.error('Failed to load categories:', error)
      }
    },
    async loadProducts(page = 1) {
      this.loading = true
      try {
        const params = {
          page,
          page_size: this.pageSize,
          sort_by: this.sortBy
        }
        if (this.selectedCategories.length > 0) {
          params.category_ids = this.selectedCategories.join(',')
        }
        if (this.searchKeyword) {
          await this.$store.dispatch('product/searchProducts', { ...params, keyword: this.searchKeyword })
        } else {
          await this.$store.dispatch('product/getProducts', params)
        }
      } catch (error) {
        console.error('Failed to load products:', error)
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.loadProducts()
    },
    handleCategoryChange(data, checked) {
      this.selectedCategories = checked.checkedKeys
      this.loadProducts()
    },
    handlePageChange(page) {
      this.loadProducts(page)
    },
    goToDetail(id) {
      this.$router.push(`/products/${id}`)
    }
  }
}
</script>

<style scoped>
.product-list-container {
  padding: 20px 0;
}

.filter-card {
  position: sticky;
  top: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
  min-height: 400px;
}

.el-pagination {
  text-align: center;
}
</style>
