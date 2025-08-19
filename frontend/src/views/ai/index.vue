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
          <el-button type="info" :loading="aiStore.syncing">
            <el-icon><Refresh /></el-icon>
            同步配置
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="db_to_file">
                <el-icon><Download /></el-icon>
                数据库 → 本地文件
              </el-dropdown-item>
              <el-dropdown-item command="file_to_db">
                <el-icon><Upload /></el-icon>
                本地文件 → 数据库
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" @click="saveCurrentConfig" :loading="saving">
          <el-icon><Document /></el-icon>
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
          
          <el-form :model="aiStore.promptsConfig" label-width="120px">
            <el-card class="config-card">
              <template #header>
                <div class="card-header">
                  <span>默认提示词类型</span>
                </div>
              </template>
              <el-form-item label="默认类型">
                <el-select v-model="aiStore.promptsConfig.default_prompt" style="width: 300px">
                  <el-option 
                    v-for="(prompt, key) in aiStore.promptsConfig.prompts" 
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
                    <el-icon><Plus /></el-icon>
                    添加模板
                  </el-button>
                </div>
              </template>
              
              <div v-for="(prompt, key) in aiStore.promptsConfig.prompts" :key="key" class="prompt-item">
                <div class="prompt-header">
                  <el-input 
                    v-model="promptKeys[key]" 
                    placeholder="模板名称" 
                    style="width: 200px; margin-right: 10px"
                    @blur="updatePromptKey(String(key), promptKeys[key])"
                  />
                  <el-button size="small" type="danger" @click="deletePromptTemplate(String(key))">
                    <el-icon><Delete /></el-icon>
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
          
          <el-form :model="aiStore.modelsConfig" label-width="120px">
            <el-card class="config-card">
              <template #header>
                <div class="card-header">
                  <span>默认模型</span>
                </div>
              </template>
              <el-form-item label="默认模型">
                <el-select v-model="aiStore.modelsConfig.default_model" style="width: 300px">
                  <el-option 
                    v-for="(model, key) in aiStore.modelsConfig.models" 
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
                    <el-icon><Plus /></el-icon>
                    添加模型
                  </el-button>
                </div>
              </template>
              
              <div v-for="(model, key) in aiStore.modelsConfig.models" :key="key" class="model-item">
                <div class="model-header">
                  <el-input 
                    v-model="modelKeys[key]" 
                    placeholder="模型标识" 
                    style="width: 200px; margin-right: 10px"
                    @blur="updateModelKey(String(key), modelKeys[key])"
                  />
                  <el-button size="small" type="danger" @click="deleteModelConfig(String(key))">
                    <el-icon><Delete /></el-icon>
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

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  ArrowDown, 
  Download, 
  Upload, 
  Document, 
  Plus, 
  Delete 
} from '@element-plus/icons-vue'
import { useAIStore } from '@/stores/ai'

// 使用store
const aiStore = useAIStore()

// 响应式数据
const activeTab = ref('prompts')
const saving = ref(false)

// 用于跟踪键名变化
const promptKeys = ref<Record<string, string>>({})
const modelKeys = ref<Record<string, string>>({})

// 加载配置数据
const loadConfigs = async () => {
  try {
    await Promise.all([
      aiStore.fetchPromptsConfig(),
      aiStore.fetchAIModels()
    ])
    
    // 初始化键名跟踪
    promptKeys.value = {}
    Object.keys(aiStore.promptsConfig.prompts).forEach(key => {
      promptKeys.value[key] = key
    })
    
    modelKeys.value = {}
    Object.keys(aiStore.modelsConfig.models).forEach(key => {
      modelKeys.value[key] = key
    })
  } catch (error) {
    ElMessage.error('加载配置失败')
    console.error('加载配置失败:', error)
  }
}

