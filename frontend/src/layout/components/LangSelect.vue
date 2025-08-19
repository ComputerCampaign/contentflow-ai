<template>
  <el-dropdown trigger="click" class="international" @command="handleSetLanguage">
    <div>
      <el-icon :size="20">
        <Operation />
      </el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item :disabled="language === 'zh-cn'" command="zh-cn">
          中文
        </el-dropdown-item>
        <el-dropdown-item :disabled="language === 'en'" command="en">
          English
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Operation } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 当前语言
const language = computed(() => appStore.state.language)

// 切换语言
const handleSetLanguage = (lang: string) => {
  appStore.setLanguage(lang)
  // 这里可以添加国际化逻辑
  // 例如：i18n.global.locale = lang
}
</script>

<style scoped>
.international {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>