import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import apiClient from '@/utils/request'

export interface AIModel {
  id?: string
  name: string
  model_key: string
  model: string
  api_key_env: string
  base_url: string
  generation_config: {
    max_tokens: number
    temperature: number
    top_p: number
    frequency_penalty: number
    presence_penalty: number
    stop_sequences?: string[]
  }
  max_retries: number
  timeout: number
  is_active: boolean
  is_default: boolean
  system_prompt?: string
  created_at?: string
  updated_at?: string
}

export interface PromptTemplate {
  [key: string]: {
    system: string
    user_template: string
  }
}

export interface PromptsConfig {
  prompts: PromptTemplate
  default_prompt: string
  _note?: string
}

export interface ModelsConfig {
  models: { [key: string]: Omit<AIModel, 'id' | 'created_at' | 'updated_at'> }
  default_model: string
  _note?: string
}

export type UpdateAIModelParams = Partial<AIModel>
export type CreateAIModelParams = Omit<AIModel, 'id' | 'created_at' | 'updated_at'>

export const useAIStore = defineStore('ai', () => {
  // 状态
  const aiModels = ref<AIModel[]>([])
  const promptsConfig = reactive<PromptsConfig>({
    prompts: {},
    default_prompt: '',
    _note: ''
  })
  const modelsConfig = reactive<ModelsConfig>({
    models: {},
    default_model: '',
    _note: ''
  })
  const loading = ref(false)
  const syncing = ref(false)

  // 获取AI模型列表
  const fetchAIModels = async () => {
    loading.value = true
    try {
      const response = await apiClient.get('/ai-config/models')
      if (response.data?.models) {
        aiModels.value = response.data.models
        
        // 同时更新modelsConfig
        const models: { [key: string]: any } = {}
        response.data.models.forEach((model: AIModel) => {
          models[model.name] = {
            name: model.name,
            model_key: model.model_key,
            model: model.model,
            api_key_env: model.api_key_env,
            base_url: model.base_url,
            generation_config: model.generation_config,
            max_retries: model.max_retries,
            timeout: model.timeout,
            is_active: model.is_active,
            is_default: model.is_default
          }
        })
        
        modelsConfig.models = models
        modelsConfig.default_model = response.data.default_model || ''
      }
    } catch (error) {
      console.error('获取AI模型列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取提示词配置
  const fetchPromptsConfig = async () => {
    loading.value = true
    try {
      const response = await apiClient.get('/ai-config/prompts')
      if (response.data) {
        Object.assign(promptsConfig, response.data)
      }
    } catch (error) {
      console.error('获取提示词配置失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建AI模型
  const createAIModel = async (modelData: Omit<AIModel, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const response = await apiClient.post('/ai-config/models', modelData)
      if (response.data) {
        await fetchAIModels() // 重新获取列表
        return response.data
      }
    } catch (error) {
      console.error('创建AI模型失败:', error)
      throw error
    }
  }

  // 更新AI模型
  const updateAIModel = async (id: string, modelData: Partial<AIModel>) => {
    try {
      const response = await apiClient.put(`/ai-config/models/${id}`, modelData)
      if (response.data) {
        await fetchAIModels() // 重新获取列表
        return response.data
      }
    } catch (error) {
      console.error('更新AI模型失败:', error)
      throw error
    }
  }

  // 删除AI模型
  const deleteAIModel = async (id: string) => {
    try {
      await apiClient.delete(`/ai-config/models/${id}`)
      await fetchAIModels() // 重新获取列表
    } catch (error) {
      console.error('删除AI模型失败:', error)
      throw error
    }
  }

  // 保存提示词配置
  const savePromptsConfig = async (config: PromptsConfig) => {
    try {
      const response = await apiClient.put('/ai-config/prompts', config)
      if (response.data) {
        Object.assign(promptsConfig, config)
        return response.data
      }
    } catch (error) {
      console.error('保存提示词配置失败:', error)
      throw error
    }
  }

  // 同步配置
  const syncConfig = async (direction: 'db_to_file' | 'file_to_db' | 'bidirectional') => {
    syncing.value = true
    try {
      let endpoint = ''
      switch (direction) {
        case 'db_to_file':
          endpoint = '/ai-config/sync/to-json'
          break
        case 'file_to_db':
          endpoint = '/ai-config/sync/from-json'
          break
        case 'bidirectional':
          endpoint = '/ai-config/sync/bidirectional'
          break
      }
      
      const response = await apiClient.post(endpoint)
      if (response.data) {
        // 重新加载配置
        await Promise.all([fetchAIModels(), fetchPromptsConfig()])
        return response.data
      }
    } catch (error) {
      console.error('同步配置失败:', error)
      throw error
    } finally {
      syncing.value = false
    }
  }

  // 测试AI模型
  const testAIModel = async (modelId: string, testPrompt: string) => {
    try {
      const response = await apiClient.post(`/ai-config/models/${modelId}/test`, {
        prompt: testPrompt
      })
      return response.data
    } catch (error) {
      console.error('测试AI模型失败:', error)
      throw error
    }
  }

  return {
    // 状态
    aiModels,
    promptsConfig,
    modelsConfig,
    loading,
    syncing,
    
    // 方法
    fetchAIModels,
    fetchPromptsConfig,
    createAIModel,
    updateAIModel,
    deleteAIModel,
    savePromptsConfig,
    syncConfig,
    testAIModel
  }
})