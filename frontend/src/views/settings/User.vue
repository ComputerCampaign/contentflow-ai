<template>
  <div class="user-settings-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户设置</h1>
        <p class="page-description">管理个人账户信息和偏好设置</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="resetProfile" type="danger" plain>
            <el-icon><RefreshLeft /></el-icon>
            重置信息
          </el-button>
          <el-button type="primary" @click="saveProfile" :loading="saving">
            <el-icon><Check /></el-icon>
            保存设置
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 设置内容 -->
    <div class="settings-content">
      <el-row :gutter="24">
        <!-- 左侧设置菜单 -->
        <el-col :span="6">
          <el-card class="settings-menu">
            <el-menu
              v-model:default-active="activeSection"
              mode="vertical"
              @select="handleSectionChange"
            >
              <el-menu-item index="profile">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
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
                <span>会话管理</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>
        
        <!-- 右侧设置面板 -->
        <el-col :span="18">
          <div class="settings-panel">
            <!-- 个人资料 -->
            <el-card v-show="activeSection === 'profile'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><User /></el-icon>
                  <span>个人资料</span>
                </div>
              </template>
              
              <div class="profile-section">
                <!-- 头像上传 -->
                <div class="avatar-section">
                  <div class="avatar-container">
                    <el-avatar :size="120" :src="userProfile.avatar" class="user-avatar">
                      <el-icon><User /></el-icon>
                    </el-avatar>
                    <div class="avatar-overlay">
                      <el-upload
                        :show-file-list="false"
                        :before-upload="beforeAvatarUpload"
                        :on-success="handleAvatarSuccess"
                        action="#"
                        accept="image/*"
                      >
                        <el-button size="small" type="primary" plain>
                          <el-icon><Camera /></el-icon>
                          更换头像
                        </el-button>
                      </el-upload>
                    </div>
                  </div>
                </div>
                
                <!-- 基本信息 -->
                <el-form :model="userProfile" label-width="120px" class="profile-form">
                  <el-form-item label="用户名">
                    <el-input v-model="userProfile.username" disabled>
                      <template #suffix>
                        <el-tooltip content="用户名不可修改" placement="top">
                          <el-icon><InfoFilled /></el-icon>
                        </el-tooltip>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item label="邮箱地址">
                    <el-input v-model="userProfile.email">
                      <template #suffix>
                        <el-tag v-if="userProfile.emailVerified" type="success" size="small">
                          已验证
                        </el-tag>
                        <el-tag v-else type="warning" size="small">
                          未验证
                        </el-tag>
                      </template>
                    </el-input>
                    <div v-if="!userProfile.emailVerified" class="verify-email">
                      <el-button size="small" type="primary" link @click="sendVerificationEmail">
                        发送验证邮件
                      </el-button>
                    </div>
                  </el-form-item>
                  
                  <el-form-item label="真实姓名">
                    <el-input v-model="userProfile.realName" placeholder="请输入真实姓名" />
                  </el-form-item>
                  
                  <el-form-item label="手机号码">
                    <el-input v-model="userProfile.phone" placeholder="请输入手机号码">
                      <template #suffix>
                        <el-tag v-if="userProfile.phoneVerified" type="success" size="small">
                          已验证
                        </el-tag>
                        <el-tag v-else type="warning" size="small">
                          未验证
                        </el-tag>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item label="公司/组织">
                    <el-input v-model="userProfile.company" placeholder="请输入公司或组织名称" />
                  </el-form-item>
                  
                  <el-form-item label="职位">
                    <el-input v-model="userProfile.position" placeholder="请输入职位" />
                  </el-form-item>
                  
                  <el-form-item label="个人简介">
                    <el-input
                      v-model="userProfile.bio"
                      type="textarea"
                      :rows="4"
                      placeholder="请输入个人简介"
                      maxlength="500"
                      show-word-limit
                    />
                  </el-form-item>
                  
                  <el-form-item label="个人网站">
                    <el-input v-model="userProfile.website" placeholder="https://example.com" />
                  </el-form-item>
                  
                  <el-form-item label="所在地区">
                    <el-cascader
                      v-model="userProfile.location"
                      :options="locationOptions"
                      placeholder="请选择所在地区"
                      style="width: 100%;"
                    />
                  </el-form-item>
                </el-form>
              </div>
            </el-card>
            
            <!-- 安全设置 -->
            <el-card v-show="activeSection === 'security'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Lock /></el-icon>
                  <span>安全设置</span>
                </div>
              </template>
              
              <div class="security-section">
                <!-- 修改密码 -->
                <div class="security-item">
                  <h3>修改密码</h3>
                  <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
                    <el-form-item label="当前密码" prop="currentPassword">
                      <el-input
                        v-model="passwordForm.currentPassword"
                        type="password"
                        placeholder="请输入当前密码"
                        show-password
                      />
                    </el-form-item>
                    
                    <el-form-item label="新密码" prop="newPassword">
                      <el-input
                        v-model="passwordForm.newPassword"
                        type="password"
                        placeholder="请输入新密码"
                        show-password
                      />
                    </el-form-item>
                    
                    <el-form-item label="确认密码" prop="confirmPassword">
                      <el-input
                        v-model="passwordForm.confirmPassword"
                        type="password"
                        placeholder="请再次输入新密码"
                        show-password
                      />
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button type="primary" @click="changePassword" :loading="changingPassword">
                        修改密码
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
                
                <el-divider />
                
                <!-- 双因子认证 -->
                <div class="security-item">
                  <div class="item-header">
                    <h3>双因子认证</h3>
                    <el-switch
                      v-model="userProfile.twoFactorEnabled"
                      @change="handleTwoFactorChange"
                    />
                  </div>
                  <p class="item-description">
                    启用双因子认证可以为您的账户提供额外的安全保护
                  </p>
                  
                  <div v-if="userProfile.twoFactorEnabled" class="two-factor-setup">
                    <el-alert
                      title="双因子认证已启用"
                      type="success"
                      :closable="false"
                      show-icon
                    />
                    <el-button @click="regenerateBackupCodes" style="margin-top: 12px;">
                      重新生成备用代码
                    </el-button>
                  </div>
                </div>
                
                <el-divider />
                
                <!-- 登录设备 -->
                <div class="security-item">
                  <h3>登录设备</h3>
                  <p class="item-description">管理已登录的设备和会话</p>
                  
                  <div class="device-list">
                    <div v-for="device in loginDevices" :key="device.id" class="device-item">
                      <div class="device-info">
                        <div class="device-icon">
                          <el-icon><Monitor v-if="device.type === 'desktop'" /><Cellphone v-else /></el-icon>
                        </div>
                        <div class="device-details">
                          <div class="device-name">{{ device.name }}</div>
                          <div class="device-meta">
                            <span>{{ device.location }}</span>
                            <span>{{ device.lastActive }}</span>
                          </div>
                        </div>
                      </div>
                      <div class="device-actions">
                        <el-tag v-if="device.current" type="success" size="small">当前设备</el-tag>
                        <el-button v-else size="small" type="danger" plain @click="revokeDevice(device.id)">
                          移除
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
            
            <!-- 偏好设置 -->
            <el-card v-show="activeSection === 'preferences'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Setting /></el-icon>
                  <span>偏好设置</span>
                </div>
              </template>
              
              <el-form :model="preferences" label-width="140px">
                <el-form-item label="界面语言">
                  <el-select v-model="preferences.language" style="width: 200px;">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                    <el-option label="日本語" value="ja-JP" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="主题模式">
                  <el-radio-group v-model="preferences.theme">
                    <el-radio label="light">浅色模式</el-radio>
                    <el-radio label="dark">深色模式</el-radio>
                    <el-radio label="auto">跟随系统</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <el-form-item label="时区设置">
                  <el-select v-model="preferences.timezone" style="width: 200px;">
                    <el-option label="Asia/Shanghai" value="Asia/Shanghai" />
                    <el-option label="UTC" value="UTC" />
                    <el-option label="America/New_York" value="America/New_York" />
                    <el-option label="Europe/London" value="Europe/London" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="日期格式">
                  <el-select v-model="preferences.dateFormat" style="width: 200px;">
                    <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
                    <el-option label="MM/DD/YYYY" value="MM/DD/YYYY" />
                    <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="时间格式">
                  <el-radio-group v-model="preferences.timeFormat">
                    <el-radio label="24h">24小时制</el-radio>
                    <el-radio label="12h">12小时制</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <el-form-item label="每页显示数量">
                  <el-select v-model="preferences.pageSize" style="width: 200px;">
                    <el-option label="10条" :value="10" />
                    <el-option label="20条" :value="20" />
                    <el-option label="50条" :value="50" />
                    <el-option label="100条" :value="100" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="自动保存">
                  <el-switch v-model="preferences.autoSave" />
                  <span class="form-item-tip">自动保存表单数据</span>
                </el-form-item>
                
                <el-form-item label="显示帮助提示">
                  <el-switch v-model="preferences.showTooltips" />
                  <span class="form-item-tip">显示界面元素的帮助提示</span>
                </el-form-item>
                
                <el-form-item label="启用快捷键">
                  <el-switch v-model="preferences.enableShortcuts" />
                  <span class="form-item-tip">启用键盘快捷键</span>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 通知设置 -->
            <el-card v-show="activeSection === 'notifications'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Bell /></el-icon>
                  <span>通知设置</span>
                </div>
              </template>
              
              <el-form :model="notifications" label-width="140px">
                <el-form-item label="邮件通知">
                  <el-switch v-model="notifications.email.enabled" />
                  <span class="form-item-tip">接收邮件通知</span>
                </el-form-item>
                
                <div v-if="notifications.email.enabled" class="notification-options">
                  <el-form-item label="通知类型">
                    <el-checkbox-group v-model="notifications.email.types">
                      <el-checkbox label="task_completed">任务完成</el-checkbox>
                      <el-checkbox label="task_failed">任务失败</el-checkbox>
                      <el-checkbox label="system_updates">系统更新</el-checkbox>
                      <el-checkbox label="security_alerts">安全警报</el-checkbox>
                      <el-checkbox label="weekly_report">周报</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                  
                  <el-form-item label="发送频率">
                    <el-radio-group v-model="notifications.email.frequency">
                      <el-radio label="immediate">立即发送</el-radio>
                      <el-radio label="daily">每日汇总</el-radio>
                      <el-radio label="weekly">每周汇总</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </div>
                
                <el-form-item label="浏览器通知">
                  <el-switch v-model="notifications.browser.enabled" @change="handleBrowserNotificationChange" />
                  <span class="form-item-tip">显示浏览器桌面通知</span>
                </el-form-item>
                
                <div v-if="notifications.browser.enabled" class="notification-options">
                  <el-form-item label="通知类型">
                    <el-checkbox-group v-model="notifications.browser.types">
                      <el-checkbox label="task_completed">任务完成</el-checkbox>
                      <el-checkbox label="task_failed">任务失败</el-checkbox>
                      <el-checkbox label="system_alerts">系统警报</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                </div>
                
                <el-form-item label="应用内通知">
                  <el-switch v-model="notifications.inApp.enabled" />
                  <span class="form-item-tip">显示应用内通知</span>
                </el-form-item>
                
                <div v-if="notifications.inApp.enabled" class="notification-options">
                  <el-form-item label="通知类型">
                    <el-checkbox-group v-model="notifications.inApp.types">
                      <el-checkbox label="task_completed">任务完成</el-checkbox>
                      <el-checkbox label="task_failed">任务失败</el-checkbox>
                      <el-checkbox label="system_updates">系统更新</el-checkbox>
                      <el-checkbox label="mentions">@提及</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                  
                  <el-form-item label="声音提醒">
                    <el-switch v-model="notifications.inApp.sound" />
                  </el-form-item>
                </div>
              </el-form>
            </el-card>
            
            <!-- 隐私设置 -->
            <el-card v-show="activeSection === 'privacy'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><View /></el-icon>
                  <span>隐私设置</span>
                </div>
              </template>
              
              <el-form :model="privacy" label-width="140px">
                <el-form-item label="个人资料可见性">
                  <el-radio-group v-model="privacy.profileVisibility">
                    <el-radio label="public">公开</el-radio>
                    <el-radio label="private">私有</el-radio>
                    <el-radio label="team">仅团队成员</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <el-form-item label="活动状态">
                  <el-switch v-model="privacy.showOnlineStatus" />
                  <span class="form-item-tip">显示在线状态</span>
                </el-form-item>
                
                <el-form-item label="最后活动时间">
                  <el-switch v-model="privacy.showLastSeen" />
                  <span class="form-item-tip">显示最后活动时间</span>
                </el-form-item>
                
                <el-form-item label="数据收集">
                  <el-switch v-model="privacy.allowDataCollection" />
                  <span class="form-item-tip">允许收集使用数据以改进服务</span>
                </el-form-item>
                
                <el-form-item label="第三方集成">
                  <el-switch v-model="privacy.allowThirdPartyIntegration" />
                  <span class="form-item-tip">允许第三方服务集成</span>
                </el-form-item>
                
                <el-form-item label="搜索引擎索引">
                  <el-switch v-model="privacy.allowSearchEngineIndexing" />
                  <span class="form-item-tip">允许搜索引擎索引个人资料</span>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 会话管理 -->
            <el-card v-show="activeSection === 'sessions'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Monitor /></el-icon>
                  <span>会话管理</span>
                </div>
              </template>
              
              <div class="sessions-section">
                <div class="sessions-header">
                  <p>管理您的活动会话。您可以查看和终止其他设备上的会话。</p>
                  <el-button type="danger" plain @click="terminateAllSessions">
                    终止所有其他会话
                  </el-button>
                </div>
                
                <div class="sessions-list">
                  <div v-for="session in activeSessions" :key="session.id" class="session-item">
                    <div class="session-info">
                      <div class="session-icon">
                        <el-icon><Monitor v-if="session.device === 'desktop'" /><Cellphone v-else /></el-icon>
                      </div>
                      <div class="session-details">
                        <div class="session-title">
                          {{ session.browser }} on {{ session.os }}
                          <el-tag v-if="session.current" type="success" size="small">当前会话</el-tag>
                        </div>
                        <div class="session-meta">
                          <span>IP: {{ session.ip }}</span>
                          <span>位置: {{ session.location }}</span>
                          <span>最后活动: {{ session.lastActive }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="session-actions">
                      <el-button v-if="!session.current" size="small" type="danger" plain @click="terminateSession(session.id)">
                        终止会话
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadProps } from 'element-plus'
import {
  User,
  Lock,
  Setting,
  Bell,
  View,
  Monitor,
  RefreshLeft,
  Check,
  Camera,
  InfoFilled,
  Cellphone
} from '@element-plus/icons-vue'

