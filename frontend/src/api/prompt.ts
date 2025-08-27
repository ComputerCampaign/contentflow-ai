import { BaseApiService } from './base'
import apiAdapter, { type StandardResponse } from '@/utils/api-adapter'

// 提示词接口定义
export interface Prompt {
  id: string
  name: string
  description?: string
  content: string
  category?: string
  tags?: string[]
  isActive: boolean
  createdAt: string
  updatedAt: string
  createdBy?: string
}

// 提示词模板配置接口
export interface PromptTemplate {
  system: string
  user_template: string
}

// 提示词配置接口
export interface PromptConfig {
  default_prompt: string
  prompts: Record<string, PromptTemplate>
  _note?: string
}

// 创建提示词参数
export interface CreatePromptParams {
  name: string
  description?: string
  content: string
  category?: string
  tags?: string[]
  isActive?: boolean
}

// 更新提示词参数
export interface UpdatePromptParams {
  name?: string
  description?: string
  content?: string
  category?: string
  tags?: string[]
  isActive?: boolean
}

// 提示词查询参数
export interface PromptQueryParams {
  page?: number
  pageSize?: number
  keyword?: string
  category?: string
  isActive?: boolean
  tags?: string[]
}

/**
 * 提示词管理API服务
 */
export class PromptApiService extends BaseApiService {
  constructor() {
    super('/prompts')
  }

  /**
   * 获取提示词配置模板
   */
  async getPromptConfig(): Promise<StandardResponse<PromptConfig>> {
    return apiAdapter.get('/ai-config/prompts')
  }

  /**
   * 获取提示词模板选项（用于下拉选择）
   */
  async getPromptTemplateOptions(): Promise<StandardResponse<Array<{ key: string, label: string, template: PromptTemplate }>>> {
    const response = await this.getPromptConfig()
    if (response.success && response.data) {
      const options = Object.entries(response.data.prompts).map(([key, template]) => ({
        key,
        label: this.getPromptDisplayName(key),
        template
      }))
      return {
        success: true,
        data: options,
        message: '获取提示词模板选项成功'
      }
    }
    return response as any
  }

  /**
   * 获取提示词显示名称
   */
  private getPromptDisplayName(key: string): string {
    const nameMap: Record<string, string> = {
      'social_media_content': '自媒体内容生成',
      'article_generation': '文章生成',
      'summary_generation': '摘要生成',
      'title_generation': '标题生成'
    }
    return nameMap[key] || key
  }

  /**
   * 获取提示词列表
   * @param params 查询参数
   */
  async getPrompts(params?: PromptQueryParams): Promise<StandardResponse<{
    prompts: Prompt[]
    pagination: {
      page: number
      per_page: number
      total: number
    }
  }>> {
    const response = await this.getPagedList<Prompt>(params)
    if (response.success && response.data) {
      return {
        ...response,
        data: {
          prompts: response.data.tasks,
          pagination: response.data.pagination
        }
      }
    }
    return response as any
  }

  /**
   * 获取活跃的提示词列表（用于下拉选择）
   * @param category 可选的分类过滤
   */
  async getActivePrompts(category?: string): Promise<StandardResponse<{
    prompts: Prompt[]
  }>> {
    const params = new URLSearchParams()
    params.append('isActive', 'true')
    params.append('pageSize', '1000') // 获取所有活跃提示词
    if (category) {
      params.append('category', category)
    }
    
    return apiAdapter.get(`${this.baseUrl}?${params.toString()}`)
  }

  /**
   * 获取提示词详情
   * @param id 提示词ID
   */
  async getPrompt(id: string): Promise<StandardResponse<Prompt>> {
    return this.getById<Prompt>(id)
  }

  /**
   * 创建提示词
   * @param params 创建参数
   */
  async createPrompt(params: CreatePromptParams): Promise<StandardResponse<Prompt>> {
    return this.create<Prompt>(params)
  }

  /**
   * 更新提示词
   * @param id 提示词ID
   * @param params 更新参数
   */
  async updatePrompt(id: string, params: UpdatePromptParams): Promise<StandardResponse<Prompt>> {
    return this.update<Prompt>(id, params)
  }

  /**
   * 删除提示词
   * @param id 提示词ID
   */
  async deletePrompt(id: string): Promise<StandardResponse<void>> {
    return this.delete<void>(id)
  }

  /**
   * 批量删除提示词
   * @param ids 提示词ID数组
   */
  async batchDeletePrompts(ids: string[]): Promise<StandardResponse<void>> {
    return this.batchAction<void>('delete', ids)
  }

  /**
   * 复制提示词
   * @param id 提示词ID
   * @param params 复制时的修改参数
   */
  async duplicatePrompt(id: string, params?: Partial<CreatePromptParams>): Promise<StandardResponse<Prompt>> {
    return this.duplicate<Prompt>(id, params)
  }

  /**
   * 获取提示词分类列表
   */
  async getPromptCategories(): Promise<StandardResponse<string[]>> {
    return apiAdapter.get(`${this.baseUrl}/categories`)
  }

  /**
   * 获取提示词标签列表
   */
  async getPromptTags(): Promise<StandardResponse<string[]>> {
    return apiAdapter.get(`${this.baseUrl}/tags`)
  }

  /**
   * 搜索提示词
   * @param keyword 搜索关键词
   * @param params 其他查询参数
   */
  async searchPrompts(keyword: string, params?: Omit<PromptQueryParams, 'keyword'>): Promise<StandardResponse<{
    prompts: Prompt[]
    pagination: {
      page: number
      per_page: number
      total: number
    }
  }>> {
    const response = await this.getPagedList<Prompt>({ ...params, keyword })
    if (response.success && response.data) {
      return {
        ...response,
        data: {
          prompts: response.data.tasks,
          pagination: response.data.pagination
        }
      }
    }
    return response as any
  }
}

// 导出单例实例
export const promptApi = new PromptApiService()
export default promptApi