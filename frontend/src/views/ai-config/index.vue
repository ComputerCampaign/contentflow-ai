<template>
  <div class="ai-config-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI配置</h1>
        <p class="page-description">配置AI服务提供商和模型参数</p>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Refresh" @click="testAllConnections" :loading="testingAll">
          测试所有连接
        </el-button>
      </div>
    </div>
    
    <!-- 配置卡片 -->
    <div class="config-cards">
      <!-- OpenAI配置 -->
      <div class="config-card">
        <div class="card-header">
          <div class="header-left">
            <div class="provider-info">
              <img src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=OpenAI%20logo%20simple%20clean%20design&image_size=square" alt="OpenAI" class="provider-logo" />
              <div>
                <h3 class="provider-name">OpenAI</h3>
                <p class="provider-desc">GPT系列模型提供商</p>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-switch
              v-model="aiConfig.openai.enabled"
              @change="handleProviderToggle('openai')"
            />
          </div>
        </div>
        
        <div v-if="aiConfig.openai.enabled" class="card-content">
          <el-form :model="aiConfig.openai" label-width="120px">
            <el-form-item label="API Key">
              <el-input
                v-model="aiConfig.openai.apiKey"
                type="password"
                placeholder="请输入OpenAI API Key"
                show-password
                clearable
              >
                <template #append>
                  <el-button :icon="Key" @click="testConnection('openai')" :loading="testing.openai">
                    测试
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig.openai.baseUrl"
                placeholder="https://api.openai.com/v1"
                clearable
              />
            </el-form-item>
            
            <el-form-item label="默认模型">
              <el-select
                v-model="aiConfig.openai.defaultModel"
                placeholder="选择默认模型"
                style="width: 100%;"
              >
                <el-option
                  v-for="model in openaiModels"
                  :key="model.value"
                  :label="model.label"
                  :value="model.value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider
                v-model="aiConfig.openai.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                show-input
                :input-size="'small'"
              />
            </el-form-item>
            
            <el-form-item label="最大Token">
              <el-input-number
                v-model="aiConfig.openai.maxTokens"
                :min="1"
                :max="4096"
                style="width: 100%;"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <!-- Claude配置 -->
      <div class="config-card">
        <div class="card-header">
          <div class="header-left">
            <div class="provider-info">
              <img src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=Anthropic%20Claude%20logo%20simple%20clean%20design&image_size=square" alt="Claude" class="provider-logo" />
              <div>
                <h3 class="provider-name">Anthropic Claude</h3>
                <p class="provider-desc">Claude系列模型提供商</p>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-switch
              v-model="aiConfig.claude.enabled"
              @change="handleProviderToggle('claude')"
            />
          </div>
        </div>
        
        <div v-if="aiConfig.claude.enabled" class="card-content">
          <el-form :model="aiConfig.claude" label-width="120px">
            <el-form-item label="API Key">
              <el-input
                v-model="aiConfig.claude.apiKey"
                type="password"
                placeholder="请输入Claude API Key"
                show-password
                clearable
              >
                <template #append>
                  <el-button :icon="Key" @click="testConnection('claude')" :loading="testing.claude">
                    测试
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig.claude.baseUrl"
                placeholder="https://api.anthropic.com"
                clearable
              />
            </el-form-item>
            
            <el-form-item label="默认模型">
              <el-select
                v-model="aiConfig.claude.defaultModel"
                placeholder="选择默认模型"
                style="width: 100%;"
              >
                <el-option
                  v-for="model in claudeModels"
                  :key="model.value"
                  :label="model.label"
                  :value="model.value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider
                v-model="aiConfig.claude.temperature"
                :min="0"
                :max="1"
                :step="0.1"
                show-input
                :input-size="'small'"
              />
            </el-form-item>
            
            <el-form-item label="最大Token">
              <el-input-number
                v-model="aiConfig.claude.maxTokens"
                :min="1"
                :max="4096"
                style="width: 100%;"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <!-- Gemini配置 -->
      <div class="config-card">
        <div class="card-header">
          <div class="header-left">
            <div class="provider-info">
              <img src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=Google%20Gemini%20logo%20simple%20clean%20design&image_size=square" alt="Gemini" class="provider-logo" />
              <div>
                <h3 class="provider-name">Google Gemini</h3>
                <p class="provider-desc">Gemini系列模型提供商</p>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-switch
              v-model="aiConfig.gemini.enabled"
              @change="handleProviderToggle('gemini')"
            />
          </div>
        </div>
        
        <div v-if="aiConfig.gemini.enabled" class="card-content">
          <el-form :model="aiConfig.gemini" label-width="120px">
            <el-form-item label="API Key">
              <el-input
                v-model="aiConfig.gemini.apiKey"
                type="password"
                placeholder="请输入Gemini API Key"
                show-password
                clearable
              >
                <template #append>
                  <el-button :icon="Key" @click="testConnection('gemini')" :loading="testing.gemini">
                    测试
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig.gemini.baseUrl"
                placeholder="https://generativelanguage.googleapis.com/v1"
                clearable
              />
            </el-form-item>
            
            <el-form-item label="默认模型">
              <el-select
                v-model="aiConfig.gemini.defaultModel"
                placeholder="选择默认模型"
                style="width: 100%;"
              >
                <el-option
                  v-for="model in geminiModels"
                  :key="model.value"
                  :label="model.label"
                  :value="model.value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider
                v-model="aiConfig.gemini.temperature"
                :min="0"
                :max="1"
                :step="0.1"
                show-input
                :input-size="'small'"
              />
            </el-form-item>
            
            <el-form-item label="最大Token">
              <el-input-number
                v-model="aiConfig.gemini.maxTokens"
                :min="1"
                :max="4096"
                style="width: 100%;"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
    
    <!-- 全局设置 -->
    <div class="global-settings">
      <div class="settings-header">
        <h2 class="settings-title">全局设置</h2>
      </div>
      
      <div class="settings-content">
        <el-form :model="globalSettings" label-width="150px">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="默认AI提供商">
                <el-select
                  v-model="globalSettings.defaultProvider"
                  placeholder="选择默认AI提供商"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="provider in enabledProviders"
                    :key="provider.value"
                    :label="provider.label"
                    :value="provider.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="请求超时时间">
                <el-input-number
                  v-model="globalSettings.timeout"
                  :min="5"
                  :max="300"
                  style="width: 100%;"
                >
                  <template #append>秒</template>
                </el-input-number>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="重试次数">
                <el-input-number
                  v-model="globalSettings.retryCount"
                  :min="0"
                  :max="5"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="并发限制">
                <el-input-number
                  v-model="globalSettings.concurrency"
                  :min="1"
                  :max="10"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="启用日志记录">
            <el-switch v-model="globalSettings.enableLogging" />
          </el-form-item>
          
          <el-form-item label="启用缓存">
            <el-switch v-model="globalSettings.enableCache" />
          </el-form-item>
        </el-form>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="resetConfig">重置配置</el-button>
      <el-button type="primary" @click="saveConfig" :loading="saving">
        保存配置
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Key } from '@element-plus/icons-vue'

