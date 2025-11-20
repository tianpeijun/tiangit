<template>
  <div class="address-container">
    <el-card>
      <div slot="header">
        <h3>收货地址管理</h3>
      </div>
      <el-form ref="addressForm" :model="addressForm" :rules="addressRules" label-width="100px">
        <el-form-item label="收货地址" prop="address">
          <el-input v-model="addressForm.address" type="textarea" :rows="4" placeholder="请输入详细收货地址" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="addressForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
          <el-button @click="loadAddress">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { getAddress, updateAddress } from '@/api/profile'

export default {
  name: 'Address',
  data() {
    return {
      addressForm: {
        address: '',
        phone: ''
      },
      addressRules: {
        address: [{ required: true, message: '请输入收货地址', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
      },
      submitting: false
    }
  },
  mounted() {
    this.loadAddress()
  },
  methods: {
    async loadAddress() {
      try {
        const data = await getAddress()
        if (data) {
          this.addressForm.address = data.address
          this.addressForm.phone = data.phone
        }
      } catch (error) {
        console.error('Failed to load address:', error)
      }
    },
    handleSave() {
      this.$refs.addressForm.validate(async valid => {
        if (!valid) return
        
        this.submitting = true
        try {
          await updateAddress(this.addressForm)
          this.$message.success('保存成功')
        } catch (error) {
          console.error('Failed to save address:', error)
        } finally {
          this.submitting = false
        }
      })
    }
  }
}
</script>

<style scoped>
.address-container {
  padding: 20px 0;
  max-width: 600px;
}
</style>
