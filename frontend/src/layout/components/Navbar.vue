<template>
  <div class="navbar">
    <div class="left-section">
      <hamburger
        id="hamburger-container"
        :is-active="sidebar.opened"
        class="hamburger-container"
        @toggleClick="toggleSideBar"
      />
      <breadcrumb id="breadcrumb-container" class="breadcrumb-container" />
    </div>

    <!-- 中间区域 - 日期时间显示 -->
    <div class="center-section">
      <div class="datetime-display">
        <div class="date-info">
          <el-icon class="date-icon"><Calendar /></el-icon>
          <span class="date-text">{{ currentDate }}</span>
        </div>
        <div class="time-info">
          <el-icon class="time-icon"><Clock /></el-icon>
          <span class="time-text">{{ currentTime }}</span>
        </div>
      </div>
    </div>

    <div class="right-menu">
      <template v-if="device !== 'mobile'">
        <!-- 全屏切换 -->
        <div class="menu-item-wrapper">
          <screenfull id="screenfull" class="right-menu-item hover-effect" />
          <span class="menu-label">全屏</span>
        </div>
        
        <!-- 消息通知 -->
        <div class="menu-item-wrapper">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="right-menu-item hover-effect">
            <el-icon :size="18">
              <Bell />
            </el-icon>
          </el-badge>
          <span class="menu-label">消息</span>
        </div>
      </template>

      <!-- 用户头像下拉菜单 -->
      <el-dropdown class="avatar-container right-menu-item hover-effect" trigger="click">
        <div class="avatar-wrapper">
          <img :src="avatar" class="user-avatar" />
          <div class="user-info">
            <span class="username">{{ username }}</span>
            <el-icon class="dropdown-icon">
              <CaretBottom />
            </el-icon>
          </div>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <router-link to="/profile/index">
              <el-dropdown-item>
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
            </router-link>
            <router-link to="/profile/settings">
              <el-dropdown-item>
                <el-icon><Setting /></el-icon>
                账户设置
              </el-dropdown-item>
            </router-link>
            <el-dropdown-item divided @click="logout">
              <el-icon><SwitchButton /></el-icon>
              <span style="display: block">退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Bell, 
  CaretBottom, 
  Calendar, 
  Clock, 
  User, 
  Setting, 
  SwitchButton 
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import Breadcrumb from './Breadcrumb.vue'
import Hamburger from './Hamburger.vue'
import Screenfull from './Screenfull.vue'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 计算属性
const sidebar = computed(() => appStore.state.sidebar)
const device = computed(() => appStore.state.device)
const avatar = computed(() => userStore.$state.userInfo?.avatar || '/logo.svg')
const username = computed(() => userStore.$state.userInfo?.nickname || '用户')
const unreadCount = computed(() => {
  // 这里可以从store中获取未读消息数量
  return 0
})

// 日期时间相关
const currentDate = ref('')
const currentTime = ref('')
let timer: number | null = null

const updateDateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const weekday = weekdays[now.getDay()]
  
  currentDate.value = `${year}年${month}月${day}日 ${weekday}`
  
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  currentTime.value = `${hours}:${minutes}:${seconds}`
}

// 切换侧边栏
const toggleSideBar = () => {
  appStore.toggleSidebar()
}

// 退出登录
const logout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await userStore.logout()
    router.push('/login')
    ElMessage.success('退出登录成功')
  } catch (error) {
    // 用户取消操作
  }
}

onMounted(() => {
  updateDateTime()
  timer = setInterval(updateDateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style lang="scss" scoped>
.navbar {
  height: 60px;
  overflow: hidden;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(0, 21, 41, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  .left-section {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
  }

  .hamburger-container {
    line-height: 56px;
    height: 100%;
    cursor: pointer;
    transition: all 0.3s ease;
    -webkit-tap-highlight-color: transparent;
    border-radius: 6px;
    padding: 0 8px;

    &:hover {
      background: rgba(255, 255, 255, 0.1);
      transform: scale(1.05);
    }
  }

  .breadcrumb-container {
    margin-left: 16px;
    
    :deep(.el-breadcrumb__inner) {
      color: rgba(255, 255, 255, 0.9) !important;
      font-weight: 500;
    }
    
    :deep(.el-breadcrumb__separator) {
      color: rgba(255, 255, 255, 0.6) !important;
    }
  }

  .center-section {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .datetime-display {
    display: flex;
    align-items: center;
    gap: 24px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 8px 16px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    .date-info,
    .time-info {
      display: flex;
      align-items: center;
      gap: 6px;
      color: rgba(255, 255, 255, 0.95);
      font-size: 14px;
      font-weight: 500;

      .date-icon,
      .time-icon {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.8);
      }
    }

    .date-text {
      font-weight: 600;
    }

    .time-text {
      font-family: 'Monaco', 'Consolas', monospace;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
  }

  .errLog-container {
    display: inline-block;
    vertical-align: top;
  }

  .right-menu {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 0 0 auto;

    &:focus {
      outline: none;
    }

    .menu-item-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      padding: 8px 12px;
      border-radius: 8px;
      transition: all 0.3s ease;
      cursor: pointer;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-1px);
      }

      .menu-label {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
        white-space: nowrap;
      }
    }

    .right-menu-item {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      color: rgba(255, 255, 255, 0.9);
      cursor: pointer;
      transition: all 0.3s ease;

      &.hover-effect {
        &:hover {
          color: rgba(255, 255, 255, 1);
          transform: scale(1.1);
        }
      }
    }

    .avatar-container {
      margin-left: 16px;
      padding: 4px 12px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      transition: all 0.3s ease;
      cursor: pointer;

      &:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .avatar-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;

        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          object-fit: cover;
          border: 2px solid rgba(255, 255, 255, 0.3);
          transition: all 0.3s ease;

          &:hover {
            border-color: rgba(255, 255, 255, 0.6);
          }
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 6px;

          .username {
            color: rgba(255, 255, 255, 0.95);
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
          }

          .dropdown-icon {
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            transition: all 0.3s ease;
          }
        }
      }

      &:hover .dropdown-icon {
        color: rgba(255, 255, 255, 1);
        transform: rotate(180deg);
      }
    }
  }
}

// 下拉菜单样式美化
:deep(.el-dropdown-menu) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  margin-top: 8px;

  .el-dropdown-menu__item {
    padding: 12px 20px;
    font-size: 14px;
    color: #333;
    transition: all 0.3s ease;
    border-radius: 8px;
    margin: 2px 8px;
    display: flex;
    align-items: center;
    gap: 8px;

    &:hover {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      transform: translateX(4px);
    }

    .el-icon {
      font-size: 16px;
    }
  }

  .el-dropdown-menu__item--divided {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    margin-top: 8px;
    padding-top: 12px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .navbar {
    padding: 0 12px;
    height: 56px;

    .center-section {
      display: none;
    }

    .datetime-display {
      display: none;
    }

    .menu-item-wrapper {
      .menu-label {
        display: none;
      }
    }

    .avatar-container {
      .user-info {
        .username {
          display: none;
        }
      }
    }
  }
}
</style>