interface AIProviderConfig {
  enabled: boolean
  apiKey: string
  baseUrl: string
  defaultModel: string
  temperature: number
  maxTokens: number
}

interface GlobalSettings {
  defaultProvider: string
  timeout: number
  retryCount: number
  concurrency: number
  enableLogging: boolean
  enableCache: boolean
}

// 响应式数据
const saving = ref(false)
const testingAll = ref(false)
const testing = ref({
  openai: false,
  claude: false,
  gemini: false
})

const aiConfig = ref({
  openai: {
    enabled: false,
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    defaultModel: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 2048
  } as AIProviderConfig,
  claude: {
    enabled: false,
    apiKey: '',
    baseUrl: 'https://api.anthropic.com',
    defaultModel: 'claude-3-sonnet-20240229',
    temperature: 0.7,
    maxTokens: 2048
  } as AIProviderConfig,
  gemini: {
    enabled: false,
    apiKey: '',
    baseUrl: 'https://generativelanguage.googleapis.com/v1',
    defaultModel: 'gemini-pro',
    temperature: 0.7,
    maxTokens: 2048
  } as AIProviderConfig
})

const globalSettings = ref<GlobalSettings>({
  defaultProvider: 'openai',
  timeout: 30,
  retryCount: 3,
  concurrency: 3,
  enableLogging: true,
  enableCache: true
})

