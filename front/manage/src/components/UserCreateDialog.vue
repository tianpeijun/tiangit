<template>
  <el-dialog title="创建用户" :visible.sync="visible" width="500px" @close="handleClose">
    <el-form ref="form" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
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
      <el-form-item label="角色" prop="role">
        <el-select v-model="form.role" style="width: 100%">
          <el-option label="员工" value="employee" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
    </el-form>
    <div slot="footer">
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { createUser } from '@/api/user'

export default {
  name: 'UserCreateDialog',
  data() {
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6 || value.length > 8) {
        callback(new Error('密码长度必须为6-8位'))
      } else if (!/\d/.test(value) || !/[a-zA-Z]/.test(value)) {
        callback(new Error('密码必须包含数字和字母'))
      } else {
        callback()
      }
    }
    return {
      visible: false,
      submitting: false,
      form: {
        username: '',
        password: '',
        real_name: '',
        employee_id: '',
        department: '',
        position: '',
        role: 'employee'
      },
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ],
        real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
        department: [{ required: true, message: '请输入部门', trigger: 'blur' }],
        role: [{ required: true, message: '请选择角色', trigger: 'change' }]
      }
    }
  },
  methods: {
    open() {
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
          await createUser(this.form)
          this.$message.success('创建成功')
          this.visible = false
          this.$emit('success')
        } catch (error) {
          console.error('Failed to create user:', error)
        } finally {
          this.submitting = false
        }
      })
    }
  }
}
</script>
