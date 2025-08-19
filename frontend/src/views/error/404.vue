<template>
  <div class="error-page">
    <div class="error-container">
      <div class="error-illustration">
        <div class="error-code">404</div>
        <div class="error-icon">
          <el-icon><QuestionFilled /></el-icon>
        </div>
      </div>
      
      <div class="error-content">
        <h1 class="error-title">页面未找到</h1>
        <p class="error-description">
          抱歉，您访问的页面不存在。可能是页面已被删除、移动或URL输入错误。请检查网址是否正确，或返回到主页继续浏览。
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
          <el-button @click="searchPage">
            <el-icon><Search /></el-icon>
            搜索页面
          </el-button>
        </div>
        
        <div class="error-tips">
          <h3>您可以尝试：</h3>
          <ul>
            <li>检查网址拼写是否正确</li>
            <li>使用导航菜单找到您需要的页面</li>
            <li>返回首页重新开始浏览</li>
            <li>联系我们报告此问题</li>
          </ul>
        </div>
        
        <div class="quick-links">
          <h3>快速链接：</h3>
          <div class="links-grid">
            <el-button text @click="navigateTo('/dashboard')">
              <el-icon><DataBoard /></el-icon>
              仪表板
            </el-button>
            <el-button text @click="navigateTo('/tasks')">
              <el-icon><List /></el-icon>
              任务管理
            </el-button>
            <el-button text @click="navigateTo('/crawler')">
              <el-icon><Connection /></el-icon>
              爬虫配置
            </el-button>
            <el-button text @click="navigateTo('/settings')">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-button>
          </div>
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
  QuestionFilled,
  ArrowLeft,
  HomeFilled,
  Search,
  DataBoard,
  List,
  Connection,
  Setting,
  Phone,
  Message
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

// 搜索页面
const searchPage = () => {
  ElMessage.info('搜索功能待实现')
  // 这里可以实现页面搜索功能
}

// 导航到指定页面
const navigateTo = (path) => {
  router.push(path)
}
</script>

<style lang="scss" scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
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
    color: #74b9ff;
    line-height: 1;
    margin-bottom: 20px;
    text-shadow: 0 4px 8px rgba(116, 185, 255, 0.3);
    
    @media (max-width: 768px) {
      font-size: 80px;
    }
  }
  
  .error-icon {
    .el-icon {
      font-size: 80px;
      color: #74b9ff;
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
    border-left: 4px solid #74b9ff;
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
  
  .quick-links {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 24px;
    border-left: 4px solid #00b894;
    
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
      color: #2c3e50;
      font-weight: 600;
    }
    
    .links-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 12px;
      
      .el-button {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        padding: 16px 12px;
        height: auto;
        border-radius: 8px;
        transition: all 0.3s ease;
        
        &:hover {
          background-color: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
        }
        
        .el-icon {
          font-size: 24px;
        }
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