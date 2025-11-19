<template>
  <div class="product-list-container">
    <el-card>
      <div slot="header" class="card-header">
        <h3>产品管理</h3>
        <el-button type="primary" icon="el-icon-plus" @click="$router.push('/products/edit')">创建产品</el-button>
      </div>
      <el-table v-loading="loading" :data="products" style="width: 100%">
        <el-table-column label="产品名称" prop="name" min-width="200" />
        <el-table-column label="所需积分" prop="points_required" width="120" />
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '已上架' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template slot-scope="scope">
            {{ new Date(scope.row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="$router.push(`/products/edit/${scope.row.id}`)">编辑</el-button>
            <el-button type="text" size="small" @click="handleToggleStatus(scope.row)">
              {{ scope.row.status === 'active' ? '下架' : '上架' }}
            </el-button>
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
  </div>
</template>

<script>
import { deleteProduct, toggleProductStatus } from '@/api/product'

export default {
  name: 'ProductList',
  data() {
    return {
      loading: false
    }
  },
  computed: {
    products() {
      return this.$store.state.product.products
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
    this.loadProducts()
  },
  methods: {
    async loadProducts(page = 1) {
      this.loading = true
      try {
        await this.$store.dispatch('product/getProducts', { page, page_size: this.pageSize })
      } catch (error) {
        console.error('Failed to load products:', error)
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.loadProducts(page)
    },
    async handleToggleStatus(product) {
      try {
        const newStatus = product.status === 'active' ? 'inactive' : 'active'
        await toggleProductStatus(product.id, newStatus)
        this.$message.success('操作成功')
        this.loadProducts(this.page)
      } catch (error) {
        console.error('Failed to toggle product status:', error)
      }
    },
    async handleDelete(product) {
      try {
        await this.$confirm('确定要删除该产品吗？', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deleteProduct(product.id)
        this.$message.success('删除成功')
        this.loadProducts(this.page)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete product:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
.product-list-container {
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
</style>
