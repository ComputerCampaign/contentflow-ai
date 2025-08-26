import { BaseApiService } from './base'
import apiAdapter, { type StandardResponse } from '@/utils/api-adapter'

// AI模型配置接口
export interface AIModelConfig {
  id: string
  name: string
  model_key: string
  description?: string
  api_key_env: string
  base_url: string
  model: string
  max_tokens: number
  temperature: number
  top_p: number
  frequency_penalty: number
  presence_penalty: number
  max_retries: number
  timeout: number
  is_active: boolean
  is_default: boolean
  user_id: number
  created_at: string
  updated_at: string
}

// 查询参数接口
export interface AIModelQueryParams {
  page?: number
  pageSize?: number
  per_page?: number
  search?: string
  is_active?: boolean
}

// 创建AI模型参数接口
export interface CreateAIModelParams {
  name: string
  model_key: string
  description?: string
  api_key_env: string
  base_url: string
  model: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  max_retries?: number
  timeout?: number
  is_active?: boolean
  is_default?: boolean
}

/**
 * AI模型配置API服务
 */
class AIModelApiService extends BaseApiService {
  constructor() {
    super('/ai-config')
  }

  /**
   * 获取AI模型配置列表
   * @param params 查询参数
   */
  async getAIModels(params?: AIModelQueryParams): Promise<StandardResponse<{
    models: AIModelConfig[]
    pagination: {
      page: number
      per_page: number
      total: number
    }
  }>> {
    return apiAdapter.get(`${this.baseUrl}/models`, { params })
  }

  /**
   * 获取单个AI模型配置
   * @param id 模型ID
   */
  async getAIModel(id: string): Promise<StandardResponse<AIModelConfig>> {
    return apiAdapter.get(`${this.baseUrl}/models/${id}`)
  }

  /**
   * 创建AI模型配置
   * @param params 创建参数
   */
  async createAIModel(params: CreateAIModelParams): Promise<StandardResponse<AIModelConfig>> {
    return apiAdapter.post(`${this.baseUrl}/models`, params)
  }

  /**
   * 更新AI模型配置
   * @param id 模型ID
   * @param params 更新参数
   */
  async updateAIModel(id: string, params: Partial<CreateAIModelParams>): Promise<StandardResponse<AIModelConfig>> {
    return apiAdapter.put(`${this.baseUrl}/models/${id}`, params)
  }

  /**
   * 删除AI模型配置
   * @param id 模型ID
   */
  async deleteAIModel(id: string): Promise<StandardResponse<void>> {
    return apiAdapter.delete(`${this.baseUrl}/models/${id}`)
  }

  /**
   * 获取活跃的AI模型列表（用于下拉选择）
   */
  async getActiveAIModels(): Promise<StandardResponse<{
    models: AIModelConfig[]
  }>> {
    return this.getAIModels({ is_active: true, pageSize: 100 })
  }
}

// 创建并导出API服务实例
const aiModelApi = new AIModelApiService()

export default aiModelApi