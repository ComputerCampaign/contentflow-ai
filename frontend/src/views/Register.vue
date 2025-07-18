<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="title">爬虫系统注册</h2>
      
      <el-form :model="registerForm" :rules="rules" ref="registerForm" label-width="0px">
        <el-form-item prop="username">
          <el-input v-model="registerForm.username" prefix-icon="el-icon-user" placeholder="用户名"></el-input>
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input v-model="registerForm.email" prefix-icon="el-icon-message" placeholder="邮箱"></el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input v-model="registerForm.password" prefix-icon="el-icon-lock" type="password" placeholder="密码"></el-input>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" prefix-icon="el-icon-lock" type="password" placeholder="确认密码"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" class="register-button" @click="handleRegister">注册</el-button>
        </el-form-item>
        
        <div class="tips">
          <span>已有账号？</span>
          <router-link to="/login">立即登录</router-link>
        </div>
      </el-form>
      
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        @close="clearError"
      ></el-alert>
      
      <el-alert
        v-if="success"
        :title="success"
        type="success"
        show-icon
        @close="clearSuccess"
      ></el-alert>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Register',
  data() {
    // 密码确认验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    ...mapActions('auth', ['register']),
    
    handleRegister() {
      this.$refs.registerForm.validate(async valid => {
        if (valid) {
          this.loading = true
          this.error = ''
          this.success = ''
          
          try {
            // 提取注册所需数据
            const { username, email, password } = this.registerForm
            await this.register({ username, email, password })
            
            this.success = '注册成功，请登录'
            
            // 注册成功后清空表单
            this.$refs.registerForm.resetFields()
            
            // 3秒后跳转到登录页
            setTimeout(() => {
              this.$router.push('/login')
            }, 3000)
          } catch (error) {
            this.error = error.response?.data?.error || '注册失败，请稍后重试'
          } finally {
            this.loading = false
          }
        }
      })
    },
    
    clearError() {
      this.error = ''
    },
    
    clearSuccess() {
      this.success = ''
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.register-box {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.register-button {
  width: 100%;
}

.tips {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
  color: #606266;
}

.tips a {
  color: #409EFF;
  text-decoration: none;
}
</style>