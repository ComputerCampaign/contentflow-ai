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
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div :class="{ 'fixed-header': fixedHeader }">
        <Navbar />
        <!-- 标签页导航 -->
        <TagsView v-if="needTagsView" />
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
import TagsView from './components/TagsView/index.vue'
// import RightPanel from './components/RightPanel.vue' // 暂时移除
import Settings from './components/Settings/index.vue'

const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()

// 计算属性
const sidebar = computed(() => appStore.state.sidebar)
const device = computed(() => appStore.state.device)
const showSettings = computed(() => false) // 暂时禁用设置面板
const needTagsView = computed(() => appStore.state.tagsView)
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
@import '@/styles/mixin.scss';
@import '@/styles/variables.scss';

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100vh;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  
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
  width: calc(100% - #{$sideBarWidth});
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: calc(100% - 54px);
}

.mobile .fixed-header {
  width: 100%;
}
</style>