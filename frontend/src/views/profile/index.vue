<template>
  <div class="profile-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">个人资料</h1>
        <p class="page-description">查看和管理您的个人信息</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="editProfile" type="primary">
            <el-icon><Edit /></el-icon>
            编辑资料
          </el-button>
          <el-button @click="exportProfile" plain>
            <el-icon><Download /></el-icon>
            导出资料
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 个人资料内容 -->
    <div class="profile-content">
      <el-row :gutter="24">
        <!-- 左侧个人信息卡片 -->
        <el-col :span="8">
          <el-card class="profile-card">
            <div class="profile-header">
              <div class="avatar-section">
                <el-avatar :size="120" :src="userProfile.avatar" class="user-avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <div class="status-indicator" :class="userProfile.onlineStatus">
                  <span class="status-dot"></span>
                  <span class="status-text">{{ getStatusText(userProfile.onlineStatus) }}</span>
                </div>
              </div>
              
              <div class="profile-info">
                <h2 class="username">{{ userProfile.realName || userProfile.username }}</h2>
                <p class="user-title">{{ userProfile.position || '用户' }}</p>
                <p class="user-company">{{ userProfile.company }}</p>
                
                <div class="user-stats">
                  <div class="stat-item">
                    <span class="stat-value">{{ userStats.totalTasks }}</span>
                    <span class="stat-label">总任务数</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ userStats.completedTasks }}</span>
                    <span class="stat-label">已完成</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ userStats.successRate }}%</span>
                    <span class="stat-label">成功率</span>
                  </div>
                </div>
              </div>
            </div>
            
            <el-divider />
            
            <div class="profile-details">
              <div class="detail-item">
                <el-icon><Message /></el-icon>
                <span class="detail-label">邮箱</span>
                <span class="detail-value">{{ userProfile.email }}</span>
                <el-tag v-if="userProfile.emailVerified" type="success" size="small">已验证</el-tag>
              </div>
              
              <div class="detail-item">
                <el-icon><Phone /></el-icon>
                <span class="detail-label">手机</span>
                <span class="detail-value">{{ userProfile.phone || '未设置' }}</span>
                <el-tag v-if="userProfile.phoneVerified" type="success" size="small">已验证</el-tag>
              </div>
              
              <div class="detail-item">
                <el-icon><Location /></el-icon>
                <span class="detail-label">地区</span>
                <span class="detail-value">{{ formatLocation(userProfile.location) }}</span>
              </div>
              
              <div class="detail-item">
                <el-icon><Link /></el-icon>
                <span class="detail-label">网站</span>
                <a v-if="userProfile.website" :href="userProfile.website" target="_blank" class="detail-link">
                  {{ userProfile.website }}
                </a>
                <span v-else class="detail-value">未设置</span>
              </div>
              
              <div class="detail-item">
                <el-icon><Calendar /></el-icon>
                <span class="detail-label">注册时间</span>
                <span class="detail-value">{{ formatDate(userProfile.createdAt) }}</span>
              </div>
              
              <div class="detail-item">
                <el-icon><Clock /></el-icon>
                <span class="detail-label">最后登录</span>
                <span class="detail-value">{{ formatDate(userProfile.lastLoginAt) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧详细信息 -->
        <el-col :span="16">
          <div class="profile-tabs">
            <el-tabs v-model="activeTab" type="card">
              <!-- 个人简介 -->
              <el-tab-pane label="个人简介" name="bio">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <el-icon><Document /></el-icon>
                      <span>个人简介</span>
                    </div>
                  </template>
                  
                  <div class="bio-content">
                    <p v-if="userProfile.bio" class="bio-text">{{ userProfile.bio }}</p>
                    <el-empty v-else description="暂无个人简介" :image-size="100" />
                  </div>
                </el-card>
              </el-tab-pane>
              
              <!-- 活动统计 -->
              <el-tab-pane label="活动统计" name="activity">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <el-icon><TrendCharts /></el-icon>
                      <span>活动统计</span>
                      <div class="header-actions">
                        <el-select v-model="activityPeriod" size="small" style="width: 120px;">
                          <el-option label="最近7天" value="7d" />
                          <el-option label="最近30天" value="30d" />
                          <el-option label="最近90天" value="90d" />
                        </el-select>
                      </div>
                    </div>
                  </template>
                  
                  <div class="activity-stats">
                    <!-- 统计卡片 -->
                    <el-row :gutter="16" class="stats-cards">
                      <el-col :span="6">
                        <div class="stat-card">
                          <div class="stat-icon tasks">
                            <el-icon><List /></el-icon>
                          </div>
                          <div class="stat-content">
                            <div class="stat-number">{{ activityStats.tasksCreated }}</div>
                            <div class="stat-title">创建任务</div>
                          </div>
                        </div>
                      </el-col>
                      
                      <el-col :span="6">
                        <div class="stat-card">
                          <div class="stat-icon crawlers">
                            <el-icon><Setting /></el-icon>
                          </div>
                          <div class="stat-content">
                            <div class="stat-number">{{ activityStats.crawlersConfigured }}</div>
                            <div class="stat-title">配置爬虫</div>
                          </div>
                        </div>
                      </el-col>
                      
                      <el-col :span="6">
                        <div class="stat-card">
                          <div class="stat-icon data">
                            <el-icon><DataBoard /></el-icon>
                          </div>
                          <div class="stat-content">
                            <div class="stat-number">{{ formatNumber(activityStats.dataExtracted) }}</div>
                            <div class="stat-title">提取数据</div>
                          </div>
                        </div>
                      </el-col>
                      
                      <el-col :span="6">
                        <div class="stat-card">
                          <div class="stat-icon time">
                            <el-icon><Timer /></el-icon>
                          </div>
                          <div class="stat-content">
                            <div class="stat-number">{{ formatDuration(activityStats.totalTime) }}</div>
                            <div class="stat-title">在线时长</div>
                          </div>
                        </div>
                      </el-col>
                    </el-row>
                    
                    <!-- 活动图表 -->
                    <div class="activity-chart">
                      <div ref="activityChartRef" style="width: 100%; height: 300px;"></div>
                    </div>
                  </div>
                </el-card>
              </el-tab-pane>
              
              <!-- 最近任务 -->
              <el-tab-pane label="最近任务" name="tasks">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <el-icon><List /></el-icon>
                      <span>最近任务</span>
                      <div class="header-actions">
                        <el-button size="small" @click="viewAllTasks">
                          查看全部
                        </el-button>
                      </div>
                    </div>
                  </template>
                  
                  <div class="recent-tasks">
                    <div v-if="recentTasks.length > 0" class="task-list">
                      <div v-for="task in recentTasks" :key="task.id" class="task-item">
                        <div class="task-info">
                          <div class="task-header">
                            <span class="task-name">{{ task.name }}</span>
                            <el-tag :type="getTaskStatusType(task.status)" size="small">
                              {{ getTaskStatusText(task.status) }}
                            </el-tag>
                          </div>
                          <div class="task-meta">
                            <span class="task-crawler">{{ task.crawlerName }}</span>
                            <span class="task-time">{{ formatDate(task.createdAt) }}</span>
                          </div>
                          <div v-if="task.progress !== undefined" class="task-progress">
                            <el-progress :percentage="task.progress" :stroke-width="6" />
                          </div>
                        </div>
                        <div class="task-actions">
                          <el-button size="small" type="primary" link @click="viewTask(task.id)">
                            查看详情
                          </el-button>
                        </div>
                      </div>
                    </div>
                    <el-empty v-else description="暂无最近任务" :image-size="100" />
                  </div>
                </el-card>
              </el-tab-pane>
              
              <!-- 安全信息 -->
              <el-tab-pane label="安全信息" name="security">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <el-icon><Lock /></el-icon>
                      <span>安全信息</span>
                    </div>
                  </template>
                  
                  <div class="security-info">
                    <div class="security-item">
                      <div class="security-header">
                        <el-icon><Key /></el-icon>
                        <span class="security-title">密码安全</span>
                        <el-tag type="success" size="small">安全</el-tag>
                      </div>
                      <p class="security-description">上次修改时间：{{ formatDate(userProfile.passwordUpdatedAt) }}</p>
                      <el-button size="small" @click="changePassword">修改密码</el-button>
                    </div>
                    
                    <el-divider />
                    
                    <div class="security-item">
                      <div class="security-header">
                        <el-icon><Lock /></el-icon>
                        <span class="security-title">双因子认证</span>
                        <el-tag v-if="userProfile.twoFactorEnabled" type="success" size="small">已启用</el-tag>
                        <el-tag v-else type="warning" size="small">未启用</el-tag>
                      </div>
                      <p class="security-description">
                        {{ userProfile.twoFactorEnabled ? '您的账户已启用双因子认证保护' : '建议启用双因子认证以提高账户安全性' }}
                      </p>
                      <el-button size="small" @click="manageTwoFactor">
                        {{ userProfile.twoFactorEnabled ? '管理设置' : '立即启用' }}
                      </el-button>
                    </div>
                    
                    <el-divider />
                    
                    <div class="security-item">
                      <div class="security-header">
                        <el-icon><Monitor /></el-icon>
                        <span class="security-title">登录设备</span>
                        <span class="device-count">{{ loginDevices.length }} 台设备</span>
                      </div>
                      <p class="security-description">管理已登录的设备和会话</p>
                      <el-button size="small" @click="manageDevices">管理设备</el-button>
                    </div>
                  </div>
                </el-card>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  User,
  Edit,
  Download,
  Message,
  Phone,
  Location,
  Link,
  Calendar,
  Clock,
  Document,
  TrendCharts,
  List,
  Setting,
  DataBoard,
  Timer,
  Lock,
  Key,
  Monitor
} from '@element-plus/icons-vue'

interface UserProfile {
  id: string
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
  onlineStatus: 'online' | 'offline' | 'away'
  twoFactorEnabled: boolean
  createdAt: string
  lastLoginAt: string
  passwordUpdatedAt: string
}

interface UserStats {
  totalTasks: number
  completedTasks: number
  successRate: number
}

interface ActivityStats {
  tasksCreated: number
  crawlersConfigured: number
  dataExtracted: number
  totalTime: number
}

interface RecentTask {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  crawlerName: string
  createdAt: string
  progress?: number
}

interface LoginDevice {
  id: string
  name: string
  type: string
  location: string
  lastActive: string
  current: boolean
}

// 路由
const router = useRouter()

// 响应式数据
const activeTab = ref('bio')
const activityPeriod = ref('30d')
const activityChartRef = ref<HTMLDivElement>()

// 用户资料
const userProfile = reactive<UserProfile>({
  id: '1',
  username: 'admin',
  email: 'admin@example.com',
  emailVerified: true,
  realName: '管理员',
  phone: '13800138000',
  phoneVerified: false,
  company: 'ContentFlow AI',
  position: '系统管理员',
  bio: '专注于智能内容采集与处理技术，致力于为用户提供高效、稳定的数据采集解决方案。拥有丰富的系统架构设计和项目管理经验。',
  website: 'https://contentflow.ai',
  location: ['中国', '北京市', '朝阳区'],
  avatar: '',
  onlineStatus: 'online',
  twoFactorEnabled: false,
  createdAt: '2024-01-15T08:30:00Z',
  lastLoginAt: '2024-12-20T14:30:00Z',
  passwordUpdatedAt: '2024-11-15T10:20:00Z'
})

// 用户统计
const userStats = reactive<UserStats>({
  totalTasks: 156,
  completedTasks: 142,
  successRate: 91
})

// 活动统计
const activityStats = reactive<ActivityStats>({
  tasksCreated: 23,
  crawlersConfigured: 8,
  dataExtracted: 125000,
  totalTime: 86400 // 秒
})

// 最近任务
const recentTasks = ref<RecentTask[]>([
  {
    id: '1',
    name: '电商产品信息采集',
    status: 'completed',
    crawlerName: '淘宝商品爬虫',
    createdAt: '2024-12-20T10:30:00Z'
  },
  {
    id: '2',
    name: '新闻资讯抓取',
    status: 'running',
    crawlerName: '新浪新闻爬虫',
    createdAt: '2024-12-20T09:15:00Z',
    progress: 65
  },
  {
    id: '3',
    name: '股票数据监控',
    status: 'failed',
    crawlerName: '东方财富爬虫',
    createdAt: '2024-12-19T16:45:00Z'
  },
  {
    id: '4',
    name: '招聘信息收集',
    status: 'pending',
    crawlerName: '智联招聘爬虫',
    createdAt: '2024-12-19T14:20:00Z'
  }
])

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

// 方法
const getStatusText = (status: string) => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    away: '离开'
  }
  return statusMap[status as keyof typeof statusMap] || '未知'
}

