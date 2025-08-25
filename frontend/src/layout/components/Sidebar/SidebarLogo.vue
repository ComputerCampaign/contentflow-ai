<template>
  <div class="sidebar-logo-container" :class="{ collapse: collapse }">
    <transition name="sidebarLogoFade">
      <router-link
        v-if="collapse"
        key="collapse"
        class="sidebar-logo-link"
        to="/"
      >
        <img v-if="logo" :src="logo" class="sidebar-logo" />
        <h1 v-else class="sidebar-title">{{ title }}</h1>
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <img v-if="logo" :src="logo" class="sidebar-logo" />
        <h1 class="sidebar-title">{{ title }}</h1>
      </router-link>
    </transition>
  </div>
</template>

<script setup lang="ts">
interface Props {
  collapse: boolean
}

withDefaults(defineProps<Props>(), {
  collapse: false
})

// 可以从配置文件或环境变量中获取
const title = 'ContentFlow AI'
const logo = '/logo.svg' // 可以放在public目录下
</script>

<style lang="scss" scoped>
.sidebarLogoFade-enter-active {
  transition: opacity 1.5s;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 60px;
  line-height: 60px;
  background: #ffffff;
  text-align: center;
  overflow: hidden;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

  & .sidebar-logo-link {
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;

    & .sidebar-logo {
      width: 36px;
      height: 36px;
      vertical-align: middle;
      margin-right: 12px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
    }

    & .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #303133;
      font-weight: 600;
      line-height: 60px;
      font-size: 16px;
      font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
      vertical-align: middle;
      background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  &.collapse {
    .sidebar-logo {
      margin-right: 0px;
    }

    .sidebar-title {
      display: none;
    }
  }
}
</style>