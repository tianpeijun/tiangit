<template>
  <el-select
    v-model="selectedUser"
    filterable
    remote
    placeholder="搜索用户"
    :remote-method="searchUsers"
    :loading="loading"
    style="width: 100%"
    @change="handleChange"
  >
    <el-option
      v-for="user in users"
      :key="user.id"
      :label="`${user.real_name} (${user.username})`"
      :value="user.id"
    />
  </el-select>
</template>

<script>
import { getUsers } from '@/api/user'

export default {
  name: 'UserSelector',
  props: {
    value: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      selectedUser: this.value,
      users: [],
      loading: false
    }
  },
  watch: {
    value(val) {
      this.selectedUser = val
    }
  },
  mounted() {
    this.searchUsers('')
  },
  methods: {
    async searchUsers(query) {
      this.loading = true
      try {
        const data = await getUsers({ keyword: query, page: 1, page_size: 20, role: 'employee' })
        this.users = data.items
      } catch (error) {
        console.error('Failed to search users:', error)
      } finally {
        this.loading = false
      }
    },
    handleChange(value) {
      this.$emit('input', value)
    }
  }
}
</script>
