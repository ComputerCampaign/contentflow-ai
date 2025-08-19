<template>
  <div class="not-found-page">
    <div class="not-found-container">
      <div class="error-illustration">
        <div class="error-code">404</div>
        <div class="error-icon">
          <i class="fas fa-search"></i>
        </div>
      </div>
      
      <div class="error-content">
        <h1>页面未找到</h1>
        <p>抱歉，您访问的页面不存在或已被移除。</p>
        
        <div class="error-actions">
          <el-button type="primary" @click="goHome">
            <i class="fas fa-home"></i>
            返回首页
          </el-button>
          <el-button @click="goBack">
            <i class="fas fa-arrow-left"></i>
            返回上页
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.not-found-container {
  text-align: center;
  z-index: 2;
  position: relative;
}

.error-illustration {
  margin-bottom: 40px;
  position: relative;
  
  .error-code {
    font-size: 120px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.9);
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
    
    @media (max-width: 768px) {
      font-size: 80px;
    }
  }
  
  .error-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    
    i {
      font-size: 40px;
      color: rgba(255, 255, 255, 0.7);
      animation: float 3s ease-in-out infinite;
    }
  }
}

.error-content {
  color: white;
  
  h1 {
    font-size: 32px;
    font-weight: 600;
    margin-bottom: 16px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    
    @media (max-width: 768px) {
      font-size: 24px;
    }
  }
  
  p {
    font-size: 16px;
    margin-bottom: 32px;
    opacity: 0.9;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
  }
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  
  @media (max-width: 480px) {
    flex-direction: column;
    align-items: center;
  }
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
  
  &.shape-1 {
    width: 80px;
    height: 80px;
    top: 20%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &.shape-2 {
    width: 120px;
    height: 120px;
    top: 60%;
    right: 15%;
    animation-delay: 2s;
  }
  
  &.shape-3 {
    width: 60px;
    height: 60px;
    bottom: 20%;
    left: 20%;
    animation-delay: 4s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

// Element Plus 按钮样式覆盖
:deep(.el-button) {
  border-radius: 25px;
  padding: 12px 24px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
  
  &.el-button--primary {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
    color: white;
    backdrop-filter: blur(10px);
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.4);
    }
  }
  
  &:not(.el-button--primary) {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: white;
    backdrop-filter: blur(10px);
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
    }
  }
}
</style>