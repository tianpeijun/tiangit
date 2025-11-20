<template>
  <el-row :gutter="20">
    <el-col :span="12">
      <el-card>
        <div slot="header">
          <h3>单个发放积分</h3>
        </div>
        <el-form ref="singleForm" :model="singleForm" :rules="singleRules" label-width="100px">
          <el-form-item label="选择用户" prop="user_id">
            <user-selector v-model="singleForm.user_id" />
          </el-form-item>
          <el-form-item label="积分数量" prop="amount">
            <el-input-number v-model="singleForm.amount" :min="1" />
          </el-form-item>
          <el-form-item label="发放说明">
            <el-input v-model="singleForm.description" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="singleSubmitting" @click="handleSingleGrant">发放</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card>
        <div slot="header">
          <h3>批量发放积分</h3>
        </div>
        <el-form ref="batchForm" :model="batchForm" :rules="batchRules" label-width="100px">
          <el-form-item label="积分数量" prop="amount">
            <el-input-number v-model="batchForm.amount" :min="1" />
          </el-form-item>
          <el-form-item label="发放说明">
            <el-input v-model="batchForm.description" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="batchSubmitting" @click="handleBatchGrant">批量发放给所有员工</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script>
import { grantPoints, grantPointsBatch } from '@/api/point'
import UserSelector from '@/components/UserSelector.vue'

export default {
  name: 'PointGrant',
  components: {
    UserSelector
  },
  data() {
    return {
      singleForm: {
        user_id: null,
        amount: 100,
        description: ''
      },
      singleRules: {
        user_id: [{ required: true, message: '请选择用户', trigger: 'change' }],
        amount: [{ required: true, message: '请输入积分数量', trigger: 'blur' }]
      },
      singleSubmitting: false,
      batchForm: {
        amount: 100,
        description: ''
      },
      batchRules: {
        amount: [{ required: true, message: '请输入积分数量', trigger: 'blur' }]
      },
      batchSubmitting: false
    }
  },
  methods: {
    handleSingleGrant() {
      this.$refs.singleForm.validate(async valid => {
        if (!valid) return
        
        this.singleSubmitting = true
        try {
          // 转换为后端期望的格式
          const data = {
            user_ids: [this.singleForm.user_id],
            amount: this.singleForm.amount,
            description: this.singleForm.description
          }
          await grantPoints(data)
          this.$message.success('发放成功')
          this.$refs.singleForm.resetFields()
        } catch (error) {
          console.error('Failed to grant points:', error)
          this.$message.error('发放失败，请重试')
        } finally {
          this.singleSubmitting = false
        }
      })
    },
    handleBatchGrant() {
      this.$refs.batchForm.validate(async valid => {
        if (!valid) return
        
        try {
          await this.$confirm('确定要给所有员工发放积分吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          })
          
          this.batchSubmitting = true
          const result = await grantPointsBatch(this.batchForm)
          this.$message.success(`发放成功，共 ${result.count} 名员工`)
          this.$refs.batchForm.resetFields()
        } catch (error) {
          if (error !== 'cancel') {
            console.error('Failed to grant points batch:', error)
          }
        } finally {
          this.batchSubmitting = false
        }
      })
    }
  }
}
</script>
