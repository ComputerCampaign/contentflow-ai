<template>
  <div class="system-settings-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统设置</h1>
        <p class="page-description">配置系统参数和管理设置</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="exportAllSettings" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出配置
          </el-button>
          <el-button @click="importSettings">
            <el-icon><Upload /></el-icon>
            导入配置
          </el-button>
          <el-button type="primary" @click="saveAllSettings" :loading="saving">
            <el-icon><Check /></el-icon>
            保存所有设置
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 设置导航卡片 -->
    <div class="settings-grid">
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="setting-nav-card" @click="navigateToSystem" shadow="hover">
            <div class="nav-card-content">
              <div class="nav-icon">
                <el-icon size="32"><Setting /></el-icon>
              </div>
              <div class="nav-info">
                <h3>系统配置</h3>
                <p>基础设置、性能配置、安全设置等</p>
              </div>
              <div class="nav-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="setting-nav-card" @click="navigateToUserManagement" shadow="hover">
            <div class="nav-card-content">
              <div class="nav-icon">
                <el-icon size="32"><UserFilled /></el-icon>
              </div>
              <div class="nav-info">
                <h3>用户管理</h3>
                <p>用户账户管理、权限分配、角色设置</p>
              </div>
              <div class="nav-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="setting-nav-card" @click="navigateToUserProfile" shadow="hover">
            <div class="nav-card-content">
              <div class="nav-icon">
                <el-icon size="32"><User /></el-icon>
              </div>
              <div class="nav-info">
                <h3>个人设置</h3>
                <p>个人资料、偏好设置、安全配置</p>
              </div>
              <div class="nav-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快速设置面板 -->
    <div class="quick-settings">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon><Lightning /></el-icon>
            <span>快速设置</span>
          </div>
        </template>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <div class="quick-setting-item">
              <div class="setting-label">
                <el-icon><Monitor /></el-icon>
                <span>维护模式</span>
              </div>
              <el-switch 
                v-model="quickSettings.maintenanceMode" 
                @change="handleMaintenanceModeChange"
              />
            </div>
            
            <div class="quick-setting-item">
              <div class="setting-label">
                <el-icon><UserFilled /></el-icon>
                <span>允许用户注册</span>
              </div>
              <el-switch 
                v-model="quickSettings.allowRegistration" 
                @change="handleRegistrationChange"
              />
            </div>
            
            <div class="quick-setting-item">
              <div class="setting-label">
                <el-icon><Bell /></el-icon>
                <span>系统通知</span>
              </div>
              <el-switch 
                v-model="quickSettings.systemNotifications" 
                @change="handleNotificationChange"
              />
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="quick-setting-item">
              <div class="setting-label">
                <el-icon><Files /></el-icon>
                <span>自动备份</span>
              </div>
              <el-switch 
                v-model="quickSettings.autoBackup" 
                @change="handleBackupChange"
              />
            </div>
            
            <div class="quick-setting-item">
              <div class="setting-label">
                <el-icon><Document /></el-icon>
                <span>调试模式</span>
              </div>
              <el-switch 
                v-model="quickSettings.debugMode" 
                @change="handleDebugModeChange"
              />
            </div>
            
            <div class="quick-setting-item">
              <div class="setting-label">
                <el-icon><Lock /></el-icon>
                <span>API访问限制</span>
              </div>
              <el-switch 
                v-model="quickSettings.apiRateLimit" 
                @change="handleApiLimitChange"
              />
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 系统状态概览 -->
    <div class="system-overview">
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card>
            <el-statistic title="在线用户" :value="systemStats.onlineUsers">
              <template #suffix>
                <el-icon><UserFilled /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card>
            <el-statistic title="运行任务" :value="systemStats.runningTasks">
              <template #suffix>
                <el-icon><Loading /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card>
            <el-statistic title="系统运行时间" :value="systemStats.uptime" suffix="小时">
              <template #suffix>
                <el-icon><Timer /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  UserFilled,
  User,
  ArrowRight,
  Lightning,
  Monitor,
  Bell,
  Files,
  Document,
  Lock,
  Download,
  Upload,
  Check,
  Loading,
  Timer
} from '@element-plus/icons-vue'

