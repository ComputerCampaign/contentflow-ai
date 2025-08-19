<template>
  <div class="system-settings-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统设置</h1>
        <p class="page-description">配置系统运行参数和全局设置</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="resetToDefault" type="danger" plain>
            <el-icon><RefreshLeft /></el-icon>
            恢复默认
          </el-button>
          <el-button @click="exportConfig" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出配置
          </el-button>
          <el-button @click="importConfig">
            <el-icon><Upload /></el-icon>
            导入配置
          </el-button>
          <el-button type="primary" @click="saveSettings" :loading="saving">
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
              <el-menu-item index="general">
                <el-icon><Setting /></el-icon>
                <span>常规设置</span>
              </el-menu-item>
              <el-menu-item index="performance">
                <el-icon><Monitor /></el-icon>
                <span>性能配置</span>
              </el-menu-item>
              <el-menu-item index="security">
                <el-icon><Lock /></el-icon>
                <span>安全设置</span>
              </el-menu-item>
              <el-menu-item index="notification">
                <el-icon><Bell /></el-icon>
                <span>通知配置</span>
              </el-menu-item>
              <el-menu-item index="storage">
                <el-icon><FolderOpened /></el-icon>
                <span>存储配置</span>
              </el-menu-item>
              <el-menu-item index="logging">
                <el-icon><Document /></el-icon>
                <span>日志配置</span>
              </el-menu-item>
              <el-menu-item index="backup">
                <el-icon><Files /></el-icon>
                <span>备份设置</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>
        
        <!-- 右侧设置面板 -->
        <el-col :span="18">
          <div class="settings-panel">
            <!-- 常规设置 -->
            <el-card v-show="activeSection === 'general'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Setting /></el-icon>
                  <span>常规设置</span>
                </div>
              </template>
              
              <el-form :model="settings.general" label-width="140px">
                <el-form-item label="系统名称">
                  <el-input v-model="settings.general.systemName" placeholder="请输入系统名称" />
                </el-form-item>
                
                <el-form-item label="系统描述">
                  <el-input
                    v-model="settings.general.systemDescription"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入系统描述"
                  />
                </el-form-item>
                
                <el-form-item label="默认语言">
                  <el-select v-model="settings.general.defaultLanguage" style="width: 200px;">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                    <el-option label="日本語" value="ja-JP" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="时区设置">
                  <el-select v-model="settings.general.timezone" style="width: 200px;">
                    <el-option label="Asia/Shanghai" value="Asia/Shanghai" />
                    <el-option label="UTC" value="UTC" />
                    <el-option label="America/New_York" value="America/New_York" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="日期格式">
                  <el-select v-model="settings.general.dateFormat" style="width: 200px;">
                    <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
                    <el-option label="MM/DD/YYYY" value="MM/DD/YYYY" />
                    <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="启用维护模式">
                  <el-switch v-model="settings.general.maintenanceMode" />
                  <span class="form-item-tip">启用后，系统将显示维护页面</span>
                </el-form-item>
                
                <el-form-item label="允许用户注册">
                  <el-switch v-model="settings.general.allowRegistration" />
                  <span class="form-item-tip">关闭后，新用户无法注册账号</span>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 性能配置 -->
            <el-card v-show="activeSection === 'performance'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Monitor /></el-icon>
                  <span>性能配置</span>
                </div>
              </template>
              
              <el-form :model="settings.performance" label-width="140px">
                <el-form-item label="最大并发任务数">
                  <el-input-number
                    v-model="settings.performance.maxConcurrentTasks"
                    :min="1"
                    :max="100"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">同时运行的最大任务数量</span>
                </el-form-item>
                
                <el-form-item label="任务队列大小">
                  <el-input-number
                    v-model="settings.performance.taskQueueSize"
                    :min="10"
                    :max="10000"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">任务队列的最大容量</span>
                </el-form-item>
                
                <el-form-item label="请求超时时间">
                  <el-input-number
                    v-model="settings.performance.requestTimeout"
                    :min="1000"
                    :max="300000"
                    :step="1000"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">HTTP请求超时时间（毫秒）</span>
                </el-form-item>
                
                <el-form-item label="重试次数">
                  <el-input-number
                    v-model="settings.performance.retryCount"
                    :min="0"
                    :max="10"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">请求失败时的重试次数</span>
                </el-form-item>
                
                <el-form-item label="缓存过期时间">
                  <el-input-number
                    v-model="settings.performance.cacheExpiration"
                    :min="60"
                    :max="86400"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">缓存数据的过期时间（秒）</span>
                </el-form-item>
                
                <el-form-item label="启用数据压缩">
                  <el-switch v-model="settings.performance.enableCompression" />
                  <span class="form-item-tip">启用HTTP响应压缩</span>
                </el-form-item>
                
                <el-form-item label="启用缓存">
                  <el-switch v-model="settings.performance.enableCache" />
                  <span class="form-item-tip">启用数据缓存功能</span>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 安全设置 -->
            <el-card v-show="activeSection === 'security'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Lock /></el-icon>
                  <span>安全设置</span>
                </div>
              </template>
              
              <el-form :model="settings.security" label-width="140px">
                <el-form-item label="密码最小长度">
                  <el-input-number
                    v-model="settings.security.minPasswordLength"
                    :min="6"
                    :max="32"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">用户密码的最小长度</span>
                </el-form-item>
                
                <el-form-item label="密码复杂度">
                  <el-checkbox-group v-model="settings.security.passwordComplexity">
                    <el-checkbox label="uppercase">包含大写字母</el-checkbox>
                    <el-checkbox label="lowercase">包含小写字母</el-checkbox>
                    <el-checkbox label="numbers">包含数字</el-checkbox>
                    <el-checkbox label="symbols">包含特殊字符</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                
                <el-form-item label="会话超时时间">
                  <el-input-number
                    v-model="settings.security.sessionTimeout"
                    :min="300"
                    :max="86400"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">用户会话的超时时间（秒）</span>
                </el-form-item>
                
                <el-form-item label="最大登录尝试">
                  <el-input-number
                    v-model="settings.security.maxLoginAttempts"
                    :min="3"
                    :max="10"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">账号锁定前的最大登录尝试次数</span>
                </el-form-item>
                
                <el-form-item label="账号锁定时间">
                  <el-input-number
                    v-model="settings.security.lockoutDuration"
                    :min="300"
                    :max="3600"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">账号锁定的持续时间（秒）</span>
                </el-form-item>
                
                <el-form-item label="启用双因子认证">
                  <el-switch v-model="settings.security.enableTwoFactor" />
                  <span class="form-item-tip">要求用户启用双因子认证</span>
                </el-form-item>
                
                <el-form-item label="启用IP白名单">
                  <el-switch v-model="settings.security.enableIpWhitelist" />
                  <span class="form-item-tip">只允许白名单IP访问</span>
                </el-form-item>
                
                <el-form-item v-if="settings.security.enableIpWhitelist" label="IP白名单">
                  <el-input
                    v-model="settings.security.ipWhitelist"
                    type="textarea"
                    :rows="3"
                    placeholder="每行一个IP地址或CIDR网段"
                  />
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 通知配置 -->
            <el-card v-show="activeSection === 'notification'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Bell /></el-icon>
                  <span>通知配置</span>
                </div>
              </template>
              
              <el-form :model="settings.notification" label-width="140px">
                <el-form-item label="邮件通知">
                  <el-switch v-model="settings.notification.enableEmail" />
                  <span class="form-item-tip">启用邮件通知功能</span>
                </el-form-item>
                
                <div v-if="settings.notification.enableEmail" class="email-config">
                  <el-form-item label="SMTP服务器">
                    <el-input v-model="settings.notification.smtpHost" placeholder="smtp.example.com" />
                  </el-form-item>
                  
                  <el-form-item label="SMTP端口">
                    <el-input-number
                      v-model="settings.notification.smtpPort"
                      :min="1"
                      :max="65535"
                      style="width: 200px;"
                    />
                  </el-form-item>
                  
                  <el-form-item label="发送邮箱">
                    <el-input v-model="settings.notification.smtpUser" placeholder="noreply@example.com" />
                  </el-form-item>
                  
                  <el-form-item label="邮箱密码">
                    <el-input
                      v-model="settings.notification.smtpPassword"
                      type="password"
                      placeholder="请输入邮箱密码或授权码"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item label="启用SSL">
                    <el-switch v-model="settings.notification.smtpSsl" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button @click="testEmailConfig" :loading="testingEmail">
                      <el-icon><Promotion /></el-icon>
                      测试邮件配置
                    </el-button>
                  </el-form-item>
                </div>
                
                <el-form-item label="Webhook通知">
                  <el-switch v-model="settings.notification.enableWebhook" />
                  <span class="form-item-tip">启用Webhook通知功能</span>
                </el-form-item>
                
                <div v-if="settings.notification.enableWebhook" class="webhook-config">
                  <el-form-item label="Webhook URL">
                    <el-input v-model="settings.notification.webhookUrl" placeholder="https://example.com/webhook" />
                  </el-form-item>
                  
                  <el-form-item label="请求方法">
                    <el-select v-model="settings.notification.webhookMethod" style="width: 120px;">
                      <el-option label="POST" value="POST" />
                      <el-option label="PUT" value="PUT" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="请求头">
                    <el-input
                      v-model="settings.notification.webhookHeaders"
                      type="textarea"
                      :rows="3"
                      placeholder="JSON格式的请求头"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button @click="testWebhookConfig" :loading="testingWebhook">
                      <el-icon><Promotion /></el-icon>
                      测试Webhook配置
                    </el-button>
                  </el-form-item>
                </div>
                
                <el-form-item label="通知事件">
                  <el-checkbox-group v-model="settings.notification.events">
                    <el-checkbox label="task_completed">任务完成</el-checkbox>
                    <el-checkbox label="task_failed">任务失败</el-checkbox>
                    <el-checkbox label="system_error">系统错误</el-checkbox>
                    <el-checkbox label="user_login">用户登录</el-checkbox>
                    <el-checkbox label="config_changed">配置变更</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 存储配置 -->
            <el-card v-show="activeSection === 'storage'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><FolderOpened /></el-icon>
                  <span>存储配置</span>
                </div>
              </template>
              
              <el-form :model="settings.storage" label-width="140px">
                <el-form-item label="数据存储路径">
                  <el-input v-model="settings.storage.dataPath" placeholder="/var/lib/contentflow" />
                  <span class="form-item-tip">系统数据的存储路径</span>
                </el-form-item>
                
                <el-form-item label="日志存储路径">
                  <el-input v-model="settings.storage.logPath" placeholder="/var/log/contentflow" />
                  <span class="form-item-tip">系统日志的存储路径</span>
                </el-form-item>
                
                <el-form-item label="临时文件路径">
                  <el-input v-model="settings.storage.tempPath" placeholder="/tmp/contentflow" />
                  <span class="form-item-tip">临时文件的存储路径</span>
                </el-form-item>
                
                <el-form-item label="最大磁盘使用">
                  <el-input-number
                    v-model="settings.storage.maxDiskUsage"
                    :min="1"
                    :max="100"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">磁盘使用率上限（%）</span>
                </el-form-item>
                
                <el-form-item label="数据保留天数">
                  <el-input-number
                    v-model="settings.storage.dataRetentionDays"
                    :min="1"
                    :max="3650"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">数据自动清理的保留天数</span>
                </el-form-item>
                
                <el-form-item label="启用数据压缩">
                  <el-switch v-model="settings.storage.enableCompression" />
                  <span class="form-item-tip">压缩存储的数据文件</span>
                </el-form-item>
                
                <el-form-item label="启用自动清理">
                  <el-switch v-model="settings.storage.enableAutoCleanup" />
                  <span class="form-item-tip">自动清理过期数据</span>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 日志配置 -->
            <el-card v-show="activeSection === 'logging'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Document /></el-icon>
                  <span>日志配置</span>
                </div>
              </template>
              
              <el-form :model="settings.logging" label-width="140px">
                <el-form-item label="日志级别">
                  <el-select v-model="settings.logging.level" style="width: 200px;">
                    <el-option label="DEBUG" value="DEBUG" />
                    <el-option label="INFO" value="INFO" />
                    <el-option label="WARN" value="WARN" />
                    <el-option label="ERROR" value="ERROR" />
                  </el-select>
                  <span class="form-item-tip">系统日志的记录级别</span>
                </el-form-item>
                
                <el-form-item label="日志格式">
                  <el-select v-model="settings.logging.format" style="width: 200px;">
                    <el-option label="JSON" value="json" />
                    <el-option label="文本" value="text" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="单个日志文件大小">
                  <el-input-number
                    v-model="settings.logging.maxFileSize"
                    :min="1"
                    :max="1000"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">单个日志文件的最大大小（MB）</span>
                </el-form-item>
                
                <el-form-item label="日志文件数量">
                  <el-input-number
                    v-model="settings.logging.maxFiles"
                    :min="1"
                    :max="100"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">保留的日志文件数量</span>
                </el-form-item>
                
                <el-form-item label="启用访问日志">
                  <el-switch v-model="settings.logging.enableAccessLog" />
                  <span class="form-item-tip">记录HTTP访问日志</span>
                </el-form-item>
                
                <el-form-item label="启用错误日志">
                  <el-switch v-model="settings.logging.enableErrorLog" />
                  <span class="form-item-tip">记录系统错误日志</span>
                </el-form-item>
                
                <el-form-item label="启用审计日志">
                  <el-switch v-model="settings.logging.enableAuditLog" />
                  <span class="form-item-tip">记录用户操作审计日志</span>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 备份设置 -->
            <el-card v-show="activeSection === 'backup'" class="setting-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Files /></el-icon>
                  <span>备份设置</span>
                </div>
              </template>
              
              <el-form :model="settings.backup" label-width="140px">
                <el-form-item label="启用自动备份">
                  <el-switch v-model="settings.backup.enableAutoBackup" />
                  <span class="form-item-tip">定期自动备份系统数据</span>
                </el-form-item>
                
                <div v-if="settings.backup.enableAutoBackup" class="backup-config">
                  <el-form-item label="备份频率">
                    <el-select v-model="settings.backup.frequency" style="width: 200px;">
                      <el-option label="每小时" value="hourly" />
                      <el-option label="每天" value="daily" />
                      <el-option label="每周" value="weekly" />
                      <el-option label="每月" value="monthly" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="备份时间">
                    <el-time-picker
                      v-model="settings.backup.backupTime"
                      format="HH:mm"
                      value-format="HH:mm"
                      placeholder="选择备份时间"
                    />
                  </el-form-item>
                </div>
                
                <el-form-item label="备份存储路径">
                  <el-input v-model="settings.backup.backupPath" placeholder="/var/backups/contentflow" />
                  <span class="form-item-tip">备份文件的存储路径</span>
                </el-form-item>
                
                <el-form-item label="保留备份数量">
                  <el-input-number
                    v-model="settings.backup.retentionCount"
                    :min="1"
                    :max="100"
                    style="width: 200px;"
                  />
                  <span class="form-item-tip">保留的备份文件数量</span>
                </el-form-item>
                
                <el-form-item label="启用压缩">
                  <el-switch v-model="settings.backup.enableCompression" />
                  <span class="form-item-tip">压缩备份文件以节省空间</span>
                </el-form-item>
                
                <el-form-item label="备份内容">
                  <el-checkbox-group v-model="settings.backup.backupContent">
                    <el-checkbox label="database">数据库</el-checkbox>
                    <el-checkbox label="config">配置文件</el-checkbox>
                    <el-checkbox label="logs">日志文件</el-checkbox>
                    <el-checkbox label="uploads">上传文件</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                
                <el-form-item>
                  <el-button @click="createBackup" :loading="creatingBackup">
                    <el-icon><Files /></el-icon>
                    立即备份
                  </el-button>
                  <el-button @click="restoreBackup">
                    <el-icon><RefreshLeft /></el-icon>
                    恢复备份
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 导入配置对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入配置"
      width="600px"
      :before-close="handleImportClose"
    >
      <div class="import-config">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="false"
          accept=".json"
          :on-change="handleFileChange"
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>
            选择配置文件
          </el-button>
        </el-upload>
        
        <div v-if="importFile" class="file-info">
          <p>已选择文件: {{ importFile.name }}</p>
          <p>文件大小: {{ formatFileSize(importFile.size) }}</p>
        </div>
        
        <el-divider>或</el-divider>
        
        <el-input
          v-model="importConfigText"
          type="textarea"
          :rows="10"
          placeholder="粘贴配置JSON内容"
        />
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmImport" :loading="importing">
            导入配置
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 恢复备份对话框 -->
    <el-dialog
      v-model="restoreDialogVisible"
      title="恢复备份"
      width="800px"
      :before-close="handleRestoreClose"
    >
      <div class="restore-backup">
        <el-table :data="backupList" stripe>
          <el-table-column prop="filename" label="备份文件" min-width="200" />
          <el-table-column prop="size" label="文件大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column prop="type" label="备份类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getBackupTypeTag(row.type)" size="small">
                {{ getBackupTypeName(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="selectBackup(row)">
                选择
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="selectedBackup" class="selected-backup">
          <el-alert
            :title="`已选择备份: ${selectedBackup.filename}`"
            type="info"
            :closable="false"
            show-icon
          />
          
          <el-checkbox-group v-model="restoreContent" style="margin-top: 16px;">
            <el-checkbox label="database">恢复数据库</el-checkbox>
            <el-checkbox label="config">恢复配置文件</el-checkbox>
            <el-checkbox label="logs">恢复日志文件</el-checkbox>
            <el-checkbox label="uploads">恢复上传文件</el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="restoreDialogVisible = false">取消</el-button>
          <el-button
            type="danger"
            @click="confirmRestore"
            :loading="restoring"
            :disabled="!selectedBackup"
          >
            确认恢复
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Monitor,
  Lock,
  Bell,
  FolderOpened,
  Document,
  Files,
  RefreshLeft,
  Download,
  Upload,
  Check,
  Promotion
} from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'

interface SystemSettings {
  general: {
    systemName: string
    systemDescription: string
    defaultLanguage: string
    timezone: string
    dateFormat: string
    maintenanceMode: boolean
    allowRegistration: boolean
  }
  performance: {
    maxConcurrentTasks: number
    taskQueueSize: number
    requestTimeout: number
    retryCount: number
    cacheExpiration: number
    enableCompression: boolean
    enableCache: boolean
  }
  security: {
    minPasswordLength: number
    passwordComplexity: string[]
    sessionTimeout: number
    maxLoginAttempts: number
    lockoutDuration: number
    enableTwoFactor: boolean
    enableIpWhitelist: boolean
    ipWhitelist: string
  }
  notification: {
    enableEmail: boolean
    smtpHost: string
    smtpPort: number
    smtpUser: string
    smtpPassword: string
    smtpSsl: boolean
    enableWebhook: boolean
    webhookUrl: string
    webhookMethod: string
    webhookHeaders: string
    events: string[]
  }
  storage: {
    dataPath: string
    logPath: string
    tempPath: string
    maxDiskUsage: number
    dataRetentionDays: number
    enableCompression: boolean
    enableAutoCleanup: boolean
  }
  logging: {
    level: string
    format: string
    maxFileSize: number
    maxFiles: number
    enableAccessLog: boolean
    enableErrorLog: boolean
    enableAuditLog: boolean
  }
  backup: {
    enableAutoBackup: boolean
    frequency: string
    backupTime: string
    backupPath: string
    retentionCount: number
    enableCompression: boolean
    backupContent: string[]
  }
}

interface BackupFile {
  id: string
  filename: string
  size: number
  createTime: string
  type: string
}

// 响应式数据
const activeSection = ref('general')
const saving = ref(false)
const exporting = ref(false)
const importing = ref(false)
const testingEmail = ref(false)
const testingWebhook = ref(false)
const creatingBackup = ref(false)
const restoring = ref(false)

const importDialogVisible = ref(false)
const restoreDialogVisible = ref(false)
const importFile = ref<File | null>(null)
const importConfigText = ref('')
const selectedBackup = ref<BackupFile | null>(null)
const restoreContent = ref(['database', 'config'])

// 系统设置
const settings = reactive<SystemSettings>({
  general: {
    systemName: 'ContentFlow AI',
    systemDescription: '智能内容采集与处理平台',
    defaultLanguage: 'zh-CN',
    timezone: 'Asia/Shanghai',
    dateFormat: 'YYYY-MM-DD',
    maintenanceMode: false,
    allowRegistration: true
  },
  performance: {
    maxConcurrentTasks: 10,
    taskQueueSize: 1000,
    requestTimeout: 30000,
    retryCount: 3,
    cacheExpiration: 3600,
    enableCompression: true,
    enableCache: true
  },
  security: {
    minPasswordLength: 8,
    passwordComplexity: ['lowercase', 'numbers'],
    sessionTimeout: 3600,
    maxLoginAttempts: 5,
    lockoutDuration: 900,
    enableTwoFactor: false,
    enableIpWhitelist: false,
    ipWhitelist: ''
  },
  notification: {
    enableEmail: false,
    smtpHost: '',
    smtpPort: 587,
    smtpUser: '',
    smtpPassword: '',
    smtpSsl: true,
    enableWebhook: false,
    webhookUrl: '',
    webhookMethod: 'POST',
    webhookHeaders: '',
    events: ['task_completed', 'task_failed', 'system_error']
  },
  storage: {
    dataPath: '/var/lib/contentflow',
    logPath: '/var/log/contentflow',
    tempPath: '/tmp/contentflow',
    maxDiskUsage: 80,
    dataRetentionDays: 30,
    enableCompression: true,
    enableAutoCleanup: true
  },
  logging: {
    level: 'INFO',
    format: 'json',
    maxFileSize: 100,
    maxFiles: 10,
    enableAccessLog: true,
    enableErrorLog: true,
    enableAuditLog: false
  },
  backup: {
    enableAutoBackup: false,
    frequency: 'daily',
    backupTime: '02:00',
    backupPath: '/var/backups/contentflow',
    retentionCount: 7,
    enableCompression: true,
    backupContent: ['database', 'config']
  }
})

// 备份列表
const backupList = ref<BackupFile[]>([])

// 方法
const generateMockBackupList = (): BackupFile[] => {
  const types = ['auto', 'manual', 'scheduled']
  const list: BackupFile[] = []
  
  for (let i = 0; i < 10; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    
    list.push({
      id: `backup_${i}`,
      filename: `contentflow_backup_${date.toISOString().split('T')[0]}.tar.gz`,
      size: Math.floor(Math.random() * 1000000000) + 100000000,
      createTime: date.toISOString(),
      type: types[Math.floor(Math.random() * types.length)]
    })
  }
  
  return list
}

const handleSectionChange = (section: string) => {
  activeSection.value = section
}

const saveSettings = async () => {
  saving.value = true
  
  try {
    // 模拟保存过程
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    ElMessage.success('系统设置保存成功')
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

const resetToDefault = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要恢复所有设置到默认值吗？此操作不可撤销。',
      '确认重置',
      {
        type: 'warning'
      }
    )
    
    // 重置设置到默认值
    Object.assign(settings, {
      general: {
        systemName: 'ContentFlow AI',
        systemDescription: '智能内容采集与处理平台',
        defaultLanguage: 'zh-CN',
        timezone: 'Asia/Shanghai',
        dateFormat: 'YYYY-MM-DD',
        maintenanceMode: false,
        allowRegistration: true
      },
      performance: {
        maxConcurrentTasks: 10,
        taskQueueSize: 1000,
        requestTimeout: 30000,
        retryCount: 3,
        cacheExpiration: 3600,
        enableCompression: true,
        enableCache: true
      },
      security: {
        minPasswordLength: 8,
        passwordComplexity: ['lowercase', 'numbers'],
        sessionTimeout: 3600,
        maxLoginAttempts: 5,
        lockoutDuration: 900,
        enableTwoFactor: false,
        enableIpWhitelist: false,
        ipWhitelist: ''
      },
      notification: {
        enableEmail: false,
        smtpHost: '',
        smtpPort: 587,
        smtpUser: '',
        smtpPassword: '',
        smtpSsl: true,
        enableWebhook: false,
        webhookUrl: '',
        webhookMethod: 'POST',
        webhookHeaders: '',
        events: ['task_completed', 'task_failed', 'system_error']
      },
      storage: {
        dataPath: '/var/lib/contentflow',
        logPath: '/var/log/contentflow',
        tempPath: '/tmp/contentflow',
        maxDiskUsage: 80,
        dataRetentionDays: 30,
        enableCompression: true,
        enableAutoCleanup: true
      },
      logging: {
        level: 'INFO',
        format: 'json',
        maxFileSize: 100,
        maxFiles: 10,
        enableAccessLog: true,
        enableErrorLog: true,
        enableAuditLog: false
      },
      backup: {
        enableAutoBackup: false,
        frequency: 'daily',
        backupTime: '02:00',
        backupPath: '/var/backups/contentflow',
        retentionCount: 7,
        enableCompression: true,
        backupContent: ['database', 'config']
      }
    })
    
    ElMessage.success('设置已恢复到默认值')
  } catch (error) {
    // 用户取消操作
  }
}

const exportConfig = async () => {
  exporting.value = true
  
  try {
    // 模拟导出过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const configData = JSON.stringify(settings, null, 2)
    const blob = new Blob([configData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `contentflow_config_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    URL.revokeObjectURL(url)
    
    ElMessage.success('配置导出成功')
  } catch (error) {
    ElMessage.error('导出配置失败')
  } finally {
    exporting.value = false
  }
}

const importConfig = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    importFile.value = file.raw
    
    const reader = new FileReader()
    reader.onload = (e) => {
      if (e.target?.result) {
        importConfigText.value = e.target.result as string
      }
    }
    reader.readAsText(file.raw)
  }
}

const confirmImport = async () => {
  if (!importConfigText.value.trim()) {
    ElMessage.warning('请选择配置文件或输入配置内容')
    return
  }
  
  importing.value = true
  
  try {
    const configData = JSON.parse(importConfigText.value)
    
    // 验证配置数据结构
    if (!configData.general || !configData.performance) {
      throw new Error('配置文件格式不正确')
    }
    
    // 应用配置
    Object.assign(settings, configData)
    
    ElMessage.success('配置导入成功')
    importDialogVisible.value = false
  } catch (error) {
    ElMessage.error('配置文件格式错误或导入失败')
  } finally {
    importing.value = false
  }
}

const handleImportClose = () => {
  importDialogVisible.value = false
  importFile.value = null
  importConfigText.value = ''
}

const testEmailConfig = async () => {
  if (!settings.notification.smtpHost || !settings.notification.smtpUser) {
    ElMessage.warning('请先配置SMTP服务器和发送邮箱')
    return
  }
  
  testingEmail.value = true
  
  try {
    // 模拟测试过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('邮件配置测试成功')
  } catch (error) {
    ElMessage.error('邮件配置测试失败')
  } finally {
    testingEmail.value = false
  }
}

const testWebhookConfig = async () => {
  if (!settings.notification.webhookUrl) {
    ElMessage.warning('请先配置Webhook URL')
    return
  }
  
  testingWebhook.value = true
  
  try {
    // 模拟测试过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('Webhook配置测试成功')
  } catch (error) {
    ElMessage.error('Webhook配置测试失败')
  } finally {
    testingWebhook.value = false
  }
}

const createBackup = async () => {
  creatingBackup.value = true
  
  try {
    // 模拟备份过程
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    ElMessage.success('备份创建成功')
    
    // 刷新备份列表
    backupList.value = generateMockBackupList()
  } catch (error) {
    ElMessage.error('创建备份失败')
  } finally {
    creatingBackup.value = false
  }
}

const restoreBackup = () => {
  restoreDialogVisible.value = true
  backupList.value = generateMockBackupList()
}

const selectBackup = (backup: BackupFile) => {
  selectedBackup.value = backup
}

const confirmRestore = async () => {
  if (!selectedBackup.value) {
    ElMessage.warning('请选择要恢复的备份文件')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要从备份 "${selectedBackup.value.filename}" 恢复数据吗？此操作将覆盖当前数据，不可撤销。`,
      '确认恢复',
      {
        type: 'warning'
      }
    )
    
    restoring.value = true
    
    // 模拟恢复过程
    await new Promise(resolve => setTimeout(resolve, 5000))
    
    ElMessage.success('数据恢复成功')
    restoreDialogVisible.value = false
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('数据恢复失败')
    }
  } finally {
    restoring.value = false
  }
}

const handleRestoreClose = () => {
  restoreDialogVisible.value = false
  selectedBackup.value = null
  restoreContent.value = ['database', 'config']
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getBackupTypeTag = (type: string) => {
  switch (type) {
    case 'auto':
      return 'success'
    case 'manual':
      return 'primary'
    case 'scheduled':
      return 'warning'
    default:
      return 'info'
  }
}

const getBackupTypeName = (type: string) => {
  switch (type) {
    case 'auto':
      return '自动备份'
    case 'manual':
      return '手动备份'
    case 'scheduled':
      return '定时备份'
    default:
      return '未知类型'
  }
}

// 生命周期
onMounted(() => {
  // 加载系统设置
  // 这里可以从API加载实际的设置数据
})
</script>

<style lang="scss" scoped>
.system-settings-container {
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
        
        .email-config,
        .webhook-config,
        .backup-config {
          margin-left: 20px;
          padding-left: 20px;
          border-left: 2px solid var(--el-border-color-light);
        }
      }
    }
  }
  
  .import-config {
    .file-info {
      margin-top: 16px;
      padding: 12px;
      background-color: var(--el-fill-color-light);
      border-radius: 6px;
      
      p {
        margin: 4px 0;
        font-size: 14px;
        color: var(--el-text-color-regular);
      }
    }
  }
  
  .restore-backup {
    .selected-backup {
      margin-top: 16px;
    }
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>