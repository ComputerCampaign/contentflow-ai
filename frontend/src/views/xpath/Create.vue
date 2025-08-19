<template>
  <div class="xpath-create">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
            <h2>创建XPath配置</h2>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="create-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          <el-form-item label="配置名称" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入配置名称"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入配置描述"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </div>

        <!-- XPath配置 -->
        <div class="form-section">
          <h3>XPath配置</h3>
          <el-form-item label="XPath表达式" prop="xpath">
            <el-input
              v-model="form.xpath"
              type="textarea"
              :rows="4"
              placeholder="请输入XPath表达式，例如：//div[@class='content']//text()"
            />
          </el-form-item>
          
          <el-form-item label="提取类型" prop="extractType">
            <el-select v-model="form.extractType" placeholder="请选择提取类型">
              <el-option label="文本" value="text" />
              <el-option label="HTML" value="html" />
              <el-option label="属性" value="attr" />
              <el-option label="链接" value="href" />
            </el-select>
          </el-form-item>
          
          <el-form-item 
            v-if="form.extractType === 'attr'" 
            label="属性名称" 
            prop="attrName"
          >
            <el-input
              v-model="form.attrName"
              placeholder="请输入属性名称，例如：href, src, title"
            />
          </el-form-item>
        </div>

        <!-- 处理规则 -->
        <div class="form-section">
          <h3>处理规则</h3>
          <el-form-item label="数据处理">
            <el-checkbox-group v-model="form.processing">
              <el-checkbox label="trim">去除首尾空格</el-checkbox>
              <el-checkbox label="lowercase">转换为小写</el-checkbox>
              <el-checkbox label="uppercase">转换为大写</el-checkbox>
              <el-checkbox label="removeHtml">移除HTML标签</el-checkbox>
              <el-checkbox label="removeNewlines">移除换行符</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </div>

        <!-- 状态设置 -->
        <div class="form-section">
          <h3>状态设置</h3>
          <el-form-item label="状态">
            <el-switch
              v-model="form.status"
              active-text="启用"
              inactive-text="禁用"
              active-value="active"
              inactive-value="inactive"
            />
          </el-form-item>
        </div>

        <!-- 测试区域 -->
        <div class="form-section">
          <h3>测试配置</h3>
          <el-form-item label="测试URL">
            <div class="test-input-group">
              <el-input
                v-model="testForm.url"
                placeholder="请输入要测试的URL"
                class="test-url-input"
              />
              <el-button 
                type="primary" 
                @click="runTest" 
                :loading="testLoading"
                :disabled="!form.xpath || !testForm.url"
              >
                测试
              </el-button>
            </div>
          </el-form-item>
          
          <div v-if="testResult" class="test-result">
            <h4>测试结果：</h4>
            <el-input
              v-model="testResult"
              type="textarea"
              :rows="4"
              readonly
            />
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            创建配置
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useXPathStore } from '@/stores/xpath'
import type { XPathConfig } from '@/stores/xpath'

const router = useRouter()
const xpathStore = useXPathStore()

const formRef = ref<FormInstance>()
const submitLoading = ref(false)
const testLoading = ref(false)
const testResult = ref('')

// 表单数据
const form = reactive<Partial<XPathConfig>>({
  name: '',
  description: '',
  xpath: '',
  extractType: 'text',
  attrName: '',
  processing: [],
  status: 'active'
})

// 测试表单
const testForm = reactive({
  url: ''
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '配置名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  xpath: [
    { required: true, message: '请输入XPath表达式', trigger: 'blur' }
  ],
  extractType: [
    { required: true, message: '请选择提取类型', trigger: 'change' }
  ],
  attrName: [
    {
      validator: (rule, value, callback) => {
        if (form.extractType === 'attr' && !value) {
          callback(new Error('选择属性提取时必须输入属性名称'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 返回
const goBack = () => {
  router.push('/xpath')
}

// 运行测试
const runTest = async () => {
  if (!form.xpath || !testForm.url) {
    ElMessage.warning('请输入XPath表达式和测试URL')
    return
  }
  
  try {
    testLoading.value = true
    const result = await xpathStore.testXPath({
      url: testForm.url,
      xpath: form.xpath,
      extractType: form.extractType,
      attrName: form.attrName,
      processing: form.processing
    })
    
    if (result.success) {
      testResult.value = result.data || '无匹配结果'
      ElMessage.success('测试完成')
    } else {
      testResult.value = `测试失败: ${result.error}`
      ElMessage.error('测试失败')
    }
  } catch (error) {
    console.error('Test error:', error)
    testResult.value = '测试过程中发生错误'
    ElMessage.error('测试失败')
  } finally {
    testLoading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    submitLoading.value = true
    
    const configData = {
      ...form,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      usageCount: 0
    } as XPathConfig
    
    const success = await xpathStore.createXPathConfig(configData)
    
    if (success) {
      ElMessage.success('创建成功')
      goBack()
    }
  } catch (error) {
    console.error('Submit error:', error)
    ElMessage.error('创建失败')
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.xpath-create {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.create-form {
  padding: 20px 0;
  max-width: 800px;
}

.form-section {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid #f0f0f0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: #606266;
  font-size: 16px;
  font-weight: 600;
}

.test-input-group {
  display: flex;
  gap: 10px;
}

.test-url-input {
  flex: 1;
}

.test-result {
  margin-top: 20px;
}

.test-result h4 {
  margin: 0 0 10px 0;
  color: #606266;
}

.form-actions {
  margin-top: 40px;
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.form-actions .el-button {
  margin: 0 10px;
  min-width: 100px;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

:deep(.el-checkbox) {
  margin-right: 0;
}
</style>