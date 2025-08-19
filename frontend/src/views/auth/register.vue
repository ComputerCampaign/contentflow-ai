<template>
  <div class="register-container">
    <div class="register-form">
      <div class="register-header">
        <div class="logo">
          <img src="/logo.svg" alt="ContentFlow AI" class="logo-img" />
          <h1 class="logo-text">ContentFlow AI</h1>
        </div>
        <p class="register-subtitle">创建您的账户</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form-content"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            size="large"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item prop="agreement">
          <el-checkbox v-model="registerForm.agreement">
            我已阅读并同意
            <a href="#" class="agreement-link">《用户协议》</a>
            和
            <a href="#" class="agreement-link">《隐私政策》</a>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注册账户' }}
          </el-button>
        </el-form-item>

        <div class="login-link">
          已有账号？
          <router-link to="/auth/login">
            立即登录
          </router-link>
        </div>
      </el-form>
    </div>

    <div class="register-bg">
      <div class="bg-content">
        <h2>加入 ContentFlow AI</h2>
        <p>开启您的智能内容管理之旅</p>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>创建账户</h4>
              <p>快速注册，立即开始</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>配置爬虫</h4>
              <p>设置您的数据源</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>智能分析</h4>
              <p>AI 驱动的内容解析</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { isValidEmail, getPasswordStrength } from '@/utils/validate'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const registerFormRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

// 自定义验证规则
const validatePassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    const strength = getPasswordStrength(value)
    if (strength < 2) {
      callback(new Error('密码强度太弱，请包含字母、数字和特殊字符'))
    } else {
      if (registerForm.confirmPassword !== '') {
        registerFormRef.value?.validateField('confirmPassword')
      }
      callback()
    }
  }
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreement = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议和隐私政策'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (!isValidEmail(value)) {
        callback(new Error('请输入有效的邮箱地址'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreement: [
    { validator: validateAgreement, trigger: 'change' }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    // 调用用户store的注册方法
    await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      confirmPassword: registerForm.confirmPassword
    })
    
    ElMessage.success('注册成功，请登录')
    
    // 跳转到登录页面
    router.push('/auth/login')
    
  } catch (error: any) {
    ElMessage.error(error.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-container {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: white;
  max-width: 480px;
  
  .register-header {
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
    
    .register-subtitle {
      color: #6c757d;
      font-size: 14px;
      margin: 0;
    }
  }
  
  .register-form-content {
    width: 100%;
    max-width: 360px;
    
    .agreement-link {
      color: #409eff;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
    
    .register-btn {
      width: 100%;
      height: 48px;
      font-size: 16px;
      font-weight: 500;
    }
    
    .login-link {
      text-align: center;
      margin-top: 1rem;
      color: #6c757d;
      font-size: 14px;
      
      a {
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

.register-bg {
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
    
    .steps {
      .step {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        text-align: left;
        
        .step-number {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 18px;
          margin-right: 1rem;
          flex-shrink: 0;
        }
        
        .step-content {
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
}

// 响应式设计
@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
  }
  
  .register-form {
    max-width: none;
    min-height: 70vh;
  }
  
  .register-bg {
    min-height: 30vh;
    
    .bg-content {
      h2 {
        font-size: 28px;
      }
      
      p {
        font-size: 16px;
        margin-bottom: 2rem;
      }
      
      .steps {
        .step {
          margin-bottom: 1.5rem;
          
          .step-number {
            width: 32px;
            height: 32px;
            font-size: 16px;
          }
          
          .step-content {
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
}
</style>