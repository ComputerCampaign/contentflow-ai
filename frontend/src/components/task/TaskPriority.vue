<template>
  <el-tag
    :type="getTagType(priority)"
    size="small"
  >
    {{ getPriorityText(priority) }}
  </el-tag>
</template>

<script setup lang="ts">
interface Props {
  priority: string
}

defineProps<Props>()

const getTagType = (priority: string) => {
  const typeMap: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const textMap: Record<string, string> = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return textMap[priority] || priority
}
</script>