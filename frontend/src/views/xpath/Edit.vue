<template>
  <div class="xpath-edit">
    <el-card class="page-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>编辑XPath配置</h2>
          <div class="header-actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">
              保存修改
            </el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="edit-form"
      >
        <!-- 基本信息 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>基本信息</h3>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="配置名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入配置名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-radio-group v-model="form.status">
                  <el-radio label="active">启用</el-radio>
                  <el-radio label="inactive">禁用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="描述">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入配置描述"
            />
          </el-form-item>
        </el-card>

        <!-- XPath配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>XPath配置</h3>
          </template>
          
          <el-form-item label="XPath表达式" prop="xpath">
            <el-input
              v-model="form.xpath"
              type="textarea"
              :rows="4"
              placeholder="请输入XPath表达式，例如：//div[@class='content']//text()"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="提取类型" prop="extractType">
                <el-select v-model="form.extractType" placeholder="选择提取类型">
                  <el-option label="文本内容" value="text" />
                  <el-option label="HTML内容" value="html" />
                  <el-option label="属性值" value="attr" />
                  <el-option label="链接地址" value="href" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                v-if="form.extractType === 'attr'"
                label="属性名称"
                prop="attrName"
              >
                <el-input v-model="form.attrName" placeholder="请输入属性名称" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="数据处理">
            <el-checkbox-group v-model="form.processing">
              <el-checkbox label="trim">去除首尾空格</el-checkbox>
              <el-checkbox label="removeEmpty">移除空值</el-checkbox>
              <el-checkbox label="unique">去重</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-card>

        <!-- 测试配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <h3>测试配置</h3>
              <el-button type="primary" size="small" @click="handleTest" :loading="testing">
                测试XPath
              </el-button>
            </div>
          </template>
          
          <el-form-item label="测试URL">
            <el-input v-model="testUrl" placeholder="请输入要测试的URL" />
          </el-form-item>
          
          <div v-if="testResult" class="test-result">
            <h4>测试结果：</h4>
            <el-alert
              v-if="testResult.success"
              title="测试成功"
              type="success"
              :description="`提取到 ${testResult.count} 个结果`"
              show-icon
            />
            <el-alert
              v-else
              title="测试失败"
              type="error"
              :description="testResult.error"
              show-icon
            />
            
            <div v-if="testResult.data" class="result-data">
              <el-input
                v-model="testResult.data"
                type="textarea"
                :rows="6"
                readonly
                class="result-textarea"
              />
            </div>
          </div>
        </el-card>

        <!-- 使用统计 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <h3>使用统计</h3>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-label">创建时间</div>
                <div class="stat-value">{{ formatDate(form.createdAt) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-label">最后修改</div>
                <div class="stat-value">{{ formatDate(form.updatedAt) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-label">使用次数</div>
                <div class="stat-value">{{ form.usageCount || 0 }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { useXPathStore } from '@/stores/xpath'

const router = useRouter()
const route = useRoute()
const xpathStore = useXPathStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const testUrl = ref('')
const testResult = ref<any>(null)

const form = reactive({
  id: '',
  name: '',
  description: '',
  xpath: '',
  extractType: 'text',
  attrName: '',
  status: 'active',
  processing: ['trim'],
  createdAt: '',
  updatedAt: '',
  usageCount: 0
})

const rules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  xpath: [
    { required: true, message: '请输入XPath表达式', trigger: 'blur' }
  ],
  extractType: [
    { required: true, message: '请选择提取类型', trigger: 'change' }
  ],
  attrName: [
    { required: true, message: '请输入属性名称', trigger: 'blur' }
  ]
}

// 加载配置数据
const loadConfig = async () => {
  const id = route.params.id as string
  if (!id) {
    ElMessage.error('配置ID不存在')
    router.push('/xpath/list')
    return
  }
  
  try {
    loading.value = true
    const config = await xpathStore.getXPathConfig(id)
    if (config) {
      Object.assign(form, config)
    } else {
      ElMessage.error('配置不存在')
      router.push('/xpath/list')
    }
  } catch (error) {
    console.error('Load config error:', error)
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

// 测试XPath
const handleTest = async () => {
  if (!form.xpath) {
    ElMessage.warning('请先输入XPath表达式')
    return
  }
  
  if (!testUrl.value) {
    ElMessage.warning('请输入测试URL')
    return
  }
  
  try {
    testing.value = true
    testResult.value = null
    
    const testConfig = {
      url: testUrl.value,
      xpath: form.xpath,
      extractType: form.extractType as 'text' | 'html' | 'attr' | 'href',
      attrName: form.attrName,
      processing: form.processing
    }
    
    const result = await xpathStore.testXPath(testConfig)
    testResult.value = result
    
    if (result.success) {
      ElMessage.success('测试完成')
    } else {
      ElMessage.error('测试失败：' + result.error)
    }
  } catch (error) {
    console.error('Test error:', error)
    ElMessage.error('测试过程中发生错误')
  } finally {
    testing.value = false
  }
}

// 保存配置
const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    saving.value = true
    
    const success = await xpathStore.updateXPathConfig(form.id, {
      ...form,
      extractType: form.extractType as 'text' | 'html' | 'attr' | 'href',
      status: form.status as 'active' | 'inactive'
    })
    if (success) {
      ElMessage.success('保存成功')
      router.push('/xpath/list')
    }
  } catch (error) {
    console.error('Save error:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.xpath-edit {
  padding: 20px;
}

.page-card {
  max-width: 1000px;
  margin: 0 auto;
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

.edit-form {
  padding: 20px 0;
}

.form-section {
  margin-bottom: 20px;
}

.form-section :deep(.el-card__header) {
  padding: 15px 20px;
  background-color: #f8f9fa;
}

.form-section h3 {
  margin: 0;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-result {
  margin-top: 20px;
}

.test-result h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.result-data {
  margin-top: 15px;
}

.result-textarea {
  font-family: 'Courier New', monospace;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}
</style>