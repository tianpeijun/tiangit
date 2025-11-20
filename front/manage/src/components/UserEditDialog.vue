<template>
  <el-dialog title="编辑用户" :visible.sync="visible" width="500px" @close="handleClose">
    <el-form ref="form" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="姓名" prop="real_name">
        <el-input v-model="form.real_name" />
      </el-form-item>
      <el-form-item label="工号" prop="employee_id">
        <el-input v-model="form.employee_id" />
      </el-form-item>
      <el-form-item label="部门" prop="department">
        <el-input v-model="form.department" />
      </el-form-item>
      <el-form-item label="职位">
        <el-input v-model="form.position" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="form.is_active" />
      </el-form-item>
    </el-form>
    <div slot="footer">
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { updateUser } from '@/api/user'

export default {
  name: 'UserEditDialog',
  data() {
    return {
      visible: false,
      submitting: false,
      userId: null,
      form: {
        real_name: '',
        employee_id: '',
        department: '',
        position: '',
        is_active: true
      },
      rules: {
        real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
        department: [{ required: true, message: '请输入部门', trigger: 'blur' }]
      }
    }
  },
  methods: {
    open(user) {
      this.userId = user.id
      this.form = {
        real_name: user.real_name,
        employee_id: user.employee_id,
        department: user.department,
        position: user.position || '',
        is_active: user.is_active
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
          await updateUser(this.userId, this.form)
          this.$message.success('更新成功')
          this.visible = false
          this.$emit('success')
        } catch (error) {
          console.error('Failed to update user:', error)
        } finally {
          this.submitting = false
        }
      })
    }
  }
}
</script>
