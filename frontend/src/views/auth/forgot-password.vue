<template>
  <div class="forgot-password-container">
    <div class="forgot-password-form">
      <div class="form-header">
        <div class="logo">
          <img src="/logo.svg" alt="ContentFlow AI" class="logo-img" />
          <h1 class="logo-text">ContentFlow AI</h1>
        </div>
        <p class="form-subtitle">重置您的密码</p>
      </div>

      <div v-if="step === 1" class="step-content">
        <p class="step-description">
          请输入您的邮箱地址，我们将向您发送重置密码的链接。
        </p>
        
        <el-form
          ref="emailFormRef"
          :model="emailForm"
          :rules="emailRules"
          class="form-content"
          @keyup.enter="handleSendEmail"
        >
          <el-form-item prop="email">
            <el-input
              v-model="emailForm.email"
              placeholder="请输入邮箱地址"
              size="large"
              prefix-icon="Message"
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="handleSendEmail"
            >
              {{ loading ? '发送中...' : '发送重置链接' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-else-if="step === 2" class="step-content">
        <div class="success-icon">
          <el-icon size="64" color="#67c23a">
            <CircleCheck />
          </el-icon>
        </div>
        <h3>邮件已发送</h3>
        <p class="step-description">
          我们已向 <strong>{{ emailForm.email }}</strong> 发送了重置密码的链接。
          请检查您的邮箱（包括垃圾邮件文件夹）并点击链接重置密码。
        </p>
        
        <div class="resend-section">
          <p class="resend-text">
            没有收到邮件？
            <span v-if="countdown > 0" class="countdown">
              {{ countdown }}秒后可重新发送
            </span>
            <a v-else href="#" class="resend-link" @click="handleResend">
              重新发送
            </a>
          </p>
        </div>
      </div>

      <div class="back-to-login">
        <router-link to="/auth/login">
          <el-icon><ArrowLeft /></el-icon>
          返回登录
        </router-link>
      </div>
    </div>

    <div class="forgot-password-bg">
      <div class="bg-content">
        <h2>密码重置</h2>
        <p>安全便捷的密码找回服务</p>
        <div class="features">
          <div class="feature">
            <el-icon size="32" color="rgba(255,255,255,0.8)">
              <Shield />
            </el-icon>
            <h4>安全可靠</h4>
            <p>采用加密技术保护您的账户安全</p>
          </div>
          <div class="feature">
            <el-icon size="32" color="rgba(255,255,255,0.8)">
              <Clock />
            </el-icon>
            <h4>快速响应</h4>
            <p>邮件将在几分钟内送达您的邮箱</p>
          </div>
          <div class="feature">
            <el-icon size="32" color="rgba(255,255,255,0.8)">
              <Message />
            </el-icon>
            <h4>邮件通知</h4>
            <p>通过邮件链接安全重置您的密码</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { CircleCheck, ArrowLeft, Clock, Message } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { isValidEmail } from '@/utils/validate'

const userStore = useUserStore()

// 表单引用
const emailFormRef = ref<FormInstance>()

// 当前步骤
const step = ref(1)

// 加载状态
const loading = ref(false)

// 倒计时
const countdown = ref(0)
let countdownTimer: number | null = null

// 邮箱表单数据
const emailForm = reactive({
  email: ''
})

// 表单验证规则
const emailRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (!isValidEmail(value)) {
        callback(new Error('请输入有效的邮箱地址'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ]
}

// 开始倒计时
const startCountdown = () => {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer!)
      countdownTimer = null
    }
  }, 1000)
}

// 发送重置邮件
const handleSendEmail = async () => {
  if (!emailFormRef.value) return
  
  try {
    const valid = await emailFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    // 调用用户store的忘记密码方法
    await userStore.forgotPassword(emailForm.email)
    
    ElMessage.success('重置链接已发送到您的邮箱')
    
    // 切换到成功步骤
    step.value = 2
    startCountdown()
    
  } catch (error: any) {
    ElMessage.error(error.message || '发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重新发送
const handleResend = () => {
  if (countdown.value > 0) return
  handleSendEmail()
}

// 清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style lang="scss" scoped>
.forgot-password-container {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.forgot-password-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: white;
  max-width: 480px;
  
  .form-header {
    text-align: center;
    margin-bottom: 2rem;
    
    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1rem;
      
      .logo-img {
        width: 48px;
        height: 48px;
        margin-right: 12px;
      }
      
      .logo-text {
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
      }
    }
    
    .form-subtitle {
      color: #6c757d;
      font-size: 14px;
      margin: 0;
    }
  }
  
  .step-content {
    width: 100%;
    max-width: 360px;
    text-align: center;
    
    .step-description {
      color: #6c757d;
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 2rem;
    }
    
    .success-icon {
      margin-bottom: 1rem;
    }
    
    h3 {
      color: #2c3e50;
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 1rem;
    }
    
    .resend-section {
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 1px solid #eee;
      
      .resend-text {
        color: #6c757d;
        font-size: 14px;
        margin: 0;
        
        .countdown {
          color: #409eff;
          font-weight: 500;
        }
        
        .resend-link {
          color: #409eff;
          text-decoration: none;
          font-weight: 500;
          
          &:hover {
            text-decoration: underline;
          }
        }
      }
    }
  }
  
  .form-content {
    width: 100%;
    
    .submit-btn {
      width: 100%;
      height: 48px;
      font-size: 16px;
      font-weight: 500;
    }
  }
  
  .back-to-login {
    margin-top: 2rem;
    
    a {
      display: flex;
      align-items: center;
      color: #6c757d;
      text-decoration: none;
      font-size: 14px;
      transition: color 0.3s;
      
      .el-icon {
        margin-right: 0.5rem;
      }
      
      &:hover {
        color: #409eff;
      }
    }
  }
}

.forgot-password-bg {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  
  .bg-content {
    text-align: center;
    max-width: 500px;
    
    h2 {
      font-size: 36px;
      font-weight: 600;
      margin-bottom: 1rem;
    }
    
    p {
      font-size: 18px;
      margin-bottom: 3rem;
      opacity: 0.9;
    }
    
    .features {
      .feature {
        margin-bottom: 2rem;
        
        .el-icon {
          margin-bottom: 1rem;
        }
        
        h4 {
          margin: 0 0 0.5rem 0;
          font-size: 18px;
          font-weight: 600;
        }
        
        p {
          margin: 0;
          font-size: 14px;
          opacity: 0.8;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .forgot-password-container {
    flex-direction: column;
  }
  
  .forgot-password-form {
    max-width: none;
    min-height: 70vh;
  }
  
  .forgot-password-bg {
    min-height: 30vh;
    
    .bg-content {
      h2 {
        font-size: 28px;
      }
      
      p {
        font-size: 16px;
        margin-bottom: 2rem;
      }
      
      .features {
        .feature {
          margin-bottom: 1.5rem;
          
          h4 {
            font-size: 16px;
          }
          
          p {
            font-size: 13px;
          }
        }
      }
    }
  }
}
</style>