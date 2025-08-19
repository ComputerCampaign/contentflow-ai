<template>
  <div class="error-page">
    <div class="error-container">
      <div class="error-illustration">
        <div class="error-code">500</div>
        <div class="error-icon">
          <el-icon><WarningFilled /></el-icon>
        </div>
      </div>
      
      <div class="error-content">
        <h1 class="error-title">服务器内部错误</h1>
        <p class="error-description">
          抱歉，服务器遇到了一个内部错误，无法完成您的请求。我们的技术团队已经收到通知，正在紧急处理这个问题。请稍后再试，或联系我们的技术支持。
        </p>
        
        <div class="error-actions">
          <el-button type="primary" @click="refreshPage">
            <el-icon><Refresh /></el-icon>
            刷新页面
          </el-button>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回上一页
          </el-button>
          <el-button @click="goHome">
            <el-icon><HomeFilled /></el-icon>
            回到首页
          </el-button>
          <el-button @click="reportError">
            <el-icon><Warning /></el-icon>
            报告问题
          </el-button>
        </div>
        
        <div class="error-details" v-if="showDetails">
          <h3>错误详情：</h3>
          <div class="details-content">
            <p><strong>错误时间：</strong>{{ errorTime }}</p>
            <p><strong>错误ID：</strong>{{ errorId }}</p>
            <p><strong>请求路径：</strong>{{ currentPath }}</p>
            <p><strong>用户代理：</strong>{{ userAgent }}</p>
          </div>
        </div>
        
        <div class="error-tips">
          <h3>可能的解决方案：</h3>
          <ul>
            <li>刷新页面重新尝试</li>
            <li>检查网络连接是否正常</li>
            <li>清除浏览器缓存和Cookie</li>
            <li>稍后再试，服务器可能正在维护</li>
            <li>如果问题持续存在，请联系技术支持</li>
          </ul>
        </div>
        
        <div class="error-actions-secondary">
          <el-button text @click="toggleDetails">
            <el-icon><View /></el-icon>
            {{ showDetails ? '隐藏' : '显示' }}错误详情
          </el-button>
          <el-button text @click="downloadLog">
            <el-icon><Download /></el-icon>
            下载错误日志
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="error-footer">
      <p>我们对此问题深表歉意，技术团队正在努力解决</p>
      <p class="support-info">
        <el-icon><Phone /></el-icon>
        紧急技术支持：400-123-4567
        <span class="divider">|</span>
        <el-icon><Message /></el-icon>
        邮箱：emergency@example.com
        <span class="divider">|</span>
        <el-icon><ChatDotRound /></el-icon>
        在线客服：24小时服务
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  WarningFilled,
  Refresh,
  ArrowLeft,
  HomeFilled,
  Warning,
  View,
  Download,
  Phone,
  Message,
  ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const showDetails = ref(false)
const errorTime = ref('')
const errorId = ref('')
const currentPath = ref('')
const userAgent = ref('')

onMounted(() => {
  // 初始化错误信息
  errorTime.value = new Date().toLocaleString('zh-CN')
  errorId.value = generateErrorId()
  currentPath.value = route.fullPath
  userAgent.value = navigator.userAgent
})

// 生成错误ID
const generateErrorId = () => {
  return 'ERR-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).substr(2, 5).toUpperCase()
}

// 刷新页面
const refreshPage = () => {
  window.location.reload()
}

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

// 回到首页
const goHome = () => {
  router.push('/')
}

// 报告错误
const reportError = async () => {
  try {
    const { value: description } = await ElMessageBox.prompt(
      '请描述您遇到的问题，这将帮助我们更快地解决问题',
      '报告错误',
      {
        confirmButtonText: '提交报告',
        cancelButtonText: '取消',
        inputPlaceholder: '请详细描述问题...',
        inputType: 'textarea'
      }
    )
    
    // 这里可以实现错误报告提交逻辑
    console.log('错误报告:', {
      errorId: errorId.value,
      errorTime: errorTime.value,
      currentPath: currentPath.value,
      userAgent: userAgent.value,
      description
    })
    
    ElMessage.success('错误报告已提交，我们会尽快处理')
  } catch {
    // 用户取消了报告
  }
}

