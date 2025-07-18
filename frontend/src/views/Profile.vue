<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <!-- 用户信息卡片 -->
        <el-card class="user-info-card">
          <div class="user-avatar">
            <el-avatar :size="100" :src="avatarUrl">{{ userInitials }}</el-avatar>
          </div>
          
          <div class="user-details">
            <h2>{{ user.username }}</h2>
            <p class="user-email">{{ user.email }}</p>
            <el-tag :type="getGroupTagType(user.group_name)">{{ user.group_name }}</el-tag>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ userStats.taskCount || 0 }}</div>
              <div class="stat-label">爬虫任务</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.ruleCount || 0 }}</div>
              <div class="stat-label">XPath规则</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ formatDate(user.created_at) }}</div>
              <div class="stat-label">注册时间</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <!-- 个人资料编辑卡片 -->
        <el-card class="profile-edit-card">
          <template #header>
            <div class="card-header">
              <span>个人资料设置</span>
            </div>
          </template>
          
          <el-form 
            :model="profileForm" 
            :rules="rules" 
            ref="profileFormRef" 
            label-width="120px"
          >
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled></el-input>
              <div class="form-tip">用户名创建后不可修改</div>
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email"></el-input>
            </el-form-item>
            
            <el-form-item label="修改密码">
              <el-switch v-model="profileForm.changePassword"></el-switch>
            </el-form-item>
            
            <template v-if="profileForm.changePassword">
              <el-form-item label="当前密码" prop="currentPassword">
                <el-input 
                  v-model="profileForm.currentPassword" 
                  type="password" 
                  show-password
                ></el-input>
              </el-form-item>
              
              <el-form-item label="新密码" prop="newPassword">
                <el-input 
                  v-model="profileForm.newPassword" 
                  type="password" 
                  show-password
                ></el-input>
                <div class="form-tip">密码长度至少为8个字符</div>
              </el-form-item>
              
              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input 
                  v-model="profileForm.confirmPassword" 
                  type="password" 
                  show-password
                ></el-input>
              </el-form-item>
            </template>
            
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="updateProfile">保存更改</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- API密钥管理卡片 -->
        <el-card class="api-key-card">
          <template #header>
            <div class="card-header">
              <span>API密钥管理</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="generateApiKey"
                :loading="generatingKey"
              >生成新密钥</el-button>
            </div>
          </template>
          
          <div v-if="apiKeys.length === 0" class="empty-data">
            <el-empty description="暂无API密钥"></el-empty>
          </div>
          
          <el-table 
            v-else 
            :data="apiKeys" 
            style="width: 100%"
          >
            <el-table-column prop="key_id" label="密钥ID" width="100"></el-table-column>
            <el-table-column prop="name" label="名称" width="150"></el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="last_used" label="最后使用">
              <template #default="scope">
                {{ scope.row.last_used ? formatDate(scope.row.last_used) : '从未使用' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-popconfirm
                  title="确定要删除此API密钥吗？"
                  @confirm="deleteApiKey(scope.row.key_id)"
                >
                  <template #reference>
                    <el-button type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 新密钥显示对话框 -->
          <el-dialog 
            title="新API密钥" 
            v-model="newKeyDialogVisible" 
            width="500px"
            :close-on-click-modal="false"
            :close-on-press-escape="false"
            :show-close="false"
          >
            <div class="new-key-container">
              <p class="key-warning">请保存此密钥，它只会显示一次！</p>
              
              <div class="key-display">
                <el-input 
                  v-model="newApiKey" 
                  readonly
                ></el-input>
                <el-button 
                  type="primary" 
                  @click="copyApiKey"
                >复制</el-button>
              </div>
              
              <div class="key-form">
                <el-form :model="keyForm" :rules="keyRules" ref="keyFormRef">
                  <el-form-item label="密钥名称" prop="name">
                    <el-input v-model="keyForm.name" placeholder="为此密钥命名（可选）"></el-input>
                  </el-form-item>
                </el-form>
              </div>
            </div>
            
            <template #footer>
              <span class="dialog-footer">
                <el-button type="primary" @click="saveApiKeyName">我已保存密钥</el-button>
              </span>
            </template>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    
    const loading = ref(false)
    const generatingKey = ref(false)
    const profileFormRef = ref(null)
    const keyFormRef = ref(null)
    const apiKeys = ref([])
    const newKeyDialogVisible = ref(false)
    const newApiKey = ref('')
    
    // 用户统计数据
    const userStats = reactive({
      taskCount: 0,
      ruleCount: 0
    })
    
    // 表单数据
    const profileForm = reactive({
      username: '',
      email: '',
      changePassword: false,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    // API密钥表单
    const keyForm = reactive({
      name: ''
    })
    
    // 表单验证规则
    const rules = {
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      currentPassword: [
        { required: true, message: '请输入当前密码', trigger: 'blur', validator: (rule, value, callback) => {
          if (profileForm.changePassword && !value) {
            callback(new Error('请输入当前密码'))
          } else {
            callback()
          }
        }}
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur', validator: (rule, value, callback) => {
          if (profileForm.changePassword && !value) {
            callback(new Error('请输入新密码'))
          } else if (profileForm.changePassword && value.length < 8) {
            callback(new Error('密码长度至少为8个字符'))
          } else {
            callback()
          }
        }}
      ],
      confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur', validator: (rule, value, callback) => {
          if (profileForm.changePassword && !value) {
            callback(new Error('请确认新密码'))
          } else if (profileForm.changePassword && value !== profileForm.newPassword) {
            callback(new Error('两次输入的密码不一致'))
          } else {
            callback()
          }
        }}
      ]
    }
    
    // API密钥表单验证规则
    const keyRules = {
      name: [
        { max: 50, message: '名称长度不能超过50个字符', trigger: 'blur' }
      ]
    }
    
    // 计算属性
    const user = computed(() => store.getters['auth/user'] || {})
    
    // 用户头像URL
    const avatarUrl = computed(() => {
      // 如果用户有头像，返回头像URL
      // 这里假设没有头像，使用默认头像
      return ''
    })
    
    // 用户名首字母（用于默认头像）
    const userInitials = computed(() => {
      if (!user.value.username) return ''
      return user.value.username.charAt(0).toUpperCase()
    })
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    // 获取用户组标签类型
    const getGroupTagType = (groupName) => {
      if (!groupName) return 'info'
      
      switch (groupName.toLowerCase()) {
        case 'admin':
          return 'danger'
        case 'user':
          return 'primary'
        default:
          return 'info'
      }
    }
    
    // 更新个人资料
    const updateProfile = () => {
      profileFormRef.value.validate(async valid => {
        if (valid) {
          loading.value = true
          
          try {
            const userData = {
              email: profileForm.email
            }
            
            // 如果需要修改密码，添加密码字段
            if (profileForm.changePassword) {
              userData.current_password = profileForm.currentPassword
              userData.new_password = profileForm.newPassword
            }
            
            await store.dispatch('user/updateCurrentUser', userData)
            
            // 重新获取用户信息
            await store.dispatch('auth/fetchUser')
            
            // 重置密码相关字段
            profileForm.changePassword = false
            profileForm.currentPassword = ''
            profileForm.newPassword = ''
            profileForm.confirmPassword = ''
            
            ElMessage.success('个人资料更新成功')
          } catch (error) {
            ElMessage.error(error.response?.data?.error || '更新个人资料失败')
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    // 重置表单
    const resetForm = () => {
      profileFormRef.value.resetFields()
      
      // 重新填充表单数据
      Object.assign(profileForm, {
        username: user.value.username || '',
        email: user.value.email || '',
        changePassword: false,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      })
    }
    
    // 生成API密钥
    const generateApiKey = async () => {
      generatingKey.value = true
      
      try {
        const response = await store.dispatch('user/generateApiKey')
        
        // 显示新密钥
        newApiKey.value = response.data.api_key
        keyForm.name = ''
        newKeyDialogVisible.value = true
        
        // 重新加载API密钥列表
        await loadApiKeys()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '生成API密钥失败')
      } finally {
        generatingKey.value = false
      }
    }
    
    // 复制API密钥
    const copyApiKey = () => {
      navigator.clipboard.writeText(newApiKey.value)
        .then(() => {
          ElMessage.success('API密钥已复制到剪贴板')
        })
        .catch(() => {
          ElMessage.error('复制失败，请手动复制')
        })
    }
    
    // 保存API密钥名称
    const saveApiKeyName = async () => {
      keyFormRef.value.validate(async valid => {
        if (valid) {
          try {
            if (keyForm.name) {
              await store.dispatch('user/updateApiKeyName', {
                key_id: apiKeys.value[0].key_id, // 假设新生成的密钥是列表中的第一个
                name: keyForm.name
              })
              
              // 重新加载API密钥列表
              await loadApiKeys()
            }
            
            // 关闭对话框
            newKeyDialogVisible.value = false
            newApiKey.value = ''
          } catch (error) {
            ElMessage.error(error.response?.data?.error || '保存API密钥名称失败')
          }
        }
      })
    }
    
    // 删除API密钥
    const deleteApiKey = async (keyId) => {
      try {
        await store.dispatch('user/deleteApiKey', keyId)
        
        // 重新加载API密钥列表
        await loadApiKeys()
        
        ElMessage.success('API密钥删除成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '删除API密钥失败')
      }
    }
    
    // 加载API密钥列表
    const loadApiKeys = async () => {
      try {
        const response = await store.dispatch('user/fetchApiKeys')
        apiKeys.value = response.data.api_keys || []
      } catch (error) {
        console.error('加载API密钥列表失败', error)
      }
    }
    
    // 加载用户统计数据
    const loadUserStats = async () => {
      try {
        const response = await store.dispatch('user/fetchUserStats')
        Object.assign(userStats, response.data || {})
      } catch (error) {
        console.error('加载用户统计数据失败', error)
      }
    }
    
    // 初始化表单数据
    const initFormData = () => {
      Object.assign(profileForm, {
        username: user.value.username || '',
        email: user.value.email || '',
        changePassword: false,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      })
    }
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      
      try {
        // 确保已加载用户信息
        if (!user.value.id) {
          await store.dispatch('auth/fetchUser')
        }
        
        // 初始化表单数据
        initFormData()
        
        // 加载API密钥列表
        await loadApiKeys()
        
        // 加载用户统计数据
        await loadUserStats()
      } catch (error) {
        console.error('加载数据失败', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      user,
      avatarUrl,
      userInitials,
      userStats,
      loading,
      generatingKey,
      profileForm,
      rules,
      profileFormRef,
      apiKeys,
      newKeyDialogVisible,
      newApiKey,
      keyForm,
      keyRules,
      keyFormRef,
      formatDate,
      getGroupTagType,
      updateProfile,
      resetForm,
      generateApiKey,
      copyApiKey,
      saveApiKeyName,
      deleteApiKey
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.user-info-card, .profile-edit-card, .api-key-card {
  margin-bottom: 20px;
}

.user-info-card {
  text-align: center;
  padding: 20px;
}

.user-avatar {
  margin-bottom: 20px;
}

.user-details {
  margin-bottom: 20px;
}

.user-details h2 {
  margin: 10px 0;
  color: #303133;
}

.user-email {
  color: #606266;
  margin-bottom: 10px;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.new-key-container {
  padding: 10px;
}

.key-warning {
  color: #e6a23c;
  font-weight: bold;
  margin-bottom: 15px;
}

.key-display {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.key-form {
  margin-top: 20px;
}
</style>