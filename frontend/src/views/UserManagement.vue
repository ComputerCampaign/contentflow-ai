<template>
  <div class="user-management-container">
    <el-row :gutter="20">
      <!-- 左侧：用户列表 -->
      <el-col :span="16">
        <el-card class="user-list-card">
          <template #header>
            <div class="card-header">
              <span>用户列表</span>
              <div class="header-actions">
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索用户"
                  style="width: 200px"
                  clearable
                ></el-input>
              </div>
            </div>
          </template>
          
          <el-table 
            v-if="!loading && users.length > 0" 
            :data="filteredUsers" 
            style="width: 100%"
            @row-click="handleUserClick"
          >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="username" label="用户名" width="150"></el-table-column>
            <el-table-column prop="email" label="邮箱"></el-table-column>
            <el-table-column prop="group_name" label="用户组" width="120">
              <template #default="scope">
                <el-tag :type="getGroupTagType(scope.row.group_name)">
                  {{ scope.row.group_name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click.stop="editUser(scope.row)"
                  :disabled="!isAdmin"
                >编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-else-if="!loading && users.length === 0" class="empty-data">
            <el-empty description="暂无用户数据"></el-empty>
          </div>
          
          <div v-else class="loading-placeholder">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div class="pagination-container" v-if="users.length > 0">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="filteredUsers.length"
              :page-size="pageSize"
              :current-page.sync="currentPage"
              @current-change="handlePageChange"
            ></el-pagination>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：用户组管理 -->
      <el-col :span="8">
        <el-card class="user-group-card">
          <template #header>
            <div class="card-header">
              <span>用户组管理</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="showCreateGroupForm"
                :disabled="!isAdmin"
              >新建用户组</el-button>
            </div>
          </template>
          
          <div v-if="loading" class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="groups.length === 0" class="empty-data">
            <el-empty description="暂无用户组数据"></el-empty>
          </div>
          
          <el-table 
            v-else 
            :data="groups" 
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="name" label="组名"></el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 用户编辑对话框 -->
    <el-dialog 
      title="编辑用户" 
      v-model="userDialogVisible" 
      width="500px"
    >
      <el-form 
        v-if="currentUser" 
        :model="userForm" 
        :rules="userRules" 
        ref="userFormRef" 
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" disabled></el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email"></el-input>
        </el-form-item>
        
        <el-form-item label="用户组" prop="group_id">
          <el-select v-model="userForm.group_id" placeholder="请选择用户组">
            <el-option 
              v-for="group in groups" 
              :key="group.id" 
              :label="group.name" 
              :value="group.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="重置密码">
          <el-switch v-model="userForm.reset_password"></el-switch>
        </el-form-item>
        
        <el-form-item label="新密码" prop="password" v-if="userForm.reset_password">
          <el-input v-model="userForm.password" type="password" show-password></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="updateUser">确认</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 用户组创建对话框 -->
    <el-dialog 
      title="创建用户组" 
      v-model="groupDialogVisible" 
      width="500px"
    >
      <el-form 
        :model="groupForm" 
        :rules="groupRules" 
        ref="groupFormRef" 
        label-width="100px"
      >
        <el-form-item label="组名" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入组名"></el-input>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="groupForm.description" 
            type="textarea" 
            placeholder="请输入用户组描述"
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="groupDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="createGroup">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'UserManagement',
  setup() {
    const store = useStore()
    
    const loading = ref(false)
    const users = ref([])
    const groups = ref([])
    const searchQuery = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const userDialogVisible = ref(false)
    const groupDialogVisible = ref(false)
    const currentUser = ref(null)
    const userFormRef = ref(null)
    const groupFormRef = ref(null)
    
    // 用户表单数据
    const userForm = reactive({
      id: '',
      username: '',
      email: '',
      group_id: '',
      reset_password: false,
      password: ''
    })
    
    // 用户组表单数据
    const groupForm = reactive({
      name: '',
      description: ''
    })
    
    // 表单验证规则
    const userRules = {
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      group_id: [
        { required: true, message: '请选择用户组', trigger: 'change' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur', validator: (rule, value, callback) => {
          if (userForm.reset_password && !value) {
            callback(new Error('请输入密码'))
          } else {
            callback()
          }
        }}
      ]
    }
    
    const groupRules = {
      name: [
        { required: true, message: '请输入组名', trigger: 'blur' },
        { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
      ]
    }
    
    // 计算属性
    const filteredUsers = computed(() => {
      if (!searchQuery.value) return users.value
      
      const query = searchQuery.value.toLowerCase()
      return users.value.filter(user => 
        user.username.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        user.group_name.toLowerCase().includes(query)
      )
    })
    
    // 分页后的用户列表
    const paginatedUsers = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredUsers.value.slice(start, end)
    })
    
    // 当前用户是否为管理员
    const isAdmin = computed(() => {
      const currentUser = store.getters['auth/user']
      return currentUser && currentUser.group_name === 'admin'
    })
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    // 获取用户组标签类型
    const getGroupTagType = (groupName) => {
      switch (groupName.toLowerCase()) {
        case 'admin':
          return 'danger'
        case 'user':
          return 'primary'
        default:
          return 'info'
      }
    }
    
    // 处理用户点击
    const handleUserClick = (user) => {
      currentUser.value = user
    }
    
    // 处理分页变化
    const handlePageChange = (page) => {
      currentPage.value = page
    }
    
    // 编辑用户
    const editUser = (user) => {
      currentUser.value = user
      
      // 填充表单数据
      Object.assign(userForm, {
        id: user.id,
        username: user.username,
        email: user.email,
        group_id: user.group_id,
        reset_password: false,
        password: ''
      })
      
      userDialogVisible.value = true
    }
    
    // 更新用户
    const updateUser = () => {
      userFormRef.value.validate(async valid => {
        if (valid) {
          loading.value = true
          
          try {
            const userData = {
              id: userForm.id,
              email: userForm.email,
              group_id: userForm.group_id
            }
            
            // 如果需要重置密码，添加密码字段
            if (userForm.reset_password) {
              userData.password = userForm.password
            }
            
            await store.dispatch('user/updateUser', userData)
            
            // 重新加载用户列表
            await loadUsers()
            
            // 关闭对话框
            userDialogVisible.value = false
            
            ElMessage.success('用户更新成功')
          } catch (error) {
            ElMessage.error(error.response?.data?.error || '更新用户失败')
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    // 显示创建用户组表单
    const showCreateGroupForm = () => {
      // 重置表单
      Object.assign(groupForm, {
        name: '',
        description: ''
      })
      
      groupDialogVisible.value = true
    }
    
    // 创建用户组
    const createGroup = () => {
      groupFormRef.value.validate(async valid => {
        if (valid) {
          loading.value = true
          
          try {
            await store.dispatch('user/createGroup', groupForm)
            
            // 重新加载用户组列表
            await loadGroups()
            
            // 关闭对话框
            groupDialogVisible.value = false
            
            ElMessage.success('用户组创建成功')
          } catch (error) {
            ElMessage.error(error.response?.data?.error || '创建用户组失败')
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      
      try {
        const response = await store.dispatch('user/fetchUsers')
        users.value = response.data.users || []
      } catch (error) {
        console.error('加载用户列表失败', error)
      } finally {
        loading.value = false
      }
    }
    
    // 加载用户组列表
    const loadGroups = async () => {
      loading.value = true
      
      try {
        const response = await store.dispatch('user/fetchGroups')
        groups.value = response.data.groups || []
      } catch (error) {
        console.error('加载用户组列表失败', error)
      } finally {
        loading.value = false
      }
    }
    
    // 加载数据
    const loadData = async () => {
      await Promise.all([
        loadUsers(),
        loadGroups()
      ])
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      loading,
      users,
      groups,
      filteredUsers,
      paginatedUsers,
      searchQuery,
      currentPage,
      pageSize,
      userDialogVisible,
      groupDialogVisible,
      currentUser,
      userForm,
      groupForm,
      userRules,
      groupRules,
      userFormRef,
      groupFormRef,
      isAdmin,
      formatDate,
      getGroupTagType,
      handleUserClick,
      handlePageChange,
      editUser,
      updateUser,
      showCreateGroupForm,
      createGroup
    }
  }
}
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.user-list-card, .user-group-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.loading-placeholder {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.el-table {
  --el-table-row-hover-bg-color: #f5f7fa;
}

.el-table .el-table__row {
  cursor: pointer;
}
</style>