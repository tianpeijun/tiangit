<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header">
            <h3>个人信息</h3>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ userInfo.real_name }}</el-descriptions-item>
            <el-descriptions-item label="工号">{{ userInfo.employee_id }}</el-descriptions-item>
            <el-descriptions-item label="部门">{{ userInfo.department }}</el-descriptions-item>
            <el-descriptions-item label="职位">{{ userInfo.position || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="积分余额">
              <span class="points-text">{{ userInfo.points }} 积分</span>
            </el-descriptions-item>
            <el-descriptions-item label="账户状态">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                {{ userInfo.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ formatDate(userInfo.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="最后登录">{{ formatDate(userInfo.last_login_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header">
            <h3>修改密码</h3>
          </div>
          <el-form ref="passwordForm" :model="passwordForm" :rules="passwordRules" label-width="100px">
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="handleChangePassword">修改密码</el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { changePassword } from '@/api/auth'

export default {
  name: 'Profile',
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
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.new_password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    return {
      passwordForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      passwordRules: {
        old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
        new_password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请确认新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      submitting: false
    }
  },
  computed: {
    userInfo() {
      return this.$store.state.user.userInfo || {}
    }
  },
  methods: {
    handleChangePassword() {
      this.$refs.passwordForm.validate(async valid => {
        if (!valid) return
        
        this.submitting = true
        try {
          await changePassword({
            old_password: this.passwordForm.old_password,
            new_password: this.passwordForm.new_password
          })
          this.$message.success('密码修改成功')
          this.resetPasswordForm()
        } catch (error) {
          console.error('Failed to change password:', error)
        } finally {
          this.submitting = false
        }
      })
    },
    resetPasswordForm() {
      this.$refs.passwordForm.resetFields()
    },
    formatDate(dateString) {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px 0;
}

.points-text {
  color: #67C23A;
  font-weight: bold;
  font-size: 18px;
}
</style>
