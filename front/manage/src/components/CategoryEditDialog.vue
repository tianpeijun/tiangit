<template>
  <el-dialog :title="isEdit ? '编辑分类' : '创建分类'" :visible.sync="visible" width="500px" @close="handleClose">
    <el-form ref="form" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="分类名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="父分类">
        <el-select v-model="form.parent_id" placeholder="选择父分类（留空为一级分类）" clearable style="width: 100%">
          <el-option
            v-for="category in parentCategories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>
    </el-form>
    <div slot="footer">
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { createCategory, updateCategory } from '@/api/category'

export default {
  name: 'CategoryEditDialog',
  data() {
    return {
      visible: false,
      submitting: false,
      isEdit: false,
      categoryId: null,
      form: {
        name: '',
        parent_id: null,
        sort_order: 0
      },
      rules: {
        name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
      }
    }
  },
  computed: {
    parentCategories() {
      return this.$store.state.category.categories.filter(c => !c.parent_id)
    }
  },
  methods: {
    open(category = null) {
      if (category) {
        this.isEdit = true
        this.categoryId = category.id
        this.form = {
          name: category.name,
          parent_id: category.parent_id,
          sort_order: category.sort_order
        }
      } else {
        this.isEdit = false
        this.categoryId = null
        this.form = {
          name: '',
          parent_id: null,
          sort_order: 0
        }
      }
      this.visible = true
    },
    handleClose() {
      this.$refs.form.resetFields()
    },
    handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (!valid) return
        
        this.submitting = true
        try {
          if (this.isEdit) {
            await updateCategory(this.categoryId, this.form)
            this.$message.success('更新成功')
          } else {
            await createCategory(this.form)
            this.$message.success('创建成功')
          }
          this.visible = false
          this.$emit('success')
        } catch (error) {
          console.error('Failed to save category:', error)
        } finally {
          this.submitting = false
        }
      })
    }
  }
}
</script>
