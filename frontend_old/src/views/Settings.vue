<template>
  <div class="settings-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>系统设置</h1>
        <p>配置系统参数和用户偏好</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="saveAllSettings">
          <i class="fas fa-save"></i>
          保存所有设置
        </el-button>
      </div>
    </div>

    <!-- 设置选项卡 -->
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基础设置 -->
      <el-tab-pane label="基础设置" name="basic">
        <div class="settings-section">
          <h3>系统配置</h3>
          <el-form :model="basicSettings" label-width="150px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" style="width: 300px" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input
                v-model="basicSettings.systemDescription"
                type="textarea"
                :rows="3"
                style="width: 400px"
              />
            </el-form-item>
            <el-form-item label="默认语言">
              <el-select v-model="basicSettings.defaultLanguage" style="width: 200px">
                <el-option label="中文" value="zh-CN"></el-option>
                <el-option label="English" value="en-US"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="时区">
              <el-select v-model="basicSettings.timezone" style="width: 200px">
                <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai"></el-option>
                <el-option label="UTC" value="UTC"></el-option>
                <el-option label="纽约时间 (UTC-5)" value="America/New_York"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="自动备份">
              <el-switch v-model="basicSettings.autoBackup" />
              <span class="setting-desc">每日自动备份系统数据</span>
            </el-form-item>
            <el-form-item label="调试模式">
              <el-switch v-model="basicSettings.debugMode" />
              <span class="setting-desc">启用详细日志记录</span>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 爬虫设置 -->
      <el-tab-pane label="爬虫设置" name="crawler">
        <div class="settings-section">
          <h3>爬虫配置</h3>
          <el-form :model="crawlerSettings" label-width="150px">
            <el-form-item label="并发数量">
              <el-input-number
                v-model="crawlerSettings.concurrency"
                :min="1"
                :max="20"
                style="width: 200px"
              />
              <span class="setting-desc">同时运行的爬虫任务数量</span>
            </el-form-item>
            <el-form-item label="请求间隔">
              <el-input-number
                v-model="crawlerSettings.requestDelay"
                :min="100"
                :max="10000"
                :step="100"
                style="width: 200px"
              />
              <span class="setting-desc">请求间隔时间（毫秒）</span>
            </el-form-item>
            <el-form-item label="超时时间">
              <el-input-number
                v-model="crawlerSettings.timeout"
                :min="5"
                :max="300"
                style="width: 200px"
              />
              <span class="setting-desc">请求超时时间（秒）</span>
            </el-form-item>
            <el-form-item label="重试次数">
              <el-input-number
                v-model="crawlerSettings.retryCount"
                :min="0"
                :max="10"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="User-Agent">
              <el-input
                v-model="crawlerSettings.userAgent"
                style="width: 500px"
                placeholder="请输入User-Agent字符串"
              />
            </el-form-item>
            <el-form-item label="代理设置">
              <el-switch v-model="crawlerSettings.useProxy" />
              <span class="setting-desc">启用代理服务器</span>
            </el-form-item>
            <el-form-item v-if="crawlerSettings.useProxy" label="代理地址">
              <el-input
                v-model="crawlerSettings.proxyUrl"
                style="width: 300px"
                placeholder="http://proxy.example.com:8080"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>



      <!-- 通知设置 -->
      <el-tab-pane label="通知设置" name="notification">
        <div class="settings-section">
          <h3>通知配置</h3>
          <el-form :model="notificationSettings" label-width="150px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.emailEnabled" />
            </el-form-item>
            <el-form-item v-if="notificationSettings.emailEnabled" label="邮箱地址">
              <el-input
                v-model="notificationSettings.emailAddress"
                style="width: 300px"
                placeholder="请输入邮箱地址"
              />
            </el-form-item>
            <el-form-item v-if="notificationSettings.emailEnabled" label="SMTP服务器">
              <el-input
                v-model="notificationSettings.smtpServer"
                style="width: 300px"
                placeholder="smtp.example.com"
              />
            </el-form-item>
            <el-form-item label="微信通知">
              <el-switch v-model="notificationSettings.wechatEnabled" />
            </el-form-item>
            <el-form-item label="钉钉通知">
              <el-switch v-model="notificationSettings.dingdingEnabled" />
            </el-form-item>
            <el-form-item label="通知类型">
              <el-checkbox-group v-model="notificationSettings.notificationTypes">
                <el-checkbox label="task_complete">任务完成</el-checkbox>
                <el-checkbox label="task_failed">任务失败</el-checkbox>
                <el-checkbox label="system_error">系统错误</el-checkbox>
                <el-checkbox label="daily_report">日报</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 安全设置 -->
      <el-tab-pane label="安全设置" name="security">
        <div class="settings-section">
          <h3>安全配置</h3>
          <el-form :model="securitySettings" label-width="150px">
            <el-form-item label="登录超时">
              <el-input-number
                v-model="securitySettings.sessionTimeout"
                :min="30"
                :max="1440"
                style="width: 200px"
              />
              <span class="setting-desc">会话超时时间（分钟）</span>
            </el-form-item>
            <el-form-item label="密码强度">
              <el-select v-model="securitySettings.passwordStrength" style="width: 200px">
                <el-option label="低" value="low"></el-option>
                <el-option label="中" value="medium"></el-option>
                <el-option label="高" value="high"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="双因子认证">
              <el-switch v-model="securitySettings.twoFactorAuth" />
            </el-form-item>
            <el-form-item label="IP白名单">
              <el-switch v-model="securitySettings.ipWhitelist" />
            </el-form-item>
            <el-form-item v-if="securitySettings.ipWhitelist" label="允许的IP">
              <el-input
                v-model="securitySettings.allowedIps"
                type="textarea"
                :rows="3"
                style="width: 400px"
                placeholder="每行一个IP地址或IP段"
              />
            </el-form-item>
            <el-form-item label="API访问限制">
              <el-input-number
                v-model="securitySettings.apiRateLimit"
                :min="10"
                :max="10000"
                style="width: 200px"
              />
              <span class="setting-desc">每分钟最大请求数</span>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 存储设置 -->
      <el-tab-pane label="存储设置" name="storage">
        <div class="settings-section">
          <h3>存储配置</h3>
          <el-form :model="storageSettings" label-width="150px">
            <el-form-item label="存储类型">
              <el-select v-model="storageSettings.storageType" style="width: 200px">
                <el-option label="本地存储" value="local"></el-option>
                <el-option label="阿里云OSS" value="aliyun"></el-option>
                <el-option label="腾讯云COS" value="tencent"></el-option>
                <el-option label="AWS S3" value="aws"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="存储路径">
              <el-input
                v-model="storageSettings.storagePath"
                style="width: 400px"
                placeholder="/data/crawler"
              />
            </el-form-item>
            <el-form-item label="最大存储">
              <el-input-number
                v-model="storageSettings.maxStorage"
                :min="1"
                :max="1000"
                style="width: 200px"
              />
              <span class="setting-desc">最大存储空间（GB）</span>
            </el-form-item>
            <el-form-item label="自动清理">
              <el-switch v-model="storageSettings.autoCleanup" />
              <span class="setting-desc">自动清理过期文件</span>
            </el-form-item>
            <el-form-item v-if="storageSettings.autoCleanup" label="保留天数">
              <el-input-number
                v-model="storageSettings.retentionDays"
                :min="1"
                :max="365"
                style="width: 200px"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

