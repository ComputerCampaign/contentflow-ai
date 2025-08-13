<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <i class="fas fa-chart-line"></i>
        </div>
        <transition name="fade">
          <div v-show="!sidebarCollapsed" class="sidebar-title">
            内容平台
          </div>
        </transition>
      </div>
      
      <nav class="nav-menu">
        <div
          v-for="item in menuItems"
          :key="item.name"
          class="nav-item"
        >
          <router-link
            :to="item.path"
            class="nav-link"
            :class="{ active: $route.name === item.name }"
          >
            <i :class="`fas fa-${item.icon} nav-icon`"></i>
            <transition name="fade">
              <span v-show="!sidebarCollapsed" class="nav-text">
                {{ item.title }}
              </span>
            </transition>
          </router-link>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <div class="user-avatar">
            <img v-if="userStore.userInfo.avatar" :src="userStore.userInfo.avatar" alt="头像">
            <i v-else class="fas fa-user"></i>
          </div>
          <transition name="fade">
            <div v-show="!sidebarCollapsed" class="user-details">
              <div class="user-name">{{ userStore.userInfo.username || '用户' }}</div>
              <div class="user-role">{{ userStore.userInfo.role || '管理员' }}</div>
            </div>
          </transition>
        </div>
        
        <!-- 用户菜单 -->
        <transition name="slide-up">
          <div v-show="showUserMenu" class="user-menu">
            <div class="menu-item" @click="handleProfile">
              <i class="fas fa-user-edit"></i>
              <span>个人设置</span>
            </div>
            <div class="menu-item" @click="handleLogout">
              <i class="fas fa-sign-out-alt"></i>
              <span>退出登录</span>
            </div>
          </div>
        </transition>
      </div>
    </aside>
    
    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <header class="header">
        <div class="header-left">
          <el-button
            type="text"
            class="sidebar-toggle"
            @click="toggleSidebar"
          >
            <i class="fas fa-bars"></i>
          </el-button>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item
              v-for="item in breadcrumbItems"
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 通知 -->
          <el-badge :value="notificationCount" class="notification-badge">
            <el-button type="text" class="header-btn" @click="showNotifications">
              <i class="fas fa-bell"></i>
            </el-button>
          </el-badge>
          
          <!-- 全屏切换 -->
          <el-button type="text" class="header-btn" @click="toggleFullscreen">
            <i :class="isFullscreen ? 'fas fa-compress' : 'fas fa-expand'"></i>
          </el-button>
          
          <!-- 主题切换 -->
          <el-button type="text" class="header-btn" @click="toggleTheme">
            <i :class="isDarkTheme ? 'fas fa-sun' : 'fas fa-moon'"></i>
          </el-button>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    
    <!-- 通知抽屉 -->
    <el-drawer
      v-model="notificationDrawer"
      title="通知中心"
      direction="rtl"
      size="350px"
    >
      <div class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.read }"
        >
          <div class="notification-icon">
            <i :class="getNotificationIcon(notification.type)"></i>
          </div>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ formatTime(notification.time) }}</div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const sidebarCollapsed = ref(false)
const showUserMenu = ref(false)
const notificationDrawer = ref(false)
const isFullscreen = ref(false)
const isDarkTheme = ref(false)
const notificationCount = ref(3)

// 菜单项配置
const menuItems = [
  { name: 'Dashboard', path: '/dashboard', title: '仪表板', icon: 'tachometer-alt' },
  { name: 'Tasks', path: '/tasks', title: '任务管理', icon: 'tasks' },
  { name: 'Crawler', path: '/crawler', title: '爬虫配置', icon: 'spider' },
  { name: 'XPath', path: '/xpath', title: 'XPath配置', icon: 'code' },
  { name: 'Monitoring', path: '/monitoring', title: '系统监控', icon: 'chart-bar' },
  { name: 'Settings', path: '/settings', title: '系统设置', icon: 'cog' }
]

// 模拟通知数据
const notifications = ref([
  {
    id: 1,
    type: 'success',
    title: '任务完成',
    message: '爬虫任务 "技术博客采集" 已成功完成',
    time: new Date(),
    read: false
  },
  {
    id: 2,
    type: 'warning',
    title: '系统警告',
    message: '存储空间使用率已达到 85%',
    time: new Date(Date.now() - 3600000),
    read: false
  },
  {
    id: 3,
    type: 'info',
    title: '新功能上线',
    message: '系统功能已更新',
    time: new Date(Date.now() - 7200000),
    read: true
  }
])

