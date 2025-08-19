<template>
  <div class="ai-config-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>AI配置管理</h1>
        <p>管理AI内容生成的提示词和模型配置</p>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleSyncCommand" style="margin-right: 10px;">
          <el-button type="info" :loading="syncing">
            <i class="fas fa-sync-alt"></i>
            同步配置
            <i class="el-icon-arrow-down el-icon--right"></i>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="db_to_file">
                <i class="fas fa-download"></i>
                数据库 → 本地文件
              </el-dropdown-item>
              <el-dropdown-item command="file_to_db">
                <i class="fas fa-upload"></i>
                本地文件 → 数据库
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" @click="saveCurrentConfig" :loading="saving">
          <i class="fas fa-save"></i>
          保存配置
        </el-button>
      </div>
    </div>

    <!-- 配置选项卡 -->
    <el-tabs v-model="activeTab" class="config-tabs">
      <!-- 提示词配置 -->
      <el-tab-pane label="提示词配置" name="prompts">
        <div class="config-content">
          <div class="config-header">
            <h3>提示词模板配置</h3>
            <p>配置AI内容生成的提示词模板，支持变量替换</p>
          </div>
          
          <el-form :model="promptsConfig" label-width="120px">
            <el-card class="config-card">
              <template #header>
                <div class="card-header">
                  <span>默认提示词类型</span>
                </div>
              </template>
              <el-form-item label="默认类型">
                <el-select v-model="promptsConfig.default_prompt" style="width: 300px">
                  <el-option 
                    v-for="(prompt, key) in promptsConfig.prompts" 
                    :key="key" 
                    :label="key" 
                    :value="key"
                  />
                </el-select>
              </el-form-item>
            </el-card>

            <el-card class="config-card">
              <template #header>
                <div class="card-header">
                  <span>提示词模板</span>
                  <el-button size="small" type="primary" @click="addPromptTemplate">
                    <i class="fas fa-plus"></i>
                    添加模板
                  </el-button>
                </div>
              </template>
              
              <div v-for="(prompt, key) in promptsConfig.prompts" :key="key" class="prompt-item">
                <div class="prompt-header">
                  <el-input 
                    v-model="promptKeys[key]" 
                    placeholder="模板名称" 
                    style="width: 200px; margin-right: 10px"
                    @blur="updatePromptKey(key, promptKeys[key])"
                  />
                  <el-button size="small" type="danger" @click="deletePromptTemplate(key)">
                    <i class="fas fa-trash"></i>
                    删除
                  </el-button>
                </div>
                
                <el-form-item label="系统提示词" class="prompt-field">
                  <el-input 
                    v-model="prompt.system" 
                    type="textarea" 
                    :rows="3" 
                    placeholder="请输入系统提示词"
                  />
                </el-form-item>
                
                <el-form-item label="用户模板" class="prompt-field">
                  <el-input 
                    v-model="prompt.user_template" 
                    type="textarea" 
                    :rows="5" 
                    placeholder="请输入用户提示词模板，支持变量如 {title}, {description}, {images}, {comments}"
                  />
                  <div class="template-help">
                    <el-text type="info" size="small">
                      支持的变量：{title} - 标题，{description} - 描述，{images} - 图片信息，{comments} - 评论信息
                    </el-text>
                  </div>
                </el-form-item>
              </div>
            </el-card>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 模型配置 -->
      <el-tab-pane label="模型配置" name="models">
        <div class="config-content">
          <div class="config-header">
            <h3>AI模型配置</h3>
            <p>配置AI内容生成使用的模型参数和API设置</p>
          </div>
          
          <el-form :model="modelsConfig" label-width="120px">
            <el-card class="config-card">
              <template #header>
                <div class="card-header">
                  <span>默认模型</span>
                </div>
              </template>
              <el-form-item label="默认模型">
                <el-select v-model="modelsConfig.default_model" style="width: 300px">
                  <el-option 
                    v-for="(model, key) in modelsConfig.models" 
                    :key="key" 
                    :label="model.name" 
                    :value="key"
                  />
                </el-select>
              </el-form-item>
            </el-card>

            <el-card class="config-card">
              <template #header>
                <div class="card-header">
                  <span>模型配置</span>
                  <el-button size="small" type="primary" @click="addModelConfig">
                    <i class="fas fa-plus"></i>
                    添加模型
                  </el-button>
                </div>
              </template>
              
              <div v-for="(model, key) in modelsConfig.models" :key="key" class="model-item">
                <div class="model-header">
                  <el-input 
                    v-model="modelKeys[key]" 
                    placeholder="模型标识" 
                    style="width: 200px; margin-right: 10px"
                    @blur="updateModelKey(key, modelKeys[key])"
                  />
                  <el-button size="small" type="danger" @click="deleteModelConfig(key)">
                    <i class="fas fa-trash"></i>
                    删除
                  </el-button>
                </div>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="模型名称" class="model-field">
                      <el-input v-model="model.name" placeholder="请输入模型显示名称" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="模型标识" class="model-field">
                      <el-input v-model="model.model" placeholder="请输入模型标识" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="API地址" class="model-field">
                      <el-input v-model="model.base_url" placeholder="请输入API基础地址" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="API密钥环境变量" class="model-field">
                      <el-input v-model="model.api_key_env" placeholder="如：OPENAI_API_KEY" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="超时时间" class="model-field">
                      <el-input-number v-model="model.timeout" :min="1" :max="300" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="最大重试" class="model-field">
                      <el-input-number v-model="model.max_retries" :min="0" :max="10" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-divider content-position="left">生成参数配置</el-divider>
                
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="最大Token" class="model-field">
                      <el-input-number v-model="model.generation_config.max_tokens" :min="1" :max="8192" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="温度" class="model-field">
                      <el-input-number v-model="model.generation_config.temperature" :min="0" :max="2" :step="0.1" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="Top P" class="model-field">
                      <el-input-number v-model="model.generation_config.top_p" :min="0" :max="1" :step="0.1" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="频率惩罚" class="model-field">
                      <el-input-number v-model="model.generation_config.frequency_penalty" :min="-2" :max="2" :step="0.1" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="存在惩罚" class="model-field">
                      <el-input-number v-model="model.generation_config.presence_penalty" :min="-2" :max="2" :step="0.1" style="width: 100%" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// 响应式数据
