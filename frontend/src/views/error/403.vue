<template>
  <div class="error-page">
    <div class="error-container">
      <div class="error-illustration">
        <div class="error-code">403</div>
        <div class="error-icon">
          <el-icon><Lock /></el-icon>
        </div>
      </div>
      
      <div class="error-content">
        <h1 class="error-title">访问被拒绝</h1>
        <p class="error-description">
          抱歉，您没有权限访问此页面。请联系管理员获取相应权限，或返回到您有权限访问的页面。
        </p>
        
        <div class="error-actions">
          <el-button type="primary" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回上一页
          </el-button>
          <el-button @click="goHome">
            <el-icon><HomeFilled /></el-icon>
            回到首页
          </el-button>
          <el-button @click="contactAdmin">
            <el-icon><Message /></el-icon>
            联系管理员
          </el-button>
        </div>
        
        <div class="error-tips">
          <h3>可能的原因：</h3>
          <ul>
            <li>您的账户权限不足</li>
            <li>页面需要特定的角色权限</li>
            <li>您的会话已过期，请重新登录</li>
            <li>系统正在维护中</li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="error-footer">
      <p>如果问题持续存在，请联系技术支持</p>
      <p class="support-info">
        <el-icon><Phone /></el-icon>
        技术支持：400-123-4567
        <span class="divider">|</span>
        <el-icon><Message /></el-icon>
        邮箱：support@example.com
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Lock,
  ArrowLeft,
  HomeFilled,
  Message,
  Phone
} from '@element-plus/icons-vue'

const router = useRouter()

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

// 联系管理员
const contactAdmin = () => {
  ElMessage.info('正在跳转到联系页面...')
  // 这里可以跳转到联系页面或打开邮件客户端
}
</script>

<style lang="scss" scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    color: #ff6b6b;
    line-height: 1;
    margin-bottom: 20px;
    text-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
    
    @media (max-width: 768px) {
      font-size: 80px;
    }
  }
  
  .error-icon {
    .el-icon {
      font-size: 80px;
      color: #ff6b6b;
      opacity: 0.8;
      
      @media (max-width: 768px) {
        font-size: 60px;
      }
    }
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
  
  .error-tips {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 24px;
    border-left: 4px solid #ff6b6b;
    
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