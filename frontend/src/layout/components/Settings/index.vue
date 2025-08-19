<template>
  <div class="drawer-container">
    <div>
      <h3 class="drawer-title">页面风格设置</h3>
      
      <div class="drawer-item">
        <span>主题色</span>
        <theme-picker style="float: right; height: 26px; margin: -3px 8px 0 0;" />
      </div>
      
      <div class="drawer-item">
        <span>开启 Tags-View</span>
        <el-switch
          v-model="tagsView"
          class="drawer-switch"
        />
      </div>
      
      <div class="drawer-item">
        <span>固定 Header</span>
        <el-switch
          v-model="fixedHeader"
          class="drawer-switch"
        />
      </div>
      
      <div class="drawer-item">
        <span>侧边栏 Logo</span>
        <el-switch
          v-model="sidebarLogo"
          class="drawer-switch"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import ThemePicker from '../ThemePicker.vue'

const appStore = useAppStore()

// 计算属性
const tagsView = computed({
  get: () => appStore.state.tagsView,
  set: (val: boolean) => {
    appStore.changeSetting({ key: 'tagsView', value: val })
  }
})

const fixedHeader = computed({
  get: () => appStore.state.fixedHeader,
  set: (val: boolean) => {
    appStore.changeSetting({ key: 'fixedHeader', value: val })
  }
})

const sidebarLogo = computed({
  get: () => appStore.state.sidebarLogo,
  set: (val: boolean) => {
    appStore.changeSetting({ key: 'sidebarLogo', value: val })
  }
})
</script>

<style lang="scss" scoped>
.drawer-container {
  padding: 24px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;

  .drawer-title {
    margin-bottom: 12px;
    color: rgba(0, 0, 0, 0.85);
    font-size: 14px;
    line-height: 22px;
  }

  .drawer-item {
    color: rgba(0, 0, 0, 0.65);
    font-size: 14px;
    padding: 12px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .drawer-switch {
      float: right;
    }
  }
}
</style>