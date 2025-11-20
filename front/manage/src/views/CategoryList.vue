<template>
  <el-card>
    <div slot="header" class="card-header">
      <h3>分类管理</h3>
      <el-button type="primary" icon="el-icon-plus" @click="handleCreate">创建分类</el-button>
    </div>
    <el-table v-loading="loading" :data="categories" row-key="id" :tree-props="{children: 'children'}" style="width: 100%">
      <el-table-column label="分类名称" prop="name" min-width="200" />
      <el-table-column label="排序" prop="sort_order" width="100" />
      <el-table-column label="创建时间" width="180">
        <template slot-scope="scope">
          {{ new Date(scope.row.created_at).toLocaleString('zh-CN') }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="text" size="small" style="color: #F56C6C" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <category-edit-dialog ref="categoryEditDialog" @success="loadCategories" />
  </el-card>
</template>

<script>
import { deleteCategory } from '@/api/category'
import CategoryEditDialog from '@/components/CategoryEditDialog.vue'

export default {
  name: 'CategoryList',
  components: {
    CategoryEditDialog
  },
  data() {
    return {
      loading: false
    }
  },
  computed: {
    categories() {
      return this.$store.state.category.categories
    }
  },
  mounted() {
    this.loadCategories()
  },
  methods: {
    async loadCategories() {
      this.loading = true
      try {
        await this.$store.dispatch('category/getCategories')
      } catch (error) {
        console.error('Failed to load categories:', error)
      } finally {
        this.loading = false
      }
    },
    handleCreate() {
      this.$refs.categoryEditDialog.open()
    },
    handleEdit(category) {
      this.$refs.categoryEditDialog.open(category)
    },
    async handleDelete(category) {
      try {
        await this.$confirm('确定要删除该分类吗？', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deleteCategory(category.id)
        this.$message.success('删除成功')
        this.loadCategories()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete category:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}
</style>
