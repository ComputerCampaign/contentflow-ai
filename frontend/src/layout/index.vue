<template>
  <div class="app-wrapper" :class="classObj">
    <!-- 移动端遮罩层 -->
    <div 
      v-if="device === 'mobile' && sidebar.opened" 
      class="drawer-bg" 
      @click="handleClickOutside"
    />
    
    <!-- 侧边栏 -->
    <Sidebar class="sidebar-container" />
    
    <!-- 主内容区域 -->
    <div class="main-container" :class="{ 'sidebar-collapsed': !sidebar.opened }">
      <!-- 顶部导航栏 -->
      <div :class="{ 'fixed-header': fixedHeader }">
        <Navbar />
      </div>
      
      <!-- 页面内容 -->
      <AppMain />
      
      <!-- 右侧设置面板 -->
      <!-- <RightPanel v-if="showSettings">
        <Settings />
      </RightPanel> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import Sidebar from './components/Sidebar/index.vue'
import Navbar from './components/Navbar.vue'
import AppMain from './components/AppMain.vue'
// import RightPanel from './components/RightPanel.vue' // 暂时移除
import Settings from './components/Settings/index.vue'

const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()

// 计算属性
const sidebar = computed(() => appStore.state.sidebar)
const device = computed(() => appStore.state.device)
const showSettings = computed(() => false) // 暂时禁用设置面板
const fixedHeader = computed(() => appStore.state.fixedHeader)

// 样式类
const classObj = computed(() => ({
  hideSidebar: !sidebar.value.opened,
  openSidebar: sidebar.value.opened,
  withoutAnimation: sidebar.value.withoutAnimation,
  mobile: device.value === 'mobile'
}))

// 处理移动端点击遮罩层关闭侧边栏
const handleClickOutside = () => {
  appStore.closeSidebar(false)
}

// 监听路由变化，移动端自动关闭侧边栏
watchEffect(() => {
  if (device.value === 'mobile' && sidebar.value.opened) {
    appStore.closeSidebar(false)
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/mixin' as *;
@use '@/styles/variables' as *;

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100vh;
  width: 100%;
  min-width: 1024px; // 设置最小宽度，小于此宽度时出现横向滚动条
  
  // 小屏幕时的处理
  @include mobile {
    min-width: 768px;
    overflow-x: auto; // 添加横向滚动条
  }
  
  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}

.drawer-bg {
  background: #000;
  opacity: 0.3;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: calc(100% - 210px);
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: calc(100% - 54px);
}

.mobile .fixed-header {
  width: 100%;
}

.main-container {
  margin-left: 210px;
  transition: margin-left 0.28s;
  min-height: 100vh;
  position: relative;
  
  &.sidebar-collapsed {
    margin-left: 54px;
  }
  
  @include mobile {
    margin-left: 0;
    
    &.sidebar-collapsed {
      margin-left: 0;
    }
  }
}

// 确保内容不被侧边栏遮挡
.sidebar-container {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1001;
  height: 100vh;
  transition: width 0.28s;
  
  @include mobile {
    z-index: 1002; // 移动端时提高层级
  }
}
</style>