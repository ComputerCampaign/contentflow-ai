<template>
  <el-tag
    :type="getTagType(status)"
    size="small"
  >
    {{ getStatusText(status) }}
  </el-tag>
</template>

<script setup lang="ts">
interface Props {
  status: string
}

defineProps<Props>()

const getTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning',
    paused: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
    paused: '已暂停'
  }
  return textMap[status] || status
}
</script>