<template>
  <el-card v-loading="loading">
    <div slot="header" class="card-header">
      <h3>{{ isEdit ? '编辑产品' : '创建产品' }}</h3>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    <el-form ref="form" :model="form" :rules="rules" label-width="120px" style="max-width: 800px">
      <el-form-item label="产品名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="产品描述">
        <el-input v-model="form.description" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item label="所需积分" prop="points_required">
        <el-input-number v-model="form.points_required" :min="1" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio label="active">上架</el-radio>
          <el-radio label="inactive">下架</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="产品分类">
        <el-select v-model="form.category_ids" multiple placeholder="请选择分类" style="width: 100%">
          <el-option
            v-for="category in flatCategories"
            :key="category.id"
            :label="category.label"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import { getProductDetail, createProduct, updateProduct } from '@/api/product'

export default {
  name: 'ProductEdit',
  data() {
    return {
      loading: false,
      submitting: false,
      isEdit: false,
      form: {
        name: '',
        description: '',
        points_required: 100,
        status: 'inactive',
        category_ids: []
      },
      rules: {
        name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
        points_required: [{ required: true, message: '请输入所需积分', trigger: 'blur' }],
        status: [{ required: true, message: '请选择状态', trigger: 'change' }]
      }
    }
  },
  computed: {
    categories() {
      return this.$store.state.category.categories
    },
    flatCategories() {
      const result = []
      const flatten = (items, prefix = '') => {
        items.forEach(item => {
          result.push({
            id: item.id,
            label: prefix + item.name
          })
          if (item.children && item.children.length > 0) {
            flatten(item.children, prefix + item.name + ' / ')
          }
        })
      }
      flatten(this.categories)
      return result
    }
  },
  mounted() {
    this.loadCategories()
    if (this.$route.params.id) {
      this.isEdit = true
      this.loadProduct()
    }
  },
  methods: {
    async loadCategories() {
      try {
        await this.$store.dispatch('category/getCategories')
      } catch (error) {
        console.error('Failed to load categories:', error)
      }
    },
    async loadProduct() {
      this.loading = true
      try {
        const data = await getProductDetail(this.$route.params.id)
        this.form = {
          name: data.name,
          description: data.description || '',
          points_required: data.points_required,
          status: data.status,
          category_ids: data.categories ? data.categories.map(c => c.id) : []
        }
      } catch (error) {
        console.error('Failed to load product:', error)
        this.$message.error('加载产品失败')
        this.$router.back()
      } finally {
        this.loading = false
      }
    },
    handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (!valid) return
        
        this.submitting = true
        try {
          if (this.isEdit) {
            await updateProduct(this.$route.params.id, this.form)
            this.$message.success('更新成功')
          } else {
            await createProduct(this.form)
            this.$message.success('创建成功')
          }
          this.$router.back()
        } catch (error) {
          console.error('Failed to save product:', error)
        } finally {
          this.submitting = false
        }
      })
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
