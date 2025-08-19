<template>
  <div class="ai-model-edit">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" style="margin-right: 16px">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h1>编辑AI模型</h1>
          <p>修改AI模型的配置信息</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="aiStore.loading && !formData.name" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 编辑表单 -->
    <el-card v-else-if="formData.name" class="form-card">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        size="default"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          
          <el-form-item label="模型名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入模型名称，如：GPT-4"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="模型标识" prop="model">
            <el-input
              v-model="formData.model"
              placeholder="请输入模型标识，如：gpt-4"
              maxlength="100"
            />
          </el-form-item>
          
          <el-form-item label="API地址" prop="base_url">
            <el-input
              v-model="formData.base_url"
              placeholder="请输入API基础地址，如：https://api.openai.com/v1"
              maxlength="500"
            />
          </el-form-item>
          
          <el-form-item label="API密钥环境变量" prop="api_key_env">
            <el-input
              v-model="formData.api_key_env"
              placeholder="请输入环境变量名，如：OPENAI_API_KEY"
              maxlength="100"
            />
            <div class="form-tip">
              系统将从环境变量中读取API密钥
            </div>
          </el-form-item>
          
          <el-form-item label="超时设置" prop="timeout">
            <el-input-number
              v-model="formData.timeout"
              :min="1"
              :max="300"
              :step="1"
              controls-position="right"
            />
            <span style="margin-left: 8px; color: #909399;">秒</span>
          </el-form-item>
          
          <el-form-item label="设置">
            <el-checkbox v-model="formData.is_active">启用模型</el-checkbox>
            <el-checkbox v-model="formData.is_default" style="margin-left: 16px;">设为默认模型</el-checkbox>
          </el-form-item>
        </div>

        <!-- 生成配置 -->
        <div class="form-section">
          <h3>生成配置</h3>
          
          <el-form-item label="最大令牌数" prop="generation_config.max_tokens">
            <el-input-number
              v-model="formData.generation_config!.max_tokens"
              :min="1"
              :max="8000"
              :step="100"
              controls-position="right"
            />
            <div class="form-tip">
              控制生成内容的最大长度
            </div>
          </el-form-item>
          
          <el-form-item label="温度" prop="generation_config.temperature">
            <el-input-number
              v-model="formData.generation_config!.temperature"
              :min="0"
              :max="2"
              :step="0.1"
              :precision="1"
              controls-position="right"
            />
            <div class="form-tip">
              控制生成内容的随机性，0-2之间，值越高越随机
            </div>
          </el-form-item>
          
          <el-form-item label="Top P" prop="generation_config.top_p">
            <el-input-number
              v-model="formData.generation_config!.top_p"
              :min="0"
              :max="1"
              :step="0.1"
              :precision="1"
              controls-position="right"
            />
            <div class="form-tip">
              核采样参数，0-1之间
            </div>
          </el-form-item>
          
          <el-form-item label="频率惩罚" prop="generation_config.frequency_penalty">
            <el-input-number
              v-model="formData.generation_config!.frequency_penalty"
              :min="-2"
              :max="2"
              :step="0.1"
              :precision="1"
              controls-position="right"
            />
            <div class="form-tip">
              减少重复内容，-2到2之间
            </div>
          </el-form-item>
          
          <el-form-item label="存在惩罚" prop="generation_config.presence_penalty">
            <el-input-number
              v-model="formData.generation_config!.presence_penalty"
              :min="-2"
              :max="2"
              :step="0.1"
              :precision="1"
              controls-position="right"
            />
            <div class="form-tip">
              鼓励谈论新话题，-2到2之间
            </div>
          </el-form-item>
          
          <el-form-item label="停止序列">
            <div class="stop-sequences">
              <el-tag
                v-for="(seq, index) in formData.generation_config!.stop_sequences"
                :key="index"
                closable
                @close="removeStopSequence(index)"
                style="margin-right: 8px; margin-bottom: 8px;"
              >
                {{ seq }}
              </el-tag>
              <el-input
                v-if="showStopInput"
                ref="stopInputRef"
                v-model="newStopSequence"
                size="small"
                style="width: 120px; margin-right: 8px;"
                @keyup.enter="addStopSequence"
                @blur="addStopSequence"
              />
              <el-button v-else size="small" @click="showStopSequenceInput">
                + 添加停止序列
              </el-button>
            </div>
            <div class="form-tip">
              遇到这些序列时停止生成
            </div>
          </el-form-item>
        </div>

        <!-- 系统提示词 -->
        <div class="form-section">
          <h3>系统提示词</h3>
          
          <el-form-item label="提示词" prop="system_prompt">
            <el-input
              v-model="formData.system_prompt"
              type="textarea"
              :rows="6"
              placeholder="请输入系统提示词，用于指导AI的行为和风格"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button @click="handleBack">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="aiStore.loading">
            保存修改
          </el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 未找到模型 -->
    <el-empty v-else description="未找到该模型" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useAIStore, type UpdateAIModelParams } from '@/stores/ai'

