<template>
  <div class="login-page">
    <!-- 全屏背景 -->
    <div class="background-layer">
      <div class="background-image"></div>
      <div class="background-overlay"></div>
    </div>
    
    <!-- 左侧简介内容区域 -->
    <div class="content-section">
      <div class="content-wrapper">
        <div class="brand-intro">
          <h1 class="intro-title">ContentFlow AI</h1>
          <p class="intro-subtitle">智能内容生成，让创作更高效</p>
          <div class="feature-list">
            <div class="feature-item">
              <div class="feature-icon">✨</div>
              <div class="feature-text">
                <h3>AI智能写作</h3>
                <p>基于先进AI技术，快速生成高质量内容</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <div class="feature-text">
                <h3>效率提升</h3>
                <p>大幅提升内容创作效率，节省宝贵时间</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎯</div>
              <div class="feature-text">
                <h3>精准定制</h3>
                <p>根据需求定制内容风格和格式</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 登录表单容器 -->
    <div class="login-container">
      <div class="login-card">
        <!-- 品牌标题 -->
        <div class="brand-header">
          <div class="brand-icon">
            <img src="/logo.svg" alt="ContentFlow AI Logo" class="brand-logo" />
          </div>
          <h1 class="brand-title">ContentFlow AI</h1>
          <p class="brand-subtitle">智能内容生成平台</p>
        </div>
        
        <!-- 登录表单 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              class="login-input"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              class="login-input"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <div class="login-options">
              <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
              <el-link type="primary" :underline="false" @click="handleForgotPassword">忘记密码？</el-link>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-button"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- 注册链接 -->
        <div class="register-link">
          <span>还没有账号？</span>
          <el-link type="primary" :underline="false" @click="handleRegister">立即注册</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
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
    await loginFormRef.value.validate()
    loading.value = true
    
    // 调用登录接口
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
      rememberMe: loginForm.remember
    })
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

// 处理注册
const handleRegister = () => {
  router.push('/register')
}

// 处理忘记密码
const handleForgotPassword = () => {
  ElMessage.info('忘记密码功能正在开发中，请联系管理员')
}
</script>

<style lang="scss" scoped>
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  box-sizing: border-box;
}

// 背景层
.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/123.jpeg');
  background-repeat: repeat;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.7) 0%,
    rgba(118, 75, 162, 0.7) 50%,
    rgba(255, 107, 107, 0.7) 100%
  );
}

// 左侧简介内容区域
.content-section {
  position: relative;
  flex: 3;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  padding: 40px;
  box-sizing: border-box;
  min-width: 0;
}

.content-wrapper {
  max-width: 500px;
  width: 100%;
}

.brand-intro {
  color: white;
  text-align: left;
}

.intro-title {
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 20px 0;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.intro-subtitle {
  font-size: 20px;
  margin: 0 0 50px 0;
  opacity: 0.9;
  line-height: 1.5;
  text-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.feature-icon {
  font-size: 24px;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.feature-text {
  flex: 1;
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: white;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }
  
  p {
    font-size: 14px;
    margin: 0;
    opacity: 0.8;
    line-height: 1.5;
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
}

// 登录容器
.login-container {
  position: relative;
  flex: 2;
  min-width: 420px;
  max-width: 600px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  padding: 20px;
  box-sizing: border-box;
}

// 登录卡片
.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 品牌头部
.brand-header {
  text-align: center;
  margin-bottom: 40px;
}

.brand-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  overflow: hidden;
  padding: 8px;
  
  .brand-logo {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    background: white;
    padding: 6px;
    box-sizing: border-box;
  }
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

// 登录表单
.login-form {
  .el-form-item {
    margin-bottom: 24px;
  }
}

.login-input {
  :deep(.el-input__wrapper) {
    background-color: rgba(255, 255, 255, 0.8);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    min-height: 50px;
    
    &:hover {
      border-color: #667eea;
      background-color: rgba(255, 255, 255, 0.9);
      box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    }
    
    &.is-focus {
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
      background-color: rgba(255, 255, 255, 0.95);
    }
  }
  
  :deep(.el-input__inner) {
    color: #2c3e50;
    font-size: 16px;
    font-weight: 500;
    
    &::placeholder {
      color: #a0a8b0;
      font-weight: 400;
    }
  }
  
  :deep(.el-input__prefix) {
    color: #7f8c8d;
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  
  :deep(.el-checkbox__label) {
    color: #7f8c8d;
    font-size: 14px;
  }
  
  .el-link {
    font-size: 14px;
  }
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

// 注册链接
.register-link {
  text-align: center;
  margin-top: 30px;
  color: #7f8c8d;
  font-size: 14px;
  
  .el-link {
    margin-left: 8px;
    font-size: 14px;
    font-weight: 500;
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .login-page {
    flex-direction: column;
  }
  
  .content-section {
    display: none;
  }
  
  .login-container {
    width: 100%;
    min-width: auto;
    max-width: none;
    flex: 1;
  }
}

@media (max-width: 768px) {
  .content-section {
    padding: 20px;
  }
  
  .login-container {
    padding: 15px;
  }
  
  .login-card {
    padding: 30px 25px;
    border-radius: 16px;
    margin: 0;
  }
  
  .brand-icon {
    width: 60px;
    height: 60px;
    
    .brand-logo {
      width: 35px;
      height: 35px;
    }
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .brand-subtitle {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 25px 20px;
    margin: 10px;
  }
  
  .brand-header {
    margin-bottom: 30px;
  }
  
  .login-input {
    :deep(.el-input__wrapper) {
      min-height: 45px;
    }
  }
  
  .login-button {
    height: 45px;
    font-size: 15px;
  }
}

// 大屏幕优化
@media (min-width: 1400px) {
  .content-section {
    padding: 80px;
  }
  
  .intro-title {
    font-size: 56px;
  }
  
  .intro-subtitle {
    font-size: 22px;
  }
  
  .login-container {
    max-width: 550px;
  }
}
</style>