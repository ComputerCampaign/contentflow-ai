<template>
  <div @click="click">
    <el-icon :size="20">
      <FullScreen v-if="!isFullscreen" />
      <Aim v-else />
    </el-icon>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { FullScreen, Aim } from '@element-plus/icons-vue'
import screenfull from 'screenfull'

const isFullscreen = ref(false)

// 点击切换全屏
const click = () => {
  if (!screenfull.isEnabled) {
    ElMessage.warning('您的浏览器不支持全屏功能')
    return
  }
  screenfull.toggle()
}

// 监听全屏状态变化
const change = () => {
  isFullscreen.value = screenfull.isFullscreen
}

// 初始化
const init = () => {
  if (screenfull.isEnabled) {
    screenfull.on('change', change)
  }
}

// 销毁
const destroy = () => {
  if (screenfull.isEnabled) {
    screenfull.off('change', change)
  }
}

onMounted(() => {
  init()
})

onUnmounted(() => {
  destroy()
})
</script>

<style scoped>
/* 可以添加一些样式 */
</style>