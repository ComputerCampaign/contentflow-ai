<template>
  <div class="user-management-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户管理</h1>
        <p class="page-description">管理系统用户账户、权限和角色</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="exportUsers" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出用户
          </el-button>
          <el-button @click="showCreateDialog" type="primary">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="searchForm.email"
            placeholder="请输入邮箱"
            clearable
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择角色" clearable style="width: 150px;">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px;">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="锁定" value="locked" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
          </template>
        </el-table-column>
        
        <el-table-column prop="username" label="用户名" min-width="120" />
        
        <el-table-column prop="email" label="邮箱" min-width="180" />
        
        <el-table-column prop="realName" label="真实姓名" min-width="120" />
        
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="lastLoginAt" label="最后登录" width="160">
          <template #default="{ row }">
            {{ formatDate(row.lastLoginAt) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="viewUser(row)">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button size="small" @click="editUser(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button 
                size="small" 
                :type="row.status === 'active' ? 'warning' : 'success'"
                @click="toggleUserStatus(row)"
              >
                <el-icon v-if="row.status === 'active'"><Lock /></el-icon>
                <el-icon v-else><Unlock /></el-icon>
              </el-button>
              <el-button size="small" type="danger" @click="deleteUser(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 批量操作 -->
    <div v-if="selectedUsers.length > 0" class="batch-actions">
      <el-card>
        <div class="batch-info">
          <span>已选择 {{ selectedUsers.length }} 个用户</span>
          <div class="batch-buttons">
            <el-button @click="batchEnable" type="success" size="small">
              <el-icon><Check /></el-icon>
              批量启用
            </el-button>
            <el-button @click="batchDisable" type="warning" size="small">
              <el-icon><Lock /></el-icon>
              批量禁用
            </el-button>
            <el-button @click="batchDelete" type="danger" size="small">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 用户详情/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增用户' : dialogMode === 'edit' ? '编辑用户' : '用户详情'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
        :disabled="dialogMode === 'view'"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="userForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item v-if="dialogMode === 'create'" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="userForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
            <el-radio label="locked">锁定</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="userForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button v-if="dialogMode !== 'view'" type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Plus,
  Search,
  RefreshLeft,
  User,
  View,
  Edit,
  Lock,
  Unlock,
  Delete,
  Check
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create') // create, edit, view
const selectedUsers = ref([])

// 搜索表单
const searchForm = reactive({
  username: '',
  email: '',
  role: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 用户列表
const userList = ref([])

// 用户表单
const userForm = reactive({
  id: null,
  username: '',
  email: '',
  realName: '',
  phone: '',
  password: '',
  role: 'user',
  status: 'active',
  remark: ''
})

// 表单验证规则
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const userFormRef = ref()

// 模拟用户数据
const mockUsers = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    realName: '系统管理员',
    phone: '13800138000',
    role: 'admin',
    status: 'active',
    avatar: '',
    lastLoginAt: '2024-01-15 10:30:00',
    createdAt: '2024-01-01 00:00:00',
    remark: '系统管理员账户'
  },
  {
    id: 2,
    username: 'user001',
    email: 'user001@example.com',
    realName: '张三',
    phone: '13800138001',
    role: 'user',
    status: 'active',
    avatar: '',
    lastLoginAt: '2024-01-15 09:15:00',
    createdAt: '2024-01-02 10:00:00',
    remark: '普通用户'
  },
  {
    id: 3,
    username: 'user002',
    email: 'user002@example.com',
    realName: '李四',
    phone: '13800138002',
    role: 'user',
    status: 'inactive',
    avatar: '',
    lastLoginAt: '2024-01-10 14:20:00',
    createdAt: '2024-01-03 15:30:00',
    remark: '已禁用用户'
  }
]

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    userList.value = mockUsers
    pagination.total = mockUsers.length
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索用户
const handleSearch = () => {
  fetchUsers()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  fetchUsers()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchUsers()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchUsers()
}

// 选择用户
const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetUserForm()
  dialogVisible.value = true
}

// 查看用户
const viewUser = (user) => {
  dialogMode.value = 'view'
  Object.assign(userForm, user)
  dialogVisible.value = true
}

// 编辑用户
const editUser = (user) => {
  dialogMode.value = 'edit'
  Object.assign(userForm, user)
  dialogVisible.value = true
}

// 切换用户状态
const toggleUserStatus = async (user) => {
  const action = user.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    user.status = user.status === 'active' ? 'inactive' : 'active'
    ElMessage.success(`用户${action}成功`)
  } catch {
    // 用户取消操作
  }
}

