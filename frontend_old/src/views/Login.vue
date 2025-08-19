<template>
  <div class="login-container">
    <!-- 背景动画 -->
    <div class="background-animation">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
        <div class="shape shape-6"></div>
      </div>
      <div class="gradient-overlay"></div>
    </div>

    <!-- 左侧内容区域 -->
    <div class="content-section">
      <div class="content-wrapper">
        <div class="brand-info">
          <div class="logo-section">
            <div class="logo-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <h1 class="brand-title">数据爬取博客发布平台</h1>
            <p class="brand-subtitle">智能化内容生产解决方案</p>
          </div>
          
          <div class="features-list">
            <div class="feature-item">
              <i class="fas fa-robot"></i>
              <span>智能爬虫配置</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-magic"></i>
              <span>AI内容生成</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-rocket"></i>
              <span>一键发布部署</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-chart-bar"></i>
              <span>实时监控分析</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-section">
      <div class="login-form-container">
        <div class="login-header">
          <h2 class="login-title">欢迎回来</h2>
          <p class="login-subtitle">请登录您的账户</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          size="large"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名或邮箱"
              prefix-icon="User"
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <div class="login-options">
              <el-checkbox v-model="loginForm.remember">
                记住我
              </el-checkbox>
              <el-link type="primary" :underline="false">
                忘记密码？
              </el-link>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <p class="register-link">
            还没有账户？
            <el-link type="primary" :underline="false">
              立即注册
            </el-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    const success = await userStore.login(loginForm)
    
    if (success) {
      ElMessage.success('登录成功，正在跳转...')
      // 立即跳转，不需要延迟
      await router.push('/dashboard')
    }
  } catch (error) {
    console.error('登录失败:', error)
    // 错误消息已经在userStore.login中处理了
  } finally {
    loading.value = false
  }
}

// 组件挂载后的操作
onMounted(() => {
  // 如果已经登录，直接跳转到仪表板
  if (userStore.isAuthenticated) {
    router.push('/dashboard')
  }
  
  // 添加页面加载动画
  document.body.classList.add('login-page')
})
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
}

// 背景动画
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 1;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite linear;
  backdrop-filter: blur(10px);
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 20%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 30%;
  left: 15%;
  animation-delay: 4s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  right: 10%;
  animation-delay: 6s;
}

.shape-5 {
  width: 40px;
  height: 40px;
  top: 50%;
  left: 50%;
  animation-delay: 8s;
}

.shape-6 {
  width: 90px;
  height: 90px;
  top: 70%;
  right: 40%;
  animation-delay: 10s;
}

@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 1;
  }
  100% {
    transform: translateY(0px) rotate(360deg);
    opacity: 0.7;
  }
}

// 左侧内容区域
.content-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  padding: 2rem;
}

.content-wrapper {
  max-width: 500px;
  color: white;
  text-align: center;
}

.brand-info {
  .logo-section {
    margin-bottom: 3rem;
    
    .logo-icon {
      width: 80px;
      height: 80px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1.5rem;
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.3);
      
      i {
        font-size: 2rem;
        color: white;
      }
    }
    
    .brand-title {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      background: linear-gradient(45deg, #fff, #f0f8ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .brand-subtitle {
      font-size: 1.2rem;
      opacity: 0.9;
      font-weight: 300;
    }
  }
  
  .features-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    
    .feature-item {
      display: flex;
      align-items: center;
      padding: 1rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.15);
      }
      
      i {
        font-size: 1.2rem;
        margin-right: 0.75rem;
        color: #ffd700;
      }
      
      span {
        font-weight: 500;
      }
    }
  }
}

// 右侧登录区域
.login-section {
  width: 450px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
}

.login-form-container {
  width: 100%;
  max-width: 350px;
  padding: 2rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
  
  .login-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
  }
  
  .login-subtitle {
    color: var(--text-secondary);
    font-size: 0.9rem;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 1.5rem;
  }
  
  .el-input {
    height: 48px;
    
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      border: 1px solid #e1e5e9;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: var(--primary-color);
      }
      
      &.is-focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
      }
    }
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  text-align: center;
  margin-top: 1.5rem;
  
  .register-link {
    color: var(--text-secondary);
    font-size: 0.9rem;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .content-section {
    min-height: 40vh;
    padding: 1rem;
  }
  
  .login-section {
    width: 100%;
    min-height: 60vh;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
  }
  
  .brand-info {
    .brand-title {
      font-size: 2rem;
    }
    
    .features-list {
      grid-template-columns: 1fr;
    }
  }
}
</style>