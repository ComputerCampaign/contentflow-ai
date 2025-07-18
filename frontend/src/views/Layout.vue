<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h3>爬虫系统</h3>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/">
          <el-icon><el-icon-menu /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-menu-item index="/crawler">
          <el-icon><el-icon-download /></el-icon>
          <span>爬虫任务</span>
        </el-menu-item>
        
        <el-menu-item index="/xpath">
          <el-icon><el-icon-document /></el-icon>
          <span>XPath规则</span>
        </el-menu-item>
        
        <el-menu-item v-if="isAdmin" index="/users">
          <el-icon><el-icon-user /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              {{ currentUser ? currentUser.username : '用户' }}
              <el-icon class="el-icon--right"><el-icon-arrow-down /></el-icon>
            </span>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'Layout',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 获取当前用户信息
    const currentUser = computed(() => store.getters['auth/currentUser'])
    const isAdmin = computed(() => store.getters['auth/isAdmin'])
    
    // 当前激活的菜单项
    const activeMenu = computed(() => route.path)
    
    // 页面标题
    const pageTitle = computed(() => {
      const matched = route.matched.find(item => item.meta && item.meta.title)
      return matched ? matched.meta.title : '仪表盘'
    })
    
    // 下拉菜单命令处理
    const handleCommand = async (command) => {
      if (command === 'logout') {
        await store.dispatch('auth/logout')
        router.push('/login')
      } else if (command === 'profile') {
        router.push('/profile')
      }
    }
    
    // 组件挂载时获取用户信息
    onMounted(async () => {
      if (!currentUser.value) {
        try {
          await store.dispatch('auth/getUserInfo')
        } catch (error) {
          console.error('获取用户信息失败', error)
        }
      }
    })
    
    return {
      currentUser,
      isAdmin,
      activeMenu,
      pageTitle,
      handleCommand
    }
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
}

.sidebar {
  background-color: #304156;
  color: #fff;
  height: 100%;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background-color: #263445;
}

.el-menu-vertical {
  border-right: none;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.user-dropdown {
  cursor: pointer;
  color: #409EFF;
  display: flex;
  align-items: center;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}
</style>