const router = useRouter()

// 加载状态
const saving = ref(false)
const exporting = ref(false)

// 快速设置
const quickSettings = ref({
  maintenanceMode: false,
  allowRegistration: true,
  systemNotifications: true,
  autoBackup: true,
  debugMode: false,
  apiRateLimit: true
})

// 系统统计
const systemStats = ref({
  onlineUsers: 0,
  runningTasks: 0,
  uptime: 0
})

// 导航方法
const navigateToSystem = () => {
  router.push('/settings/system')
}

const navigateToUserManagement = () => {
  router.push('/settings/user-management')
}

const navigateToUserProfile = () => {
  router.push('/settings/user')
}

// 快速设置处理方法
const handleMaintenanceModeChange = (value) => {
  if (value) {
    ElMessageBox.confirm(
      '启用维护模式后，普通用户将无法访问系统，确定要启用吗？',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      ElMessage.success('维护模式已启用')
    }).catch(() => {
      quickSettings.value.maintenanceMode = false
    })
  } else {
    ElMessage.success('维护模式已关闭')
  }
}

const handleRegistrationChange = (value) => {
  ElMessage.success(value ? '已允许用户注册' : '已禁止用户注册')
}

const handleNotificationChange = (value) => {
  ElMessage.success(value ? '系统通知已启用' : '系统通知已关闭')
}

const handleBackupChange = (value) => {
  ElMessage.success(value ? '自动备份已启用' : '自动备份已关闭')
}

const handleDebugModeChange = (value) => {
  ElMessage.success(value ? '调试模式已启用' : '调试模式已关闭')
}

const handleApiLimitChange = (value) => {
  ElMessage.success(value ? 'API访问限制已启用' : 'API访问限制已关闭')
}

// 保存所有设置
const saveAllSettings = async () => {
  saving.value = true
  try {
    // 模拟保存操作
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('所有设置已保存')
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

// 导出配置
const exportAllSettings = async () => {
  exporting.value = true
  try {
    // 模拟导出操作
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('配置导出成功')
  } catch (error) {
    ElMessage.error('导出配置失败')
  } finally {
    exporting.value = false
  }
}

// 导入配置
const importSettings = () => {
  ElMessage.info('导入功能开发中')
}

// 获取系统统计信息
const fetchSystemStats = async () => {
  try {
    // 模拟获取系统统计
    systemStats.value = {
      onlineUsers: Math.floor(Math.random() * 100) + 10,
      runningTasks: Math.floor(Math.random() * 20) + 1,
      uptime: Math.floor(Math.random() * 1000) + 100
    }
  } catch (error) {
    console.error('获取系统统计失败:', error)
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchSystemStats()
  // 定时更新统计信息
  setInterval(fetchSystemStats, 30000)
})
</script>

<style lang="scss" scoped>
.system-settings-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
    
    .page-description {
      margin: 0;
      color: var(--el-text-color-regular);
    }
  }
}

.settings-grid {
  margin-bottom: 24px;
  
  .setting-nav-card {
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .nav-card-content {
      display: flex;
      align-items: center;
      padding: 8px 0;
      
      .nav-icon {
        margin-right: 16px;
        color: var(--el-color-primary);
      }
      
      .nav-info {
        flex: 1;
        
        h3 {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
        
        p {
          margin: 0;
          font-size: 12px;
          color: var(--el-text-color-regular);
        }
      }
      
      .nav-arrow {
        color: var(--el-text-color-placeholder);
      }
    }
  }
}

.quick-settings {
  margin-bottom: 24px;
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }
  
  .quick-setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    
    &:last-child {
      border-bottom: none;
    }
    
    .setting-label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }
  }
}

.system-overview {
  .el-card {
    text-align: center;
  }
  
  :deep(.el-statistic__content) {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
}
</style>