// 保存当前配置
const saveCurrentConfig = async () => {
  saving.value = true
  try {
    if (activeTab.value === 'prompts') {
      await aiStore.savePromptsConfig(aiStore.promptsConfig)
      ElMessage.success('提示词配置保存成功')
    } else {
      // 将配置格式转换为数据库格式并保存
      const modelUpdates = []
      for (const [name, config] of Object.entries(aiStore.modelsConfig.models)) {
        const modelData = {
          name: name,
          model_key: name.toLowerCase().replace(/[^a-z0-9]/g, '_'),
          model: config.model,
          api_key_env: config.api_key_env,
          base_url: config.base_url,
          generation_config: config.generation_config,
          max_retries: config.max_retries,
          timeout: config.timeout,
          is_active: true,
          is_default: name === aiStore.modelsConfig.default_model
        }
        modelUpdates.push(modelData)
      }
      
      // 批量更新模型配置
      for (const modelData of modelUpdates) {
        await aiStore.createAIModel(modelData)
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
const handleSyncCommand = async (command: string) => {
  try {
    await aiStore.syncConfig(command as any)
    
    if (command === 'db_to_file') {
      ElMessage.success('数据库配置已同步到本地文件')
    } else if (command === 'file_to_db') {
      ElMessage.success('本地文件配置已同步到数据库')
      await loadConfigs()
    }
  } catch (error) {
    ElMessage.error('同步配置失败')
    console.error('同步配置失败:', error)
  }
}

// 添加提示词模板
const addPromptTemplate = async () => {
  try {
    const { value: templateName } = await ElMessageBox.prompt(
      '请输入新模板名称',
      '添加提示词模板',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^[a-zA-Z0-9_]+$/,
        inputErrorMessage: '模板名称只能包含字母、数字和下划线'
      }
    )
    
    if (templateName && !aiStore.promptsConfig.prompts[templateName]) {
      aiStore.promptsConfig.prompts[templateName] = {
        system: '',
        user_template: ''
      }
      promptKeys.value[templateName] = templateName
    } else if (templateName) {
      ElMessage.warning('模板名称已存在')
    }
  } catch {
    // 用户取消
  }
}

// 删除提示词模板
const deletePromptTemplate = async (key: string) => {
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
    
    delete aiStore.promptsConfig.prompts[key]
    delete promptKeys.value[key]
    
    // 如果删除的是默认模板，重置默认值
    if (aiStore.promptsConfig.default_prompt === key) {
      const remainingKeys = Object.keys(aiStore.promptsConfig.prompts)
      aiStore.promptsConfig.default_prompt = remainingKeys.length > 0 ? remainingKeys[0] : ''
    }
  } catch {
    // 用户取消删除
  }
}

// 更新提示词键名
const updatePromptKey = (oldKey: string, newKey: string) => {
  if (oldKey !== newKey && newKey && !aiStore.promptsConfig.prompts[newKey]) {
    const promptData = aiStore.promptsConfig.prompts[oldKey]
    delete aiStore.promptsConfig.prompts[oldKey]
    aiStore.promptsConfig.prompts[newKey] = promptData
    
    delete promptKeys.value[oldKey]
    promptKeys.value[newKey] = newKey
    
    // 更新默认值
    if (aiStore.promptsConfig.default_prompt === oldKey) {
      aiStore.promptsConfig.default_prompt = newKey
    }
  } else if (newKey && aiStore.promptsConfig.prompts[newKey] && oldKey !== newKey) {
    ElMessage.warning('模板名称已存在')
    promptKeys.value[oldKey] = oldKey
  }
}

// 添加模型配置
const addModelConfig = async () => {
  try {
    const { value: modelName } = await ElMessageBox.prompt(
      '请输入新模型标识',
      '添加模型配置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^[a-zA-Z0-9_-]+$/,
        inputErrorMessage: '模型标识只能包含字母、数字、下划线和连字符'
      }
    )
    
    if (modelName && !aiStore.modelsConfig.models[modelName]) {
      aiStore.modelsConfig.models[modelName] = {
        name: '',
        model_key: modelName.toLowerCase().replace(/[^a-z0-9]/g, '_'),
        base_url: '',
        model: '',
        api_key_env: '',
        timeout: 60,
        max_retries: 3,
        is_active: true,
        is_default: false,
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
  } catch {
    // 用户取消
  }
}

// 删除模型配置
const deleteModelConfig = async (key: string) => {
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
    
    delete aiStore.modelsConfig.models[key]
    delete modelKeys.value[key]
    
    // 如果删除的是默认模型，重置默认值
    if (aiStore.modelsConfig.default_model === key) {
      const remainingKeys = Object.keys(aiStore.modelsConfig.models)
      aiStore.modelsConfig.default_model = remainingKeys.length > 0 ? remainingKeys[0] : ''
    }
  } catch {
    // 用户取消删除
  }
}

// 更新模型键名
const updateModelKey = (oldKey: string, newKey: string) => {
  if (oldKey !== newKey && newKey && !aiStore.modelsConfig.models[newKey]) {
    const modelData = aiStore.modelsConfig.models[oldKey]
    delete aiStore.modelsConfig.models[oldKey]
    aiStore.modelsConfig.models[newKey] = modelData
    
    delete modelKeys.value[oldKey]
    modelKeys.value[newKey] = newKey
    
    // 更新默认值
    if (aiStore.modelsConfig.default_model === oldKey) {
      aiStore.modelsConfig.default_model = newKey
    }
  } else if (newKey && aiStore.modelsConfig.models[newKey] && oldKey !== newKey) {
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
</style>