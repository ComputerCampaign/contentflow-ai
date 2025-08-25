<template>
  <div :class="{ 'has-logo': showLogo }">
    <SidebarLogo v-if="showLogo" :collapse="isCollapse" />
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :background-color="variables.menuBg"
        :text-color="variables.menuText"
        :unique-opened="false"
        :active-text-color="variables.menuActiveText"
        :collapse-transition="false"
        mode="vertical"
      >
        <SidebarItem
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import SidebarItem from './SidebarItem.vue'
import SidebarLogo from './SidebarLogo.vue'
// 使用现代化的颜色方案
const variables = {
  menuBg: '#ffffff',
  menuText: '#606266',
  menuActiveText: '#409eff',
  menuHover: '#f5f7fa',
  menuActiveBg: '#ecf5ff',
  borderColor: '#e4e7ed'
}

const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()

// 计算属性
const sidebar = computed(() => appStore.state.sidebar)
const routes = computed(() => {
  // 根据用户权限过滤路由
  return filterRoutes(appStore.state.routes)
})
const showLogo = computed(() => appStore.state.sidebarLogo)
const isCollapse = computed(() => !sidebar.value.opened)
const activeMenu = computed(() => {
  const { meta, path } = route
  // 如果设置了activeMenu，则使用activeMenu
  if (meta?.activeMenu) {
    return meta.activeMenu
  }
  return path
})

// 根据权限过滤路由
const filterRoutes = (routes: any[]) => {
  const res: any[] = []
  
  routes.forEach(route => {
    const tmp = { ...route }
    
    // 检查路由权限
    if (hasPermission(tmp)) {
      if (tmp.children) {
        tmp.children = filterRoutes(tmp.children)
      }
      res.push(tmp)
    }
  })
  
  return res
}

// 检查权限
const hasPermission = (route: any) => {
  const { meta } = route
  if (!meta) return true
  
  // 检查是否隐藏 - 隐藏的路由不在侧边栏显示
  if (meta.hidden) {
    return false
  }
  
  // 检查是否需要认证
  if (meta.requiresAuth && !userStore.isAuthenticated) {
    return false
  }
  
  // 如果用户未登录，只显示不需要权限的路由
  if (!userStore.isAuthenticated) {
    return !meta.permissions && !meta.roles
  }
  
  // 获取用户权限和角色
  const userPermissions = userStore.permissions || []
  const userRoles = userStore.roles || []
  
  // admin用户可以访问所有页面
  if (userRoles.includes('admin') || userPermissions.includes('admin:*') || userPermissions.includes('*')) {
    return true
  }
  
  // 检查权限要求
  if (meta.permissions && meta.permissions.length > 0) {
    // 特殊处理：只有系统设置需要admin权限，其他页面普通用户都可以访问
    if (meta.permissions.includes('admin')) {
      // 只有系统设置模块需要admin权限
      return userRoles.includes('admin')
    }
    
    // 其他权限检查（如user:manage等）
    return meta.permissions.some((permission: string) => {
      // 支持通配符权限，如 task:* 可以匹配 task:view, task:create 等
      if (permission.includes('*')) {
        const prefix = permission.replace('*', '')
        return userPermissions.some(userPerm => userPerm.startsWith(prefix))
      }
      return userPermissions.includes(permission)
    })
  }
  
  // 检查角色要求
  if (meta.roles && meta.roles.length > 0) {
    return meta.roles.some((role: string) => userRoles.includes(role as any))
  }
  
  // 默认情况下，已登录用户可以访问没有特殊权限要求的页面
  return true
}
</script>

<style lang="scss">
@use '@/styles/variables' as *;

.sidebar-container {
  transition: width 0.28s;
  width: 220px !important;
  background-color: #ffffff;
  height: 100%;
  position: fixed;
  font-size: 0px;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  overflow: hidden;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);

  // reset element-ui css
  .horizontal-collapse-transition {
    transition: 0s width ease-in-out, 0s padding-left ease-in-out, 0s padding-right ease-in-out;
  }

  .scrollbar-wrapper {
    overflow-x: hidden !important;
  }

  .el-scrollbar__bar.is-vertical {
    right: 0px;
  }

  .el-scrollbar {
    height: 100%;
  }

  &.has-logo {
    .el-scrollbar {
      height: calc(100% - 50px);
    }
  }

  .is-horizontal {
    display: none;
  }

  a {
    display: inline-block;
    width: 100%;
    overflow: hidden;
  }

  .svg-icon {
    margin-right: 16px;
  }

  .sub-el-icon {
    margin-right: 12px;
    margin-left: -2px;
  }

  .el-menu {
    border: none;
    height: 100%;
    width: 100% !important;
  }

  // 菜单项样式优化
  .el-menu-item {
    margin: 4px 12px;
    border-radius: 8px;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: #f5f7fa !important;
      color: #409eff !important;
    }
    
    &.is-active {
      background-color: #ecf5ff !important;
      color: #409eff !important;
      font-weight: 500;
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 20px;
        background-color: #409eff;
        border-radius: 0 2px 2px 0;
      }
    }
  }
  
  .el-submenu {
    margin: 4px 12px;
    
    .el-submenu__title {
      border-radius: 8px;
      transition: all 0.3s ease;
      
      &:hover {
        background-color: #f5f7fa !important;
        color: #409eff !important;
      }
    }
    
    &.is-active > .el-submenu__title {
      background-color: #ecf5ff !important;
      color: #409eff !important;
      font-weight: 500;
    }
  }
  
  // 子菜单样式
  .nest-menu {
    .el-menu-item {
      margin: 2px 8px 2px 24px;
      padding-left: 32px !important;
      min-height: 44px !important;
      
      &:hover {
        background-color: #f0f9ff !important;
      }
      
      &.is-active {
        background-color: #e1f5fe !important;
        
        &::before {
          left: 8px;
        }
      }
    }
  }
}

.hideSidebar {
  .sidebar-container {
    width: 64px !important;
  }

  .main-container {
    margin-left: 64px;
  }

  .submenu-title-noDropdown {
    padding: 0 !important;
    position: relative;

    .el-tooltip {
      padding: 0 !important;

      .svg-icon {
        margin-left: 20px;
      }

      .sub-el-icon {
        margin-left: 19px;
      }
    }
  }

  .el-submenu {
    overflow: hidden;

    & > .el-submenu__title {
      padding: 0 !important;

      .svg-icon {
        margin-left: 20px;
      }

      .sub-el-icon {
        margin-left: 19px;
      }

      .el-submenu__icon-arrow {
        display: none;
      }
    }
  }

  .el-menu--collapse {
    .el-submenu {
      & > .el-submenu__title {
        & > span {
          height: 0;
          width: 0;
          overflow: hidden;
          visibility: hidden;
          display: inline-block;
        }
      }
    }
  }
}

.el-menu--collapse .el-menu .el-submenu {
  min-width: 220px !important;
}

// mobile responsive
.mobile {
  .main-container {
    margin-left: 0px;
  }

  .sidebar-container {
    transition: transform 0.28s;
    width: 220px !important;
  }

  &.hideSidebar {
    .sidebar-container {
      pointer-events: none;
      transition-duration: 0.3s;
      transform: translate3d(-220px, 0, 0);
    }
  }
}

.withoutAnimation {
  .main-container,
  .sidebar-container {
    transition: none;
  }
}
</style>