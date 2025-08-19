<template>
  <div class="user-profile-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">个人资料</h1>
        <p class="page-description">管理您的个人信息和账户设置</p>
      </div>
      <div class="header-right">
        <el-button @click="handleSave" type="primary" :loading="saving">
          <el-icon><Check /></el-icon>
          保存更改
        </el-button>
      </div>
    </div>

    <div class="profile-container">
      <!-- 左侧导航 -->
      <div class="profile-sidebar">
        <el-menu
          v-model="activeTab"
          class="profile-menu"
          @select="handleTabChange"
        >
          <el-menu-item index="basic">
            <el-icon><User /></el-icon>
            <span>基本信息</span>
          </el-menu-item>
          <el-menu-item index="security">
            <el-icon><Lock /></el-icon>
            <span>安全设置</span>
          </el-menu-item>
          <el-menu-item index="preferences">
            <el-icon><Setting /></el-icon>
            <span>偏好设置</span>
          </el-menu-item>
          <el-menu-item index="notifications">
            <el-icon><Bell /></el-icon>
            <span>通知设置</span>
          </el-menu-item>
          <el-menu-item index="privacy">
            <el-icon><View /></el-icon>
            <span>隐私设置</span>
          </el-menu-item>
          <el-menu-item index="sessions">
            <el-icon><Monitor /></el-icon>
            <span>登录会话</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容 -->
      <div class="profile-content">
        <!-- 基本信息 -->
        <div v-show="activeTab === 'basic'" class="tab-content">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3>基本信息</h3>
                <p>管理您的基本个人信息</p>
              </div>
            </template>
            
            <div class="avatar-section">
              <div class="avatar-container">
                <el-avatar :size="80" :src="userInfo.avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <div class="avatar-actions">
                  <el-button size="small" @click="handleAvatarUpload">
                    <el-icon><Upload /></el-icon>
                    更换头像
                  </el-button>
                  <el-button size="small" @click="handleAvatarRemove" type="danger" plain>
                    <el-icon><Delete /></el-icon>
                    删除头像
                  </el-button>
                </div>
              </div>
            </div>
            
            <el-form
              ref="basicFormRef"
              :model="userInfo"
              :rules="basicFormRules"
              label-width="100px"
              class="profile-form"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="userInfo.username" disabled />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="userInfo.email" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="真实姓名" prop="realName">
                    <el-input v-model="userInfo.realName" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="手机号" prop="phone">
                    <el-input v-model="userInfo.phone" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="性别">
                    <el-radio-group v-model="userInfo.gender">
                      <el-radio label="male">男</el-radio>
                      <el-radio label="female">女</el-radio>
                      <el-radio label="other">其他</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="生日">
                    <el-date-picker
                      v-model="userInfo.birthday"
                      type="date"
                      placeholder="选择生日"
                      style="width: 100%;"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-form-item label="个人简介">
                <el-input
                  v-model="userInfo.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="介绍一下自己..."
                />
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 安全设置 -->
        <div v-show="activeTab === 'security'" class="tab-content">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3>安全设置</h3>
                <p>管理您的账户安全</p>
              </div>
            </template>
            
            <div class="security-items">
              <div class="security-item">
                <div class="item-info">
                  <h4>修改密码</h4>
                  <p>定期更换密码以保护账户安全</p>
                </div>
                <el-button @click="showPasswordDialog">修改密码</el-button>
              </div>
              
              <el-divider />
              
              <div class="security-item">
                <div class="item-info">
                  <h4>两步验证</h4>
                  <p>为您的账户添加额外的安全保护</p>
                </div>
                <el-switch
                  v-model="securitySettings.twoFactorEnabled"
                  @change="handleTwoFactorChange"
                />
              </div>
              
              <el-divider />
              
              <div class="security-item">
                <div class="item-info">
                  <h4>登录通知</h4>
                  <p>当有新设备登录时通知您</p>
                </div>
                <el-switch v-model="securitySettings.loginNotification" />
              </div>
              
              <el-divider />
              
              <div class="security-item">
                <div class="item-info">
                  <h4>账户锁定</h4>
                  <p>多次登录失败后自动锁定账户</p>
                </div>
                <el-switch v-model="securitySettings.accountLock" />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 偏好设置 -->
        <div v-show="activeTab === 'preferences'" class="tab-content">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3>偏好设置</h3>
                <p>个性化您的使用体验</p>
              </div>
            </template>
            
            <el-form label-width="120px" class="preferences-form">
              <el-form-item label="界面语言">
                <el-select v-model="preferences.language" style="width: 200px;">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                  <el-option label="繁體中文" value="zh-TW" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="时区">
                <el-select v-model="preferences.timezone" style="width: 200px;">
                  <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                  <el-option label="东京时间 (UTC+9)" value="Asia/Tokyo" />
                  <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
                  <el-option label="伦敦时间 (UTC+0)" value="Europe/London" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="主题模式">
                <el-radio-group v-model="preferences.theme">
                  <el-radio label="light">浅色模式</el-radio>
                  <el-radio label="dark">深色模式</el-radio>
                  <el-radio label="auto">跟随系统</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="每页显示">
                <el-select v-model="preferences.pageSize" style="width: 120px;">
                  <el-option label="10" :value="10" />
                  <el-option label="20" :value="20" />
                  <el-option label="50" :value="50" />
                  <el-option label="100" :value="100" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="自动保存">
                <el-switch v-model="preferences.autoSave" />
                <span class="form-tip">编辑时自动保存草稿</span>
              </el-form-item>
              
              <el-form-item label="快捷键">
                <el-switch v-model="preferences.shortcuts" />
                <span class="form-tip">启用键盘快捷键</span>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 通知设置 -->
        <div v-show="activeTab === 'notifications'" class="tab-content">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3>通知设置</h3>
                <p>管理您接收的通知类型</p>
              </div>
            </template>
            
            <div class="notification-groups">
              <div class="notification-group">
                <h4>邮件通知</h4>
                <div class="notification-items">
                  <div class="notification-item">
                    <div class="item-info">
                      <span>任务完成通知</span>
                      <p>爬虫任务完成时发送邮件</p>
                    </div>
                    <el-switch v-model="notifications.email.taskComplete" />
                  </div>
                  
                  <div class="notification-item">
                    <div class="item-info">
                      <span>任务失败通知</span>
                      <p>爬虫任务失败时发送邮件</p>
                    </div>
                    <el-switch v-model="notifications.email.taskFailed" />
                  </div>
                  
                  <div class="notification-item">
                    <div class="item-info">
                      <span>系统维护通知</span>
                      <p>系统维护时发送邮件</p>
                    </div>
                    <el-switch v-model="notifications.email.maintenance" />
                  </div>
                </div>
              </div>
              
              <el-divider />
              
              <div class="notification-group">
                <h4>浏览器通知</h4>
                <div class="notification-items">
                  <div class="notification-item">
                    <div class="item-info">
                      <span>桌面通知</span>
                      <p>在浏览器中显示桌面通知</p>
                    </div>
                    <el-switch v-model="notifications.browser.desktop" />
                  </div>
                  
                  <div class="notification-item">
                    <div class="item-info">
                      <span>声音提醒</span>
                      <p>通知时播放提示音</p>
                    </div>
                    <el-switch v-model="notifications.browser.sound" />
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 隐私设置 -->
        <div v-show="activeTab === 'privacy'" class="tab-content">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3>隐私设置</h3>
                <p>控制您的隐私和数据使用</p>
              </div>
            </template>
            
            <div class="privacy-items">
              <div class="privacy-item">
                <div class="item-info">
                  <h4>个人资料可见性</h4>
                  <p>控制其他用户是否可以查看您的个人资料</p>
                </div>
                <el-radio-group v-model="privacy.profileVisibility">
                  <el-radio label="public">公开</el-radio>
                  <el-radio label="private">私密</el-radio>
                </el-radio-group>
              </div>
              
              <el-divider />
              
              <div class="privacy-item">
                <div class="item-info">
                  <h4>活动状态</h4>
                  <p>显示您的在线状态</p>
                </div>
                <el-switch v-model="privacy.showOnlineStatus" />
              </div>
              
              <el-divider />
              
              <div class="privacy-item">
                <div class="item-info">
                  <h4>数据收集</h4>
                  <p>允许收集使用数据以改善服务</p>
                </div>
                <el-switch v-model="privacy.dataCollection" />
              </div>
              
              <el-divider />
              
              <div class="privacy-item">
                <div class="item-info">
                  <h4>第三方集成</h4>
                  <p>允许第三方服务访问您的数据</p>
                </div>
                <el-switch v-model="privacy.thirdPartyIntegration" />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 登录会话 -->
        <div v-show="activeTab === 'sessions'" class="tab-content">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3>登录会话</h3>
                <p>管理您的活跃登录会话</p>
              </div>
            </template>
            
            <div class="sessions-list">
              <div v-for="session in sessions" :key="session.id" class="session-item">
                <div class="session-info">
                  <div class="session-device">
                    <el-icon><Monitor /></el-icon>
                    <div class="device-info">
                      <h4>{{ session.device }}</h4>
                      <p>{{ session.browser }} · {{ session.os }}</p>
                    </div>
                  </div>
                  <div class="session-details">
                    <p class="session-location">
                      <el-icon><Location /></el-icon>
                      {{ session.location }}
                    </p>
                    <p class="session-time">
                      <el-icon><Clock /></el-icon>
                      {{ session.lastActive }}
                    </p>
                    <el-tag v-if="session.current" type="success" size="small">当前会话</el-tag>
                  </div>
                </div>
                <div class="session-actions">
                  <el-button
                    v-if="!session.current"
                    size="small"
                    type="danger"
                    @click="terminateSession(session)"
                  >
                    终止会话
                  </el-button>
                </div>
              </div>
            </div>
            
            <div class="sessions-actions">
              <el-button @click="terminateAllSessions" type="danger">
                <el-icon><Delete /></el-icon>
                终止所有其他会话
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordFormRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePasswordChange" :loading="changingPassword">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  User,
  Lock,
  Setting,
  Bell,
  View,
  Monitor,
  Upload,
  Delete,
  Location,
  Clock
} from '@element-plus/icons-vue'