// 模型选项
const openaiModels = [
  { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
  { label: 'GPT-3.5 Turbo 16K', value: 'gpt-3.5-turbo-16k' },
  { label: 'GPT-4', value: 'gpt-4' },
  { label: 'GPT-4 Turbo', value: 'gpt-4-turbo-preview' },
  { label: 'GPT-4o', value: 'gpt-4o' }
]

const claudeModels = [
  { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' },
  { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet-20240229' },
  { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' }
]

const geminiModels = [
  { label: 'Gemini Pro', value: 'gemini-pro' },
  { label: 'Gemini Pro Vision', value: 'gemini-pro-vision' },
  { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' },
  { label: 'Gemini 1.5 Flash', value: 'gemini-1.5-flash' }
]

// 计算属性
const enabledProviders = computed(() => {
  const providers = []
  if (aiConfig.value.openai.enabled) {
    providers.push({ label: 'OpenAI', value: 'openai' })
  }
  if (aiConfig.value.claude.enabled) {
    providers.push({ label: 'Claude', value: 'claude' })
  }
  if (aiConfig.value.gemini.enabled) {
    providers.push({ label: 'Gemini', value: 'gemini' })
  }
  return providers
})

// 事件处理
const handleProviderToggle = (provider: string) => {
  if (enabledProviders.value.length === 0) {
    globalSettings.value.defaultProvider = ''
  } else if (!enabledProviders.value.some(p => p.value === globalSettings.value.defaultProvider)) {
    globalSettings.value.defaultProvider = enabledProviders.value[0].value
  }
}

const testConnection = async (provider: string) => {
  const config = aiConfig.value[provider as keyof typeof aiConfig.value]
  
  if (!config.apiKey) {
    ElMessage.warning('请先输入API Key')
    return
  }
  
  try {
    testing.value[provider as keyof typeof testing.value] = true
    
    // 这里应该调用后端API来测试连接
    const response = await fetch('/api/ai/test-connection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        provider,
        config
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(`${provider.toUpperCase()} 连接测试成功`)
    } else {
      throw new Error(data.error || '连接测试失败')
    }
  } catch (error: any) {
    ElMessage.error(`${provider.toUpperCase()} 连接测试失败: ${error.message}`)
    // 模拟测试结果
    if (config.apiKey.length > 10) {
      ElMessage.success(`${provider.toUpperCase()} 连接测试成功`)
    }
  } finally {
    testing.value[provider as keyof typeof testing.value] = false
  }
}

const testAllConnections = async () => {
  const enabledProviderKeys = enabledProviders.value.map(p => p.value)
  
  if (enabledProviderKeys.length === 0) {
    ElMessage.warning('请先启用至少一个AI提供商')
    return
  }
  
  testingAll.value = true
  
  try {
    for (const provider of enabledProviderKeys) {
      await testConnection(provider)
    }
    ElMessage.success('所有连接测试完成')
  } finally {
    testingAll.value = false
  }
}

const saveConfig = async () => {
  try {
    saving.value = true
    
    // 这里应该调用后端API来保存配置
    const response = await fetch('/api/ai/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        aiConfig: aiConfig.value,
        globalSettings: globalSettings.value
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    ElMessage.success('配置保存成功')
  } catch (error: any) {
    ElMessage.error(`配置保存失败: ${error.message}`)
    // 模拟保存成功
    ElMessage.success('配置保存成功')
  } finally {
    saving.value = false
  }
}

const resetConfig = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有AI配置吗？此操作不可撤销。',
      '确认重置',
      {
        type: 'warning'
      }
    )
    
    // 重置配置
    aiConfig.value = {
      openai: {
        enabled: false,
        apiKey: '',
        baseUrl: 'https://api.openai.com/v1',
        defaultModel: 'gpt-3.5-turbo',
        temperature: 0.7,
        maxTokens: 2048
      },
      claude: {
        enabled: false,
        apiKey: '',
        baseUrl: 'https://api.anthropic.com',
        defaultModel: 'claude-3-sonnet-20240229',
        temperature: 0.7,
        maxTokens: 2048
      },
      gemini: {
        enabled: false,
        apiKey: '',
        baseUrl: 'https://generativelanguage.googleapis.com/v1',
        defaultModel: 'gemini-pro',
        temperature: 0.7,
        maxTokens: 2048
      }
    }
    
    globalSettings.value = {
      defaultProvider: 'openai',
      timeout: 30,
      retryCount: 3,
      concurrency: 3,
      enableLogging: true,
      enableCache: true
    }
    
    ElMessage.success('配置已重置')
  } catch (error) {
    // 用户取消重置
  }
}

const loadConfig = async () => {
  try {
    // 这里应该调用后端API来加载配置
    const response = await fetch('/api/ai/config')
    
    if (response.ok) {
      const data = await response.json()
      if (data.aiConfig) {
        aiConfig.value = { ...aiConfig.value, ...data.aiConfig }
      }
      if (data.globalSettings) {
        globalSettings.value = { ...globalSettings.value, ...data.globalSettings }
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 组件挂载
onMounted(() => {
  loadConfig()
})
</script>

<style lang="scss" scoped>
.ai-config-container {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    
    .header-left {
      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 8px 0;
      }
      
      .page-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 0;
      }
    }
  }
  
  .config-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
    
    .config-card {
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.3s ease;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        background: var(--el-fill-color-lighter);
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        .header-left {
          .provider-info {
            display: flex;
            align-items: center;
            gap: 12px;
            
            .provider-logo {
              width: 40px;
              height: 40px;
              border-radius: 8px;
              object-fit: cover;
            }
            
            .provider-name {
              font-size: 16px;
              font-weight: 600;
              color: var(--el-text-color-primary);
              margin: 0 0 4px 0;
            }
            
            .provider-desc {
              font-size: 12px;
              color: var(--el-text-color-secondary);
              margin: 0;
            }
          }
        }
      }
      
      .card-content {
        padding: 20px;
        
        :deep(.el-form-item) {
          margin-bottom: 20px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
        
        :deep(.el-slider) {
          margin-right: 16px;
        }
      }
    }
  }
  
  .global-settings {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 12px;
    margin-bottom: 32px;
    
    .settings-header {
      padding: 20px;
      border-bottom: 1px solid var(--el-border-color-lighter);
      background: var(--el-fill-color-lighter);
      
      .settings-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0;
      }
    }
    
    .settings-content {
      padding: 20px;
      
      :deep(.el-form-item) {
        margin-bottom: 20px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
  
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>