const route = useRoute()
const router = useRouter()
const aiStore = useAIStore()

const formRef = ref<FormInstance>()
const stopInputRef = ref()

const modelId = computed(() => route.params.id as string)

// 表单数据
const formData = reactive<UpdateAIModelParams>({
  name: '',
  model: '',
  base_url: '',
  api_key_env: '',
  timeout: 30,
  is_active: true,
  is_default: false,
  generation_config: {
    max_tokens: 2000,
    temperature: 0.7,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    stop_sequences: []
  },
  system_prompt: ''
})

// 停止序列相关
const showStopInput = ref(false)
const newStopSequence = ref('')

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入模型标识', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: '请输入API地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  api_key_env: [
    { required: true, message: '请输入API密钥环境变量', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请设置超时时间', trigger: 'blur' },
    { type: 'number', min: 1, max: 300, message: '超时时间应在 1-300 秒之间', trigger: 'blur' }
  ]
}

// 加载模型数据
const loadModelData = async () => {
  try {
    // 如果store中没有数据，先加载
    if (aiStore.aiModels.length === 0) {
      await aiStore.fetchAIModels()
    }
    
    // 查找当前模型
    const model = aiStore.aiModels.find(m => m.id?.toString() === modelId.value)
    if (!model) {
      ElMessage.error('未找到指定的模型')
      router.push('/ai')
      return
    }
    
    // 填充表单数据
    Object.assign(formData, {
      name: model.name,
      model: model.model,
      base_url: model.base_url,
      api_key_env: model.api_key_env,
      timeout: model.timeout,
      is_active: model.is_active,
      is_default: model.is_default,
      generation_config: {
        max_tokens: model.generation_config?.max_tokens || 2000,
        temperature: model.generation_config?.temperature || 0.7,
        top_p: model.generation_config?.top_p || 1.0,
        frequency_penalty: model.generation_config?.frequency_penalty || 0.0,
        presence_penalty: model.generation_config?.presence_penalty || 0.0,
        stop_sequences: model.generation_config?.stop_sequences || []
      },
      system_prompt: model.system_prompt || ''
    })
  } catch (error) {
    ElMessage.error('加载模型数据失败')
    console.error('加载模型数据失败:', error)
  }
}

// 返回列表
const handleBack = () => {
  router.push('/ai')
}

// 显示停止序列输入框
const showStopSequenceInput = () => {
  showStopInput.value = true
  nextTick(() => {
    stopInputRef.value?.focus()
  })
}

// 添加停止序列
const addStopSequence = () => {
  if (newStopSequence.value.trim()) {
    formData.generation_config!.stop_sequences!.push(newStopSequence.value.trim())
    newStopSequence.value = ''
  }
  showStopInput.value = false
}

// 移除停止序列
const removeStopSequence = (index: number) => {
  formData.generation_config!.stop_sequences!.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    const id = parseInt(modelId.value)
    await aiStore.updateAIModel(id, formData)
    ElMessage.success('保存成功')
    router.push('/ai')
  } catch (error) {
    ElMessage.error('保存失败')
    console.error('更新AI模型失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadModelData()
})
</script>

<style scoped>
.ai-model-edit {
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

.header-left {
  display: flex;
  align-items: center;
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

.loading-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.form-tip {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.stop-sequences {
  min-height: 32px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.form-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
  text-align: right;
}

.form-actions .el-button {
  margin-left: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number) {
  width: 200px;
}
</style>