interface UserProfile {
  username: string
  email: string
  emailVerified: boolean
  realName: string
  phone: string
  phoneVerified: boolean
  company: string
  position: string
  bio: string
  website: string
  location: string[]
  avatar: string
  twoFactorEnabled: boolean
}

interface PasswordForm {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

interface Preferences {
  language: string
  theme: string
  timezone: string
  dateFormat: string
  timeFormat: string
  pageSize: number
  autoSave: boolean
  showTooltips: boolean
  enableShortcuts: boolean
}

interface Notifications {
  email: {
    enabled: boolean
    types: string[]
    frequency: string
  }
  browser: {
    enabled: boolean
    types: string[]
  }
  inApp: {
    enabled: boolean
    types: string[]
    sound: boolean
  }
}

interface Privacy {
  profileVisibility: string
  showOnlineStatus: boolean
  showLastSeen: boolean
  allowDataCollection: boolean
  allowThirdPartyIntegration: boolean
  allowSearchEngineIndexing: boolean
}

interface LoginDevice {
  id: string
  name: string
  type: string
  location: string
  lastActive: string
  current: boolean
}

interface ActiveSession {
  id: string
  browser: string
  os: string
  device: string
  ip: string
  location: string
  lastActive: string
  current: boolean
}

// 响应式数据
const activeSection = ref('profile')
const saving = ref(false)
const changingPassword = ref(false)
const passwordFormRef = ref<FormInstance>()

// 用户资料
const userProfile = reactive<UserProfile>({
  username: 'admin',
  email: 'admin@example.com',
  emailVerified: true,
  realName: '管理员',
  phone: '13800138000',
  phoneVerified: false,
  company: 'ContentFlow AI',
  position: '系统管理员',
  bio: '专注于智能内容采集与处理技术',
  website: 'https://contentflow.ai',
  location: ['中国', '北京市', '朝阳区'],
  avatar: '',
  twoFactorEnabled: false
})

// 密码表单
const passwordForm = reactive<PasswordForm>({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 偏好设置
const preferences = reactive<Preferences>({
  language: 'zh-CN',
  theme: 'light',
  timezone: 'Asia/Shanghai',
  dateFormat: 'YYYY-MM-DD',
  timeFormat: '24h',
  pageSize: 20,
  autoSave: true,
  showTooltips: true,
  enableShortcuts: true
})

// 通知设置
const notifications = reactive<Notifications>({
  email: {
    enabled: true,
    types: ['task_completed', 'task_failed', 'security_alerts'],
    frequency: 'immediate'
  },
  browser: {
    enabled: false,
    types: ['task_completed', 'system_alerts']
  },
  inApp: {
    enabled: true,
    types: ['task_completed', 'task_failed', 'mentions'],
    sound: true
  }
})

// 隐私设置
const privacy = reactive<Privacy>({
  profileVisibility: 'team',
  showOnlineStatus: true,
  showLastSeen: true,
  allowDataCollection: true,
  allowThirdPartyIntegration: false,
  allowSearchEngineIndexing: false
})

// 登录设备
const loginDevices = ref<LoginDevice[]>([
  {
    id: '1',
    name: 'Chrome on Windows',
    type: 'desktop',
    location: '北京市',
    lastActive: '2分钟前',
    current: true
  },
  {
    id: '2',
    name: 'Safari on iPhone',
    type: 'mobile',
    location: '上海市',
    lastActive: '1小时前',
    current: false
  }
])

// 活动会话
const activeSessions = ref<ActiveSession[]>([
  {
    id: '1',
    browser: 'Chrome 120.0',
    os: 'Windows 11',
    device: 'desktop',
    ip: '192.168.1.100',
    location: '北京市',
    lastActive: '2分钟前',
    current: true
  },
  {
    id: '2',
    browser: 'Safari 17.0',
    os: 'iOS 17.0',
    device: 'mobile',
    ip: '192.168.1.101',
    location: '上海市',
    lastActive: '1小时前',
    current: false
  }
])

// 地区选项
const locationOptions = [
  {
    value: '中国',
    label: '中国',
    children: [
      {
        value: '北京市',
        label: '北京市',
        children: [
          { value: '朝阳区', label: '朝阳区' },
          { value: '海淀区', label: '海淀区' }
        ]
      },
      {
        value: '上海市',
        label: '上海市',
        children: [
          { value: '浦东新区', label: '浦东新区' },
          { value: '黄浦区', label: '黄浦区' }
        ]
      }
    ]
  }
]

// 密码验证规则
const passwordRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' }
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

// 方法
const handleSectionChange = (section: string) => {
  activeSection.value = section
}

const saveProfile = async () => {
  saving.value = true
  
  try {
    // 模拟保存过程
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    ElMessage.success('用户设置保存成功')
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

const resetProfile = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置个人信息吗？此操作将恢复到默认设置。',
      '确认重置',
      {
        type: 'warning'
      }
    )
    
    // 重置用户资料
    Object.assign(userProfile, {
      realName: '',
      phone: '',
      company: '',
      position: '',
      bio: '',
      website: '',
      location: []
    })
    
    ElMessage.success('个人信息已重置')
  } catch (error) {
    // 用户取消操作
  }
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像只能是 JPG/PNG 格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const handleAvatarSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
  userProfile.avatar = URL.createObjectURL(uploadFile.raw!)
  ElMessage.success('头像上传成功')
}

const sendVerificationEmail = async () => {
  try {
    // 模拟发送验证邮件
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('验证邮件已发送，请查收')
  } catch (error) {
    ElMessage.error('发送验证邮件失败')
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate((valid) => {
    if (valid) {
      changingPassword.value = true
      
      // 模拟修改密码
      setTimeout(() => {
        changingPassword.value = false
        
        // 重置表单
        Object.assign(passwordForm, {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        })
        
        ElMessage.success('密码修改成功')
      }, 1500)
    }
  })
}

const handleTwoFactorChange = async (enabled: boolean) => {
  if (enabled) {
    try {
      await ElMessageBox.confirm(
        '启用双因子认证需要您使用认证应用扫描二维码。确定要继续吗？',
        '启用双因子认证',
        {
          type: 'info'
        }
      )
      
      // 这里应该显示二维码设置流程
      ElMessage.success('双因子认证已启用')
    } catch (error) {
      userProfile.twoFactorEnabled = false
    }
  } else {
    try {
      await ElMessageBox.confirm(
        '确定要关闭双因子认证吗？这将降低您账户的安全性。',
        '关闭双因子认证',
        {
          type: 'warning'
        }
      )
      
      ElMessage.success('双因子认证已关闭')
    } catch (error) {
      userProfile.twoFactorEnabled = true
    }
  }
}

const regenerateBackupCodes = async () => {
  try {
    await ElMessageBox.confirm(
      '重新生成备用代码将使之前的代码失效。确定要继续吗？',
      '重新生成备用代码',
      {
        type: 'warning'
      }
    )
    
    ElMessage.success('备用代码已重新生成')
  } catch (error) {
    // 用户取消操作
  }
}

const revokeDevice = async (deviceId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要移除此设备吗？该设备将被强制退出登录。',
      '移除设备',
      {
        type: 'warning'
      }
    )
    
    loginDevices.value = loginDevices.value.filter(device => device.id !== deviceId)
    ElMessage.success('设备已移除')
  } catch (error) {
    // 用户取消操作
  }
}

const handleBrowserNotificationChange = async (enabled: boolean) => {
  if (enabled) {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') {
        notifications.browser.enabled = false
        ElMessage.warning('需要授权浏览器通知权限')
      }
    } else {
      notifications.browser.enabled = false
      ElMessage.error('您的浏览器不支持桌面通知')
    }
  }
}