const formatLocation = (location: string[]) => {
  return location.length > 0 ? location.join(' ') : '未设置'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return num.toString()
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  return `${hours}h`
}

const getTaskStatusType = (status: string) => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

const getTaskStatusText = (status: string) => {
  const textMap = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status as keyof typeof textMap] || '未知'
}

const editProfile = () => {
  router.push('/settings/user')
}

const exportProfile = () => {
  // 导出个人资料逻辑
  const profileData = {
    ...userProfile,
    stats: userStats,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(profileData, null, 2)], {
    type: 'application/json'
  })
  
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `profile_${userProfile.username}_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success('个人资料导出成功')
}

const viewAllTasks = () => {
  router.push('/task/list')
}

const viewTask = (taskId: string) => {
  router.push(`/task/monitor?id=${taskId}`)
}

const changePassword = () => {
  router.push('/settings/user?section=security')
}

const manageTwoFactor = () => {
  router.push('/settings/user?section=security')
}

const manageDevices = () => {
  router.push('/settings/user?section=sessions')
}

const initActivityChart = () => {
  if (!activityChartRef.value) return
  
  const chart = echarts.init(activityChartRef.value)
  
  const option = {
    title: {
      text: '活动趋势',
      left: 'left',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['任务创建', '数据提取'],
      right: 'right'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['12-14', '12-15', '12-16', '12-17', '12-18', '12-19', '12-20']
    },
    yAxis: [
      {
        type: 'value',
        name: '任务数',
        position: 'left'
      },
      {
        type: 'value',
        name: '数据量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '任务创建',
        type: 'line',
        smooth: true,
        data: [2, 5, 3, 8, 4, 6, 3],
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '数据提取',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: [1200, 2800, 1800, 4200, 2100, 3500, 1800],
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 生命周期
onMounted(async () => {
  // 加载用户数据
  // 这里可以从API加载实际的用户数据
  
  // 初始化图表
  await nextTick()
  if (activeTab.value === 'activity') {
    initActivityChart()
  }
})

// 监听标签页切换
const handleTabChange = async (tabName: string) => {
  if (tabName === 'activity') {
    await nextTick()
    initActivityChart()
  }
}
</script>

<style lang="scss" scoped>
.profile-container {
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
  
  .profile-content {
    .profile-card {
      .profile-header {
        text-align: center;
        
        .avatar-section {
          margin-bottom: 20px;
          
          .user-avatar {
            border: 4px solid var(--el-border-color-light);
            margin-bottom: 12px;
          }
          
          .status-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            
            .status-dot {
              width: 8px;
              height: 8px;
              border-radius: 50%;
            }
            
            .status-text {
              font-size: 12px;
              color: var(--el-text-color-secondary);
            }
            
            &.online .status-dot {
              background-color: #67C23A;
            }
            
            &.offline .status-dot {
              background-color: #909399;
            }
            
            &.away .status-dot {
              background-color: #E6A23C;
            }
          }
        }
        
        .profile-info {
          .username {
            font-size: 20px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin: 0 0 8px 0;
          }
          
          .user-title {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin: 0 0 4px 0;
          }
          
          .user-company {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin: 0 0 20px 0;
          }
          
          .user-stats {
            display: flex;
            justify-content: space-around;
            
            .stat-item {
              text-align: center;
              
              .stat-value {
                display: block;
                font-size: 18px;
                font-weight: 600;
                color: var(--el-color-primary);
                margin-bottom: 4px;
              }
              
              .stat-label {
                font-size: 12px;
                color: var(--el-text-color-secondary);
              }
            }
          }
        }
      }
      
      .profile-details {
        .detail-item {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
          
          .el-icon {
            color: var(--el-text-color-secondary);
            font-size: 16px;
          }
          
          .detail-label {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            min-width: 60px;
          }
          
          .detail-value {
            font-size: 14px;
            color: var(--el-text-color-primary);
            flex: 1;
          }
          
          .detail-link {
            font-size: 14px;
            color: var(--el-color-primary);
            text-decoration: none;
            flex: 1;
            
            &:hover {
              text-decoration: underline;
            }
          }
        }
      }
    }
    
    .profile-tabs {
      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        
        > div:first-child {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
        }
      }
      
      .bio-content {
        .bio-text {
          font-size: 14px;
          line-height: 1.6;
          color: var(--el-text-color-primary);
          margin: 0;
        }
      }
      
      .activity-stats {
        .stats-cards {
          margin-bottom: 24px;
          
          .stat-card {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 20px;
            background: var(--el-bg-color-page);
            border-radius: 8px;
            border: 1px solid var(--el-border-color-light);
            
            .stat-icon {
              width: 48px;
              height: 48px;
              border-radius: 8px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 24px;
              color: white;
              
              &.tasks {
                background: linear-gradient(135deg, #409EFF, #66B1FF);
              }
              
              &.crawlers {
                background: linear-gradient(135deg, #67C23A, #85CE61);
              }
              
              &.data {
                background: linear-gradient(135deg, #E6A23C, #EEBC5B);
              }
              
              &.time {
                background: linear-gradient(135deg, #F56C6C, #F78989);
              }
            }
            
            .stat-content {
              .stat-number {
                font-size: 24px;
                font-weight: 600;
                color: var(--el-text-color-primary);
                margin-bottom: 4px;
              }
              
              .stat-title {
                font-size: 14px;
                color: var(--el-text-color-secondary);
              }
            }
          }
        }
        
        .activity-chart {
          margin-top: 24px;
        }
      }
      
      .recent-tasks {
        .task-list {
          .task-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            border: 1px solid var(--el-border-color-light);
            border-radius: 8px;
            margin-bottom: 12px;
            
            .task-info {
              flex: 1;
              
              .task-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 8px;
                
                .task-name {
                  font-weight: 500;
                  color: var(--el-text-color-primary);
                }
              }
              
              .task-meta {
                display: flex;
                gap: 16px;
                margin-bottom: 8px;
                
                .task-crawler,
                .task-time {
                  font-size: 12px;
                  color: var(--el-text-color-secondary);
                }
              }
              
              .task-progress {
                max-width: 200px;
              }
            }
          }
        }
      }
      
      .security-info {
        .security-item {
          margin-bottom: 24px;
          
          .security-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            
            .security-title {
              font-weight: 500;
              color: var(--el-text-color-primary);
              flex: 1;
            }
            
            .device-count {
              font-size: 12px;
              color: var(--el-text-color-secondary);
            }
          }
          
          .security-description {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin: 0 0 12px 0;
          }
        }
      }
    }
  }
}
</style>