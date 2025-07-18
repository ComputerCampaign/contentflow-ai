<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="title">爬虫系统登录</h2>
      
      <el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="0px">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" prefix-icon="el-icon-user" placeholder="用户名"></el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" prefix-icon="el-icon-lock" type="password" placeholder="密码" @keyup.enter="handleLogin"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-button" @click="handleLogin">登录</el-button>
        </el-form-item>
        
        <div class="tips">
          <span>还没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </div>
      </el-form>
      
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        @close="clearError"
      ></el-alert>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    ...mapActions('auth', ['login']),
    
    handleLogin() {
      this.$refs.loginForm.validate(async valid => {
        if (valid) {
          this.loading = true
          this.error = ''
          
          try {
            await this.login(this.loginForm)
            this.$router.push('/')
          } catch (error) {
            this.error = error.response?.data?.error || '登录失败，请检查用户名和密码'
          } finally {
            this.loading = false
          }
        }
      })
    },
    
    clearError() {
      this.error = ''
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-box {
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

.login-button {
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