// 删除用户
const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    const index = userList.value.findIndex(u => u.id === user.id)
    if (index > -1) {
      userList.value.splice(index, 1)
      pagination.total--
    }
    ElMessage.success('用户删除成功')
  } catch {
    // 用户取消操作
  }
}

// 批量操作
const batchEnable = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要启用选中的 ${selectedUsers.value.length} 个用户吗？`,
      '确认操作',
      { type: 'warning' }
    )
    
    selectedUsers.value.forEach(user => {
      user.status = 'active'
    })
    ElMessage.success('批量启用成功')
  } catch {
    // 用户取消操作
  }
}

const batchDisable = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要禁用选中的 ${selectedUsers.value.length} 个用户吗？`,
      '确认操作',
      { type: 'warning' }
    )
    
    selectedUsers.value.forEach(user => {
      user.status = 'inactive'
    })
    ElMessage.success('批量禁用成功')
  } catch {
    // 用户取消操作
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复！`,
      '确认删除',
      { type: 'error' }
    )
    
    const selectedIds = selectedUsers.value.map(user => user.id)
    userList.value = userList.value.filter(user => !selectedIds.includes(user.id))
    pagination.total -= selectedUsers.value.length
    selectedUsers.value = []
    ElMessage.success('批量删除成功')
  } catch {
    // 用户取消操作
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    submitting.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (dialogMode.value === 'create') {
      const newUser = {
        ...userForm,
        id: Date.now(),
        avatar: '',
        lastLoginAt: null,
        createdAt: new Date().toLocaleString()
      }
      userList.value.unshift(newUser)
      pagination.total++
      ElMessage.success('用户创建成功')
    } else if (dialogMode.value === 'edit') {
      const index = userList.value.findIndex(u => u.id === userForm.id)
      if (index > -1) {
        Object.assign(userList.value[index], userForm)
      }
      ElMessage.success('用户更新成功')
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

// 重置用户表单
const resetUserForm = () => {
  Object.assign(userForm, {
    id: null,
    username: '',
    email: '',
    realName: '',
    phone: '',
    password: '',
    role: 'user',
    status: 'active',
    remark: ''
  })
  
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

// 导出用户
const exportUsers = async () => {
  exporting.value = true
  try {
    // 模拟导出操作
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('用户数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 工具函数
const getRoleTagType = (role) => {
  const types = {
    admin: 'danger',
    user: 'primary',
    guest: 'info'
  }
  return types[role] || 'info'
}

const getRoleLabel = (role) => {
  const labels = {
    admin: '管理员',
    user: '普通用户',
    guest: '访客'
  }
  return labels[role] || '未知'
}

const getStatusTagType = (status) => {
  const types = {
    active: 'success',
    inactive: 'warning',
    locked: 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    active: '启用',
    inactive: '禁用',
    locked: '锁定'
  }
  return labels[status] || '未知'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.user-management-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
    
    .page-description {
      margin: 0;
      color: var(--el-text-color-regular);
    }
  }
}

.search-card {
  margin-bottom: 16px;
  
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.table-card {
  .pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  
  .el-card {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .batch-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    
    .batch-buttons {
      display: flex;
      gap: 8px;
    }
  }
}

.dialog-footer {
  text-align: right;
}
</style>