const activeTab = ref('prompts')
const saving = ref(false)
const loading = ref(false)
const syncing = ref(false)

// 配置数据
const promptsConfig = reactive({
  prompts: {},
  default_prompt: '',
  _note: ''
})

const modelsConfig = reactive({
  models: {},
  default_model: '',
  _note: ''
})

// 用于跟踪键名变化
const promptKeys = ref({})
const modelKeys = ref({})

// 加载配置数据
const loadConfigs = async () => {
  loading.value = true
  try {
    // 加载提示词配置
    const promptsResponse = await request.get('/ai-config/prompts')
    if (promptsResponse.data) {
      Object.assign(promptsConfig, promptsResponse.data)
    }
    
    // 初始化提示词键名跟踪
    promptKeys.value = {}
    Object.keys(promptsConfig.prompts).forEach(key => {
      promptKeys.value[key] = key
    })
    
    // 加载模型配置 - 从数据库获取
    const modelsResponse = await request.get('/ai-config/models')
    if (modelsResponse.data?.models) {
      // 将数据库模型转换为配置格式
      const models = {}
      modelsResponse.data.models.forEach(model => {
        models[model.name] = {
          model: model.model,  // 修正字段名
          api_key_env: model.api_key_env,
          base_url: model.base_url,
          generation_config: model.generation_config,
          max_retries: model.max_retries,
          timeout: model.timeout
        }
      })
      
      modelsConfig.models = models
      modelsConfig.default_model = modelsResponse.data.default_model || ''
    }
    
    // 初始化模型键名跟踪
    modelKeys.value = {}
    Object.keys(modelsConfig.models).forEach(key => {
      modelKeys.value[key] = key
    })
    
  } catch (error) {
    ElMessage.error('加载配置失败')
    console.error('加载配置失败:', error)
  } finally {
    loading.value = false
  }
}

// 保存当前配置
const saveCurrentConfig = async () => {
  saving.value = true
  try {
    if (activeTab.value === 'prompts') {
      const response = await request.put('/ai-config/prompts', promptsConfig)
      if (response.data) {
        ElMessage.success('提示词配置保存成功')
      } else {
        throw new Error('保存失败')
      }
    } else {
      // 将配置格式转换为数据库格式并保存
      const modelUpdates = []
      Object.entries(modelsConfig.models).forEach(([name, config]) => {
        modelUpdates.push({
          name: name,
          model_key: name.toLowerCase().replace(/[^a-z0-9]/g, '_'),  // 生成model_key
          model: config.model,
          api_key_env: config.api_key_env,
          base_url: config.base_url,
          generation_config: config.generation_config,
          max_retries: config.max_retries,
          timeout: config.timeout,
          is_active: true,
          is_default: name === modelsConfig.default_model
        })
      })
      
      // 批量更新模型配置
      for (const modelData of modelUpdates) {
        await request.post('/ai-config/models', modelData)
      }
      
      ElMessage.success('模型配置保存成功')
    }
  } catch (error) {
    ElMessage.error('保存配置失败')
    console.error('保存配置失败:', error)
  } finally {
    saving.value = false
  }
}

// 处理同步命令
const handleSyncCommand = async (command) => {
  syncing.value = true
  try {
    let response
    if (command === 'db_to_file') {
      response = await request.post('/ai-config/sync/to-json')
      if (response.data) {
        ElMessage.success('数据库配置已同步到本地文件')
      } else {
        throw new Error('同步失败')
      }
    } else if (command === 'file_to_db') {
      response = await request.post('/ai-config/sync/from-json')
      if (response.data) {
        ElMessage.success('本地文件配置已同步到数据库')
        // 重新加载配置以显示最新数据
        await loadConfigs()
      } else {
        throw new Error('同步失败')
      }
    } else if (command === 'bidirectional') {
      response = await request.post('/ai-config/sync/bidirectional')
      if (response.data) {
        ElMessage.success('双向同步完成')
        await loadConfigs()
      } else {
        throw new Error('同步失败')
      }
    }
  } catch (error) {
    ElMessage.error('同步配置失败')
    console.error('同步配置失败:', error)
  } finally {
    syncing.value = false
  }
}