const terminateSession = async (sessionId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要终止此会话吗？该设备将被强制退出登录。',
      '终止会话',
      {
        type: 'warning'
      }
    )
    
    activeSessions.value = activeSessions.value.filter(session => session.id !== sessionId)
    ElMessage.success('会话已终止')
  } catch (error) {
    // 用户取消操作
  }
}

const terminateAllSessions = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要终止所有其他会话吗？所有其他设备将被强制退出登录。',
      '终止所有会话',
      {
        type: 'warning'
      }
    )
    
    activeSessions.value = activeSessions.value.filter(session => session.current)
    ElMessage.success('所有其他会话已终止')
  } catch (error) {
    // 用户取消操作
  }
}

// 生命周期
onMounted(() => {
  // 加载用户设置
  // 这里可以从API加载实际的用户数据
})
</script>

<style lang="scss" scoped>
.user-settings-container {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .header-left {
      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 8px 0;
      }
      
      .page-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 0;
      }
    }
  }
  
  .settings-content {
    .settings-menu {
      .el-menu {
        border-right: none;
        
        .el-menu-item {
          border-radius: 6px;
          margin-bottom: 4px;
          
          &.is-active {
            background-color: var(--el-color-primary-light-9);
            color: var(--el-color-primary);
          }
        }
      }
    }
    
    .settings-panel {
      .setting-card {
        margin-bottom: 16px;
        
        .card-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
        }
        
        .form-item-tip {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-left: 12px;
        }
      }
    }
  }
  
  .profile-section {
    .avatar-section {
      display: flex;
      justify-content: center;
      margin-bottom: 32px;
      
      .avatar-container {
        position: relative;
        
        .user-avatar {
          border: 4px solid var(--el-border-color-light);
        }
        
        .avatar-overlay {
          position: absolute;
          bottom: -10px;
          left: 50%;
          transform: translateX(-50%);
        }
      }
    }
    
    .profile-form {
      max-width: 600px;
      
      .verify-email {
        margin-top: 8px;
      }
    }
  }
  
  .security-section {
    .security-item {
      margin-bottom: 32px;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 16px 0;
      }
      
      .item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        h3 {
          margin: 0;
        }
      }
      
      .item-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 0 0 16px 0;
      }
      
      .two-factor-setup {
        margin-top: 16px;
      }
    }
    
    .device-list {
      .device-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        border: 1px solid var(--el-border-color-light);
        border-radius: 8px;
        margin-bottom: 12px;
        
        .device-info {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .device-icon {
            font-size: 24px;
            color: var(--el-text-color-secondary);
          }
          
          .device-details {
            .device-name {
              font-weight: 500;
              color: var(--el-text-color-primary);
              margin-bottom: 4px;
            }
            
            .device-meta {
              font-size: 12px;
              color: var(--el-text-color-secondary);
              
              span {
                margin-right: 16px;
              }
            }
          }
        }
      }
    }
  }
  
  .notification-options {
    margin-left: 20px;
    padding-left: 20px;
    border-left: 2px solid var(--el-border-color-light);
  }
  
  .sessions-section {
    .sessions-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
      
      p {
        margin: 0;
        color: var(--el-text-color-secondary);
        flex: 1;
        margin-right: 16px;
      }
    }
    
    .sessions-list {
      .session-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        border: 1px solid var(--el-border-color-light);
        border-radius: 8px;
        margin-bottom: 12px;
        
        .session-info {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .session-icon {
            font-size: 24px;
            color: var(--el-text-color-secondary);
          }
          
          .session-details {
            .session-title {
              font-weight: 500;
              color: var(--el-text-color-primary);
              margin-bottom: 4px;
              display: flex;
              align-items: center;
              gap: 8px;
            }
            
            .session-meta {
              font-size: 12px;
              color: var(--el-text-color-secondary);
              
              span {
                margin-right: 16px;
              }
            }
          }
        }
      }
    }
  }
}
</style>