// 响应式数据
const saving = ref(false)
const changingPassword = ref(false)
const activeTab = ref('basic')
const passwordDialogVisible = ref(false)

// 用户信息
const userInfo = reactive({
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  realName: '系统管理员',
  phone: '13800138000',
  gender: 'male',
  birthday: null,
  bio: '这是一个系统管理员账户',
  avatar: ''
})

// 安全设置
const securitySettings = reactive({
  twoFactorEnabled: false,
  loginNotification: true,
  accountLock: true
})

// 偏好设置
const preferences = reactive({
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  theme: 'light',
  pageSize: 20,
  autoSave: true,
  shortcuts: true
})

// 通知设置
const notifications = reactive({
  email: {
    taskComplete: true,
    taskFailed: true,
    maintenance: true
  },
  browser: {
    desktop: true,
    sound: false
  }
})

// 隐私设置
const privacy = reactive({
  profileVisibility: 'public',
  showOnlineStatus: true,
  dataCollection: true,
  thirdPartyIntegration: false
})

// 登录会话
const sessions = ref([
  {
    id: 1,
    device: 'MacBook Pro',
    browser: 'Chrome 120.0',
    os: 'macOS 14.0',
    location: '北京, 中国',
    lastActive: '刚刚',
    current: true
  },
  {
    id: 2,
    device: 'iPhone 15',
    browser: 'Safari 17.0',
    os: 'iOS 17.0',
    location: '上海, 中国',
    lastActive: '2小时前',
    current: false
  }
])

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const basicFormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordFormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const basicFormRef = ref()
const passwordFormRef = ref()