// 添加提示词模板
const addPromptTemplate = async () => {
  const { value: templateName } = await ElMessageBox.prompt(
    '请输入新模板名称',
    '添加提示词模板',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^[a-zA-Z0-9_]+$/,
      inputErrorMessage: '模板名称只能包含字母、数字和下划线'
    }
  ).catch(() => ({ value: null }))
  
  if (templateName && !promptsConfig.prompts[templateName]) {
    promptsConfig.prompts[templateName] = {
      system: '',
      user_template: ''
    }
    promptKeys.value[templateName] = templateName
  } else if (templateName) {
    ElMessage.warning('模板名称已存在')
  }
}

// 删除提示词模板
const deletePromptTemplate = async (key) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除提示词模板 "${key}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    delete promptsConfig.prompts[key]
    delete promptKeys.value[key]
    
    // 如果删除的是默认模板，重置默认值
    if (promptsConfig.default_prompt === key) {
      const remainingKeys = Object.keys(promptsConfig.prompts)
      promptsConfig.default_prompt = remainingKeys.length > 0 ? remainingKeys[0] : ''
    }
  } catch {
    // 用户取消删除
  }
}

// 更新提示词键名
const updatePromptKey = (oldKey, newKey) => {
  if (oldKey !== newKey && newKey && !promptsConfig.prompts[newKey]) {
    const promptData = promptsConfig.prompts[oldKey]
    delete promptsConfig.prompts[oldKey]
    promptsConfig.prompts[newKey] = promptData
    
    delete promptKeys.value[oldKey]
    promptKeys.value[newKey] = newKey
    
    // 更新默认值
    if (promptsConfig.default_prompt === oldKey) {
      promptsConfig.default_prompt = newKey
    }
  } else if (newKey && promptsConfig.prompts[newKey] && oldKey !== newKey) {
    ElMessage.warning('模板名称已存在')
    promptKeys.value[oldKey] = oldKey
  }
}

// 添加模型配置
const addModelConfig = async () => {
  const { value: modelName } = await ElMessageBox.prompt(
    '请输入新模型标识',
    '添加模型配置',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^[a-zA-Z0-9_-]+$/,
      inputErrorMessage: '模型标识只能包含字母、数字、下划线和连字符'
    }
  ).catch(() => ({ value: null }))
  
  if (modelName && !modelsConfig.models[modelName]) {
    modelsConfig.models[modelName] = {
      name: '',
      base_url: '',
      model: '',
      api_key_env: '',
      timeout: 60,
      max_retries: 3,
      generation_config: {
        max_tokens: 2000,
        temperature: 0.7,
        top_p: 0.9,
        frequency_penalty: 0.0,
        presence_penalty: 0.0
      }
    }
    modelKeys.value[modelName] = modelName
  } else if (modelName) {
    ElMessage.warning('模型标识已存在')
  }
}

// 删除模型配置
const deleteModelConfig = async (key) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型配置 "${key}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    delete modelsConfig.models[key]
    delete modelKeys.value[key]
    
    // 如果删除的是默认模型，重置默认值
    if (modelsConfig.default_model === key) {
      const remainingKeys = Object.keys(modelsConfig.models)
      modelsConfig.default_model = remainingKeys.length > 0 ? remainingKeys[0] : ''
    }
  } catch {
    // 用户取消删除
  }
}

// 更新模型键名
const updateModelKey = (oldKey, newKey) => {
  if (oldKey !== newKey && newKey && !modelsConfig.models[newKey]) {
    const modelData = modelsConfig.models[oldKey]
    delete modelsConfig.models[oldKey]
    modelsConfig.models[newKey] = modelData
    
    delete modelKeys.value[oldKey]
    modelKeys.value[newKey] = newKey
    
    // 更新默认值
    if (modelsConfig.default_model === oldKey) {
      modelsConfig.default_model = newKey
    }
  } else if (newKey && modelsConfig.models[newKey] && oldKey !== newKey) {
    ElMessage.warning('模型标识已存在')
    modelKeys.value[oldKey] = oldKey
  }
}

// 组件挂载时加载配置
onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.ai-config-page {
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

.config-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.config-content {
  padding: 20px 0;
}

.config-header {
  margin-bottom: 20px;
}

.config-header h3 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 18px;
}

.config-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prompt-item, .model-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.prompt-header, .model-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.prompt-field, .model-field {
  margin-bottom: 15px;
}

.template-help {
  margin-top: 5px;
}

.fas {
  margin-right: 5px;
}
</style>