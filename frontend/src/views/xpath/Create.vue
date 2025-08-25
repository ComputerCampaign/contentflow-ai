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
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="规则ID" prop="rule_id">
                <el-input
                  v-model="form.rule_id"
                  placeholder="请输入规则ID，如：reddit_comments"
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="配置名称" prop="name">
                <el-input
                  v-model="form.name"
                  placeholder="请输入配置名称"
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="字段名称" prop="field_name">
                <el-input
                  v-model="form.field_name"
                  placeholder="请输入字段名称，用于标识提取的数据字段"
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="规则类型" prop="rule_type">
                <el-select v-model="form.rule_type" placeholder="请选择规则类型" style="width: 100%">
                  <el-option label="文本" value="text" />
                  <el-option label="图片" value="image" />
                  <el-option label="属性" value="attr" />
                  <el-option label="链接" value="href" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
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
          
          <el-form-item label="域名模式" prop="domain_patterns">
            <el-input
              v-model="domainPatternsText"
              type="textarea"
              :rows="2"
              placeholder="请输入域名模式，每行一个，如：\nreddit.com\nwww.reddit.com"
              @blur="updateDomainPatterns"
            />
            <div class="form-tip">支持多个域名模式，每行输入一个域名</div>
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
        </div>
        
        <!-- 扩展XPath配置 -->
        <div class="form-section">
          <h3>扩展XPath配置</h3>
          <el-form-item label="启用扩展配置">
            <el-switch v-model="enableCommentXpath" />
            <div class="form-tip">启用后可配置更详细的XPath提取规则，适用于复杂的数据结构</div>
          </el-form-item>
          
          <div v-if="enableCommentXpath" class="comment-xpath-config">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="文本XPath">
                  <el-input
                    v-model="commentXpathFields.text"
                    placeholder="提取文本内容的XPath"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="作者XPath">
                  <el-input
                    v-model="commentXpathFields.author"
                    placeholder="提取作者的XPath"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="评分XPath">
                  <el-input
                    v-model="commentXpathFields.score"
                    placeholder="提取评分的XPath"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="时间戳XPath">
                  <el-input
                    v-model="commentXpathFields.timestamp"
                    placeholder="提取时间戳的XPath"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="评论ID XPath">
                  <el-input
                    v-model="commentXpathFields.comment_id"
                    placeholder="提取评论ID的XPath"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="深度XPath">
                  <el-input
                    v-model="commentXpathFields.depth"
                    placeholder="提取深度的XPath"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="链接XPath">
              <el-input
                v-model="commentXpathFields.permalink"
                placeholder="提取链接的XPath"
              />
            </el-form-item>
          </div>
        </div>

        <!-- 规则设置 -->
        <div class="form-section">
          <h3>规则设置</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="状态">
                <el-switch
                  v-model="form.enabled"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公开规则">
                <el-switch
                  v-model="form.is_public"
                  active-text="公开"
                  inactive-text="私有"
                />
                <div class="form-tip">公开规则可被其他用户使用</div>
              </el-form-item>
            </el-col>
          </el-row>
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
const enableCommentXpath = ref(false)
const domainPatternsText = ref('')

// 扩展 XPath 配置字段
const commentXpathFields = reactive({
  text: '',
  author: '',
  score: '',
  timestamp: '',
  comment_id: '',
  depth: '',
  permalink: ''
})

// 表单数据
const form = reactive<Partial<XPathConfig>>({
  rule_id: '',
  name: '',
  field_name: '',
  description: '',
  xpath: '',
  rule_type: 'text',
  domain_patterns: [],
  enabled: true,
  is_public: false
})

// 测试表单
const testForm = reactive({
  url: ''
})

// 域名模式处理
const updateDomainPatterns = () => {
  if (domainPatternsText.value.trim()) {
    form.domain_patterns = domainPatternsText.value
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
  } else {
    form.domain_patterns = []
  }
}

// 表单验证规则
const rules: FormRules = {
  rule_id: [
    { required: true, message: '请输入规则ID', trigger: 'blur' },
    { min: 2, max: 50, message: '规则ID长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '配置名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  field_name: [
    { required: true, message: '请输入字段名称', trigger: 'blur' },
    { min: 2, max: 50, message: '字段名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  xpath: [
    { required: true, message: '请输入XPath表达式', trigger: 'blur' }
  ],
  domain_patterns: [
    { required: true, message: '请输入域名模式', trigger: 'blur' }
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
      rule_type: form.rule_type || 'text'
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
    // 更新域名模式
    updateDomainPatterns()
    
    const valid = await formRef.value.validate()
    if (!valid) return
    
    submitLoading.value = true
    
    const configData = {
      ...form,
      status: form.enabled ? 'active' : 'inactive',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      usage_count: 0
    } as any
    
    // 如果启用了扩展XPath配置
    if (enableCommentXpath.value) {
      configData.comment_xpath = {
        text: commentXpathFields.text,
        author: commentXpathFields.author,
        score: commentXpathFields.score,
        timestamp: commentXpathFields.timestamp,
        comment_id: commentXpathFields.comment_id,
        depth: commentXpathFields.depth,
        permalink: commentXpathFields.permalink
      }
    }
    
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