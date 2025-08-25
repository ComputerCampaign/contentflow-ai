<template>
  <div class="prompt-edit">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>编辑提示词</h2>
          <div class="header-actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">
              保存
            </el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        class="prompt-form"
        v-loading="loading"
      >
        <!-- 基本信息 -->
        <el-card class="form-section">
          <template #header>
            <span class="section-title">基本信息</span>
          </template>
          
          <el-form-item label="提示词名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入提示词名称"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="提示词标识" prop="key">
            <el-input
              v-model="formData.key"
              placeholder="请输入提示词标识（英文字母、数字、下划线）"
              maxlength="50"
              show-word-limit
              :disabled="true"
            />
            <div class="form-help">
              <el-text type="info" size="small">
                提示词标识不可修改
              </el-text>
            </div>
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="3"
              placeholder="请输入提示词描述"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-card>

        <!-- 提示词配置 -->
        <el-card class="form-section">
          <template #header>
            <span class="section-title">提示词配置</span>
          </template>
          
          <el-form-item label="系统提示词" prop="system">
            <el-input
              v-model="formData.system"
              type="textarea"
              :rows="5"
              placeholder="请输入系统提示词，用于设定AI的角色和行为规范"
              maxlength="2000"
              show-word-limit
            />
            <div class="form-help">
              <el-text type="info" size="small">
                系统提示词用于定义AI的角色、行为规范和回答风格
              </el-text>
            </div>
          </el-form-item>
          
          <el-form-item label="用户模板" prop="user_template">
            <el-input
              v-model="formData.user_template"
              type="textarea"
              :rows="8"
              placeholder="请输入用户提示词模板，支持变量如 {title}, {description}, {images}, {comments}"
              maxlength="5000"
              show-word-limit
            />
            <div class="form-help">
              <el-text type="info" size="small">
                支持的变量：{title} - 标题，{description} - 描述，{images} - 图片信息，{comments} - 评论信息
              </el-text>
            </div>
          </el-form-item>
        </el-card>

        <!-- 设置 -->
        <el-card class="form-section">
          <template #header>
            <span class="section-title">设置</span>
          </template>
          
          <el-form-item label="状态">
            <el-switch
              v-model="formData.status"
              active-text="启用"
              inactive-text="禁用"
              active-value="active"
              inactive-value="inactive"
            />
          </el-form-item>
          
          <el-form-item label="设为默认">
            <el-switch
              v-model="formData.is_default"
              active-text="是"
              inactive-text="否"
            />
            <div class="form-help">
              <el-text type="info" size="small">
                设为默认后，新的内容生成将使用此提示词模板
              </el-text>
            </div>
          </el-form-item>
        </el-card>

        <!-- 测试配置 -->
        <el-card class="form-section">
          <template #header>
            <div class="section-header">
              <span class="section-title">测试配置</span>
              <el-button size="small" type="primary" @click="handleTest" :loading="testing">
                测试提示词
              </el-button>
            </div>
          </template>
          
          <el-form-item label="测试数据">
            <el-input
              v-model="testData"
              type="textarea"
              :rows="4"
              placeholder="请输入测试数据（JSON格式），例如：{&quot;title&quot;: &quot;测试标题&quot;, &quot;description&quot;: &quot;测试描述&quot;}"
            />
          </el-form-item>
          
          <el-form-item label="测试结果" v-if="testResult">
            <div class="test-result">
              <pre>{{ testResult }}</pre>
            </div>
          </el-form-item>
        </el-card>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useAIStore } from '@/stores/ai'

const router = useRouter()
const route = useRoute()
const aiStore = useAIStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const testData = ref('')
const testResult = ref('')
const originalKey = ref('')

const formData = reactive({
  name: '',
  key: '',
  description: '',
  system: '',
  user_template: '',
  status: 'active',
  is_default: false
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入提示词名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  key: [
    { required: true, message: '请输入提示词标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含英文字母、数字和下划线', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  system: [
    { required: true, message: '请输入系统提示词', trigger: 'blur' }
  ],
  user_template: [
    { required: true, message: '请输入用户模板', trigger: 'blur' }
  ]
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    const key = route.params.key as string
    if (!key) {
      ElMessage.error('参数错误')
      router.push('/ai')
      return
    }
    
    await aiStore.fetchPromptsConfig()
    
    const promptData = aiStore.promptsConfig.prompts[key]
    if (!promptData) {
      ElMessage.error('提示词不存在')
      router.push('/ai')
      return
    }
    
    originalKey.value = key
    Object.assign(formData, {
      name: key,
      key: key,
      description: '',
      system: promptData.system || '',
      user_template: promptData.user_template || '',
      status: 'active',
      is_default: aiStore.promptsConfig.default_prompt === key
    })
    
  } catch (error) {
    console.error('Load data error:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 保存
const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    saving.value = true
    
    // 更新配置
    aiStore.promptsConfig.prompts[originalKey.value] = {
      system: formData.system,
      user_template: formData.user_template
    }
    
    // 如果设为默认，更新默认设置
    if (formData.is_default) {
      aiStore.promptsConfig.default_prompt = originalKey.value
    } else if (aiStore.promptsConfig.default_prompt === originalKey.value) {
      // 如果取消默认设置
      aiStore.promptsConfig.default_prompt = ''
    }
    
    await aiStore.savePromptsConfig(aiStore.promptsConfig)
    
    ElMessage.success('保存成功')
    router.push('/ai')
    
  } catch (error) {
    console.error('Save error:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 取消
const handleCancel = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消编辑吗？未保存的数据将丢失。',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '继续编辑',
        type: 'warning'
      }
    )
    
    router.push('/ai')
  } catch (error) {
    // 用户取消
  }
}

// 测试提示词
const handleTest = async () => {
  if (!formData.system || !formData.user_template) {
    ElMessage.warning('请先填写系统提示词和用户模板')
    return
  }
  
  try {
    testing.value = true
    
    let testDataObj = {}
    if (testData.value) {
      try {
        testDataObj = JSON.parse(testData.value)
      } catch (e) {
        ElMessage.error('测试数据格式错误，请输入有效的JSON格式')
        return
      }
    }
    
    // 替换模板中的变量
    let processedTemplate = formData.user_template
    Object.entries(testDataObj).forEach(([key, value]) => {
      const regex = new RegExp(`\\{${key}\\}`, 'g')
      processedTemplate = processedTemplate.replace(regex, String(value))
    })
    
    testResult.value = `系统提示词：\n${formData.system}\n\n用户提示词：\n${processedTemplate}`
    
    ElMessage.success('测试完成')
    
  } catch (error) {
    console.error('Test error:', error)
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.prompt-edit {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.prompt-form {
  max-width: 800px;
}

.form-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: 600;
  color: #303133;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.form-help {
  margin-top: 5px;
}

.test-result {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.test-result pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #303133;
}
</style>