// 切换标签页
const handleTabChange = (key) => {
  activeTab.value = key
}

// 保存设置
const handleSave = async () => {
  if (!basicFormRef.value) return
  
  try {
    await basicFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    saving.value = false
  }
}

// 头像上传
const handleAvatarUpload = () => {
  // 模拟头像上传
  ElMessage.info('头像上传功能待实现')
}

// 删除头像
const handleAvatarRemove = () => {
  userInfo.avatar = ''
  ElMessage.success('头像已删除')
}

// 显示修改密码对话框
const showPasswordDialog = () => {
  passwordDialogVisible.value = true
  // 重置表单
  Object.assign(passwordForm, {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
}

// 修改密码
const handlePasswordChange = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    changingPassword.value = false
  }
}

// 两步验证切换
const handleTwoFactorChange = (enabled) => {
  if (enabled) {
    ElMessage.info('两步验证功能待实现')
  } else {
    ElMessage.success('两步验证已关闭')
  }
}

// 终止会话
const terminateSession = async (session) => {
  try {
    await ElMessageBox.confirm(
      `确定要终止 "${session.device}" 的登录会话吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = sessions.value.findIndex(s => s.id === session.id)
    if (index > -1) {
      sessions.value.splice(index, 1)
    }
    ElMessage.success('会话已终止')
  } catch {
    // 用户取消操作
  }
}

// 终止所有其他会话
const terminateAllSessions = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要终止所有其他设备的登录会话吗？',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    sessions.value = sessions.value.filter(session => session.current)
    ElMessage.success('所有其他会话已终止')
  } catch {
    // 用户取消操作
  }
}

// 组件挂载时初始化数据
onMounted(() => {
  // 初始化用户数据
})
</script>

<style lang="scss" scoped>
.user-profile-page {
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

.profile-container {
  display: flex;
  gap: 24px;
  height: calc(100vh - 200px);
}

.profile-sidebar {
  width: 200px;
  flex-shrink: 0;
  
  .profile-menu {
    border-radius: 8px;
    border: 1px solid var(--el-border-color-light);
    
    :deep(.el-menu-item) {
      height: 48px;
      line-height: 48px;
      
      &.is-active {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
      }
    }
  }
}

.profile-content {
  flex: 1;
  overflow-y: auto;
}

.tab-content {
  .info-card {
    .card-header {
      h3 {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }
      
      p {
        margin: 0;
        color: var(--el-text-color-regular);
        font-size: 14px;
      }
    }
  }
}

.avatar-section {
  margin-bottom: 32px;
  
  .avatar-container {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .avatar-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.profile-form {
  .form-tip {
    margin-left: 8px;
    color: var(--el-text-color-regular);
    font-size: 12px;
  }
}

.security-items,
.privacy-items {
  .security-item,
  .privacy-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    
    .item-info {
      flex: 1;
      
      h4 {
        margin: 0 0 4px 0;
        font-size: 16px;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
      
      p {
        margin: 0;
        color: var(--el-text-color-regular);
        font-size: 14px;
      }
    }
  }
}

.notification-groups {
  .notification-group {
    margin-bottom: 24px;
    
    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    
    .notification-items {
      .notification-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        
        .item-info {
          flex: 1;
          
          span {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }
          
          p {
            margin: 0;
            color: var(--el-text-color-regular);
            font-size: 12px;
          }
        }
      }
    }
  }
}

.sessions-list {
  .session-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    margin-bottom: 12px;
    
    .session-info {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 16px;
      
      .session-device {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .el-icon {
          font-size: 24px;
          color: var(--el-text-color-regular);
        }
        
        .device-info {
          h4 {
            margin: 0 0 4px 0;
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary);
          }
          
          p {
            margin: 0;
            color: var(--el-text-color-regular);
            font-size: 12px;
          }
        }
      }
      
      .session-details {
        display: flex;
        flex-direction: column;
        gap: 4px;
        
        p {
          margin: 0;
          display: flex;
          align-items: center;
          gap: 4px;
          color: var(--el-text-color-regular);
          font-size: 12px;
          
          .el-icon {
            font-size: 12px;
          }
        }
      }
    }
  }
}

.sessions-actions {
  margin-top: 24px;
  text-align: center;
}

.dialog-footer {
  text-align: right;
}
</style>