<template>
  <div class="ai-model-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>AI模型管理</h1>
        <p>管理和配置AI内容生成模型</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建模型
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="模型名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入模型名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 模型列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="aiStore.loading"
        :data="filteredModels"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="模型名称" width="180">
          <template #default="{ row }">
            <div class="model-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_default" type="success" size="small" style="margin-left: 8px">
                默认
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="model" label="模型标识" width="200" />
        
        <el-table-column prop="base_url" label="API地址" width="250" show-overflow-tooltip />
        
        <el-table-column prop="api_key_env" label="API密钥环境变量" width="180" />
        
        <el-table-column label="生成参数" width="200">
          <template #default="{ row }">
            <div class="generation-params">
              <div>Max Tokens: {{ row.generation_config?.max_tokens || 'N/A' }}</div>
              <div>Temperature: {{ row.generation_config?.temperature || 'N/A' }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="timeout" label="超时(秒)" width="100" />
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleStatusChange(row)"
              active-text="启用"
              inactive-text="禁用"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click">
              <el-button size="small" :icon="More" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleEdit(row)">
                    编辑
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleDelete(row)">
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  Edit,
  Delete,
  More
} from '@element-plus/icons-vue'
import { useAIStore, type AIModel } from '@/stores/ai'
import { formatDate } from '@/utils/date'

const router = useRouter()
const aiStore = useAIStore()

// 搜索表单
const searchForm = ref({
  name: '',
  status: ''
})

// 过滤后的模型列表
const filteredModels = computed(() => {
  let models = aiStore.aiModels
  
  if (searchForm.value.name) {
    models = models.filter(model => 
      model.name.toLowerCase().includes(searchForm.value.name.toLowerCase())
    )
  }
  
  if (searchForm.value.status) {
    const isActive = searchForm.value.status === 'active'
    models = models.filter(model => model.is_active === isActive)
  }
  
  return models
})

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在computed中实现
}

// 重置搜索
const handleReset = () => {
  searchForm.value = {
    name: '',
    status: ''
  }
}

// 创建模型
const handleCreate = () => {
  router.push('/ai/create')
}

// 编辑模型
const handleEdit = (model: AIModel) => {
  router.push(`/ai/edit/${model.id}`)
}

// 删除模型
const handleDelete = async (model: AIModel) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (model.id) {
      await aiStore.deleteAIModel(model.id)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除模型失败:', error)
    }
  }
}

// 状态变更
const handleStatusChange = async (model: AIModel) => {
  try {
    if (model.id) {
      await aiStore.updateAIModel(model.id, { is_active: model.is_active })
      ElMessage.success('状态更新成功')
    }
  } catch (error) {
    ElMessage.error('状态更新失败')
    // 恢复原状态
    model.is_active = !model.is_active
    console.error('更新模型状态失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  aiStore.fetchAIModels()
})
</script>

<style scoped>
.ai-model-list {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 24px;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.model-name {
  display: flex;
  align-items: center;
}

.generation-params {
  font-size: 12px;
  color: #666;
}

.generation-params div {
  margin-bottom: 2px;
}
</style>