// 计算属性
const breadcrumbItems = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title
  }))
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
}

const handleProfile = () => {
  showUserMenu.value = false
  router.push('/settings')
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await userStore.logout()
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}

const showNotifications = () => {
  notificationDrawer.value = true
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value
  document.documentElement.classList.toggle('dark', isDarkTheme.value)
  localStorage.setItem('darkTheme', isDarkTheme.value)
}

const getNotificationIcon = (type) => {
  const icons = {
    success: 'fas fa-check-circle text-success',
    warning: 'fas fa-exclamation-triangle text-warning',
    error: 'fas fa-times-circle text-danger',
    info: 'fas fa-info-circle text-info'
  }
  return icons[type] || icons.info
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 全屏状态监听
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

// 点击外部关闭用户菜单
const handleClickOutside = (event) => {
  if (!event.target.closest('.user-info') && !event.target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

// 生命周期
onMounted(() => {
  // 恢复侧边栏状态
  const savedCollapsed = localStorage.getItem('sidebarCollapsed')
  if (savedCollapsed !== null) {
    sidebarCollapsed.value = JSON.parse(savedCollapsed)
  }
  
  // 恢复主题设置
  const savedTheme = localStorage.getItem('darkTheme')
  if (savedTheme !== null) {
    isDarkTheme.value = JSON.parse(savedTheme)
    document.documentElement.classList.toggle('dark', isDarkTheme.value)
  }
  
  // 添加事件监听
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="scss" scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-secondary);
}

// 侧边栏样式
.sidebar {
  width: 260px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  z-index: 100;
  
  &.collapsed {
    width: 70px;
  }
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-light);
  
  .sidebar-logo {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
    
    i {
      color: white;
      font-size: 16px;
    }
  }
  
  .sidebar-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.nav-menu {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  margin-bottom: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: var(--text-regular);
  text-decoration: none;
  transition: all 0.3s ease;
  border-radius: 0 25px 25px 0;
  margin-right: 20px;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    color: var(--primary-color);
  }
  
  &.active {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    
    .nav-icon {
      color: white;
    }
  }
  
  .nav-icon {
    width: 20px;
    font-size: 16px;
    margin-right: 12px;
    text-align: center;
  }
  
  .nav-text {
    font-weight: 500;
  }
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--border-light);
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.3s ease;
  
  &:hover {
    background: var(--bg-tertiary);
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--primary-color);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
    overflow: hidden;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    i {
      color: white;
      font-size: 16px;
    }
  }
  
  .user-details {
    .user-name {
      font-weight: 500;
      color: var(--text-primary);
      font-size: 14px;
    }
    
    .user-role {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

.user-menu {
  position: absolute;
  bottom: 100%;
  left: 20px;
  right: 20px;
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  box-shadow: var(--shadow-base);
  overflow: hidden;
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.3s ease;
    
    &:hover {
      background: var(--bg-tertiary);
    }
    
    i {
      margin-right: 8px;
      width: 16px;
      text-align: center;
    }
  }
}

// 主容器样式
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 99;
}

.header-left {
  display: flex;
  align-items: center;
  
  .sidebar-toggle {
    margin-right: 16px;
    
    i {
      font-size: 16px;
    }
  }
  
  .breadcrumb {
    font-size: 14px;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .header-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    i {
      font-size: 16px;
    }
  }
  
  .notification-badge {
    :deep(.el-badge__content) {
      background: var(--danger-color);
      border: none;
    }
  }
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-secondary);
}

// 通知列表样式
.notification-list {
  .notification-item {
    display: flex;
    padding: 16px;
    border-bottom: 1px solid var(--border-light);
    transition: background 0.3s ease;
    
    &:hover {
      background: var(--bg-tertiary);
    }
    
    &.unread {
      background: rgba(102, 126, 234, 0.05);
      border-left: 3px solid var(--primary-color);
    }
    
    .notification-icon {
      margin-right: 12px;
      
      i {
        font-size: 20px;
      }
    }
    
    .notification-content {
      flex: 1;
      
      .notification-title {
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .notification-message {
        color: var(--text-regular);
        font-size: 13px;
        line-height: 1.4;
        margin-bottom: 8px;
      }
      
      .notification-time {
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

// 响应式设计
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    
    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .header-left {
    .breadcrumb {
      display: none;
    }
  }
}
</style>