// 基础设置
const basicSettings = ref({
  systemName: '智能爬虫内容管理系统',
  systemDescription: '基于AI的智能爬虫和内容生成平台',
  defaultLanguage: 'zh-CN',
  timezone: 'Asia/Shanghai',
  autoBackup: true,
  debugMode: false
})

// 爬虫设置
const crawlerSettings = ref({
  concurrency: 5,
  requestDelay: 1000,
  timeout: 30,
  retryCount: 3,
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  useProxy: false,
  proxyUrl: ''
})



// 通知设置
const notificationSettings = ref({
  emailEnabled: false,
  emailAddress: '',
  smtpServer: '',
  wechatEnabled: false,
  dingdingEnabled: false,
  notificationTypes: ['task_complete', 'system_error']
})

// 安全设置
const securitySettings = ref({
  sessionTimeout: 120,
  passwordStrength: 'medium',
  twoFactorAuth: false,
  ipWhitelist: false,
  allowedIps: '',
  apiRateLimit: 1000
})

// 存储设置
const storageSettings = ref({
  storageType: 'local',
  storagePath: '/data/crawler',
  maxStorage: 100,
  autoCleanup: true,
  retentionDays: 30
})

const saveAllSettings = () => {
  // 模拟保存设置
  ElMessage.success('设置保存成功')
}
</script>

<style lang="scss" scoped>
.settings-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
    }
  }
}

.settings-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 24px;
  }
  
  :deep(.el-tabs__nav-wrap) {
    background: var(--bg-primary);
    border-radius: 8px;
    padding: 4px;
  }
  
  :deep(.el-tabs__item) {
    border-radius: 6px;
    margin-right: 4px;
    
    &.is-active {
      background: var(--primary-color);
      color: white;
    }
  }
}

.settings-section {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
  
  h3 {
    margin: 0 0 20px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-light);
  }
  
  .setting-desc {
    margin-left: 12px;
    font-size: 12px;
    color: var(--text-secondary);
  }
  
  :deep(.el-form-item) {
    margin-bottom: 20px;
    
    .el-form-item__label {
      color: var(--text-primary);
      font-weight: 500;
    }
  }
  
  :deep(.el-checkbox-group) {
    .el-checkbox {
      margin-right: 20px;
      margin-bottom: 8px;
    }
  }
}
</style>