// 切换详情显示
const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

// 下载错误日志
const downloadLog = () => {
  const logData = {
    errorId: errorId.value,
    errorTime: errorTime.value,
    currentPath: currentPath.value,
    userAgent: userAgent.value,
    errorType: '500 Internal Server Error',
    timestamp: Date.now()
  }
  
  const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `error-log-${errorId.value}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success('错误日志已下载')
}
</script>

<style lang="scss" scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
  padding: 20px;
}

.error-container {
  display: flex;
  align-items: center;
  gap: 60px;
  max-width: 1000px;
  width: 100%;
  background: white;
  border-radius: 20px;
  padding: 60px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 40px;
    padding: 40px 20px;
  }
}

.error-illustration {
  flex-shrink: 0;
  text-align: center;
  position: relative;
  
  .error-code {
    font-size: 120px;
    font-weight: 900;
    color: #ff7675;
    line-height: 1;
    margin-bottom: 20px;
    text-shadow: 0 4px 8px rgba(255, 118, 117, 0.3);
    
    @media (max-width: 768px) {
      font-size: 80px;
    }
  }
  
  .error-icon {
    .el-icon {
      font-size: 80px;
      color: #ff7675;
      opacity: 0.8;
      animation: pulse 2s infinite;
      
      @media (max-width: 768px) {
        font-size: 60px;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
}

.error-content {
  flex: 1;
  
  .error-title {
    font-size: 36px;
    font-weight: 700;
    color: #2c3e50;
    margin: 0 0 20px 0;
    
    @media (max-width: 768px) {
      font-size: 28px;
      text-align: center;
    }
  }
  
  .error-description {
    font-size: 18px;
    color: #7f8c8d;
    line-height: 1.6;
    margin: 0 0 40px 0;
    
    @media (max-width: 768px) {
      font-size: 16px;
      text-align: center;
    }
  }
  
  .error-actions {
    display: flex;
    gap: 16px;
    margin-bottom: 40px;
    flex-wrap: wrap;
    
    @media (max-width: 768px) {
      flex-direction: column;
      align-items: center;
    }
    
    .el-button {
      padding: 12px 24px;
      font-size: 16px;
      border-radius: 8px;
      
      @media (max-width: 768px) {
        width: 200px;
      }
    }
  }
  
  .error-details {
    background: #fff5f5;
    border: 1px solid #fed7d7;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
    
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
      color: #c53030;
      font-weight: 600;
    }
    
    .details-content {
      p {
        margin: 8px 0;
        font-size: 14px;
        color: #4a5568;
        word-break: break-all;
        
        strong {
          color: #2d3748;
        }
      }
    }
  }
  
  .error-tips {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 24px;
    border-left: 4px solid #ff7675;
    margin-bottom: 32px;
    
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
      color: #2c3e50;
      font-weight: 600;
    }
    
    ul {
      margin: 0;
      padding-left: 20px;
      
      li {
        color: #7f8c8d;
        line-height: 1.8;
        font-size: 14px;
      }
    }
  }
  
  .error-actions-secondary {
    display: flex;
    gap: 16px;
    justify-content: center;
    
    @media (max-width: 768px) {
      flex-direction: column;
      align-items: center;
    }
    
    .el-button {
      padding: 8px 16px;
      font-size: 14px;
    }
  }
}

.error-footer {
  text-align: center;
  margin-top: 40px;
  color: white;
  
  p {
    margin: 8px 0;
    opacity: 0.9;
  }
  
  .support-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
    
    .el-icon {
      font-size: 16px;
    }
    
    .divider {
      margin: 0 12px;
      opacity: 0.6;
    }
    
    @media (max-width: 768px) {
      flex-direction: column;
      gap: 4px;
      
      .divider {
        display: none;
      }
    }
  }
}
</style>