<template>
  <div class="xpath-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>XPath配置</h1>
        <p>配置和管理XPath提取规则</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <i class="fas fa-plus"></i>
          新建规则
        </el-button>
      </div>
    </div>

    <!-- 配置列表 -->
    <div v-loading="loading" class="config-grid">
      <div
        v-for="config in xpathRules"
        :key="config.id"
        class="config-card"
      >
        <div class="config-header">
          <h3>{{ config.name }}</h3>
          <el-tag :type="config.status === 'active' ? 'success' : 'info'">
            {{ config.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </div>
        <p class="config-description">{{ config.description }}</p>
        <div class="config-details">
          <div class="detail-item">
            <span class="label">规则ID:</span>
            <span class="value">{{ config.rule_id }}</span>
          </div>
          <div class="detail-item">
            <span class="label">规则类型:</span>
            <span class="value">{{ config.rule_type }}</span>
          </div>
          <div class="detail-item">
            <span class="label">字段名称:</span>
            <span class="value">{{ config.field_name }}</span>
          </div>
          <div class="detail-item">
            <span class="label">域名匹配:</span>
            <span class="value">{{ config.domain_patterns?.join(', ') || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">使用次数:</span>
            <span class="value">{{ config.usage_count || 0 }}</span>
          </div>
          <div class="detail-item">
            <span class="label">成功率:</span>
            <span class="value">{{ getSuccessRate(config) }}%</span>
          </div>
        </div>
        <div class="config-actions">
          <el-button size="small" @click="editConfig(config)">
            <i class="fas fa-edit"></i>
            编辑
          </el-button>
          <el-button size="small" @click="testConfig(config)">
            <i class="fas fa-play"></i>
            测试
          </el-button>
          <el-button size="small" type="danger" @click="deleteConfig(config)">
            <i class="fas fa-trash"></i>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 创建配置对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建XPath规则"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        label-width="120px"
        :rules="formRules"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-form-item label="规则ID" prop="rule_id">
          <el-input v-model="createForm.rule_id" placeholder="请输入规则ID，如：reddit_comments" />
        </el-form-item>
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入规则描述"
          />
        </el-form-item>
        
        <!-- 域名配置 -->
        <el-divider content-position="left">域名配置</el-divider>
        <el-form-item label="域名匹配" prop="domain_patterns">
          <el-select
            v-model="createForm.domain_patterns"
            multiple
            filterable
            allow-create
            placeholder="请输入域名，如：reddit.com"
            style="width: 100%"
          >
          </el-select>
        </el-form-item>
        
        <!-- XPath配置 -->
        <el-divider content-position="left">XPath配置</el-divider>
        <el-form-item label="XPath表达式" prop="xpath">
          <el-input
            v-model="createForm.xpath"
            type="textarea"
            :rows="3"
            placeholder="请输入XPath表达式，如：//div[@class='content']//p/text()"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则类型" prop="rule_type">
              <el-select v-model="createForm.rule_type" style="width: 100%">
                <el-option label="文本" value="text"></el-option>
                <el-option label="图片" value="image"></el-option>
                <el-option label="链接" value="link"></el-option>
                <el-option label="属性" value="attribute"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="字段名称" prop="field_name">
              <el-input v-model="createForm.field_name" placeholder="请输入字段名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 扩展XPath配置 -->
        <el-divider content-position="left">扩展XPath配置</el-divider>
        <el-form-item label="启用扩展配置">
          <el-switch v-model="enableCommentXpath" />
        </el-form-item>
        <div v-if="enableCommentXpath">
          <el-form-item label="文本XPath">
            <el-input v-model="createForm.comment_xpath_text" placeholder="提取文本内容的XPath" />
          </el-form-item>
          <el-form-item label="作者XPath">
            <el-input v-model="createForm.comment_xpath_author" placeholder="提取作者的XPath" />
          </el-form-item>
          <el-form-item label="评分XPath">
            <el-input v-model="createForm.comment_xpath_score" placeholder="提取评分的XPath" />
          </el-form-item>
          <el-form-item label="时间戳XPath">
            <el-input v-model="createForm.comment_xpath_timestamp" placeholder="提取时间戳的XPath" />
          </el-form-item>
          <el-form-item label="ID XPath">
            <el-input v-model="createForm.comment_xpath_comment_id" placeholder="提取ID的XPath" />
          </el-form-item>
          <el-form-item label="深度XPath">
            <el-input v-model="createForm.comment_xpath_depth" placeholder="提取深度的XPath" />
          </el-form-item>
          <el-form-item label="链接XPath">
            <el-input v-model="createForm.comment_xpath_permalink" placeholder="提取链接的XPath" />
          </el-form-item>
        </div>
        
        <!-- 状态配置 -->
        <el-divider content-position="left">状态配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="createForm.status" style="width: 100%">
                <el-option label="启用" value="active"></el-option>
                <el-option label="禁用" value="inactive"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公开规则">
              <el-switch v-model="createForm.is_public" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createConfig" :loading="creating">
            创建规则
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑配置对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑XPath规则"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="120px"
        :rules="formRules"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-form-item label="规则ID" prop="rule_id">
          <el-input v-model="editForm.rule_id" placeholder="请输入规则ID" />
        </el-form-item>
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入规则描述"
          />
        </el-form-item>
        
        <!-- 域名配置 -->
        <el-divider content-position="left">域名配置</el-divider>
        <el-form-item label="域名匹配" prop="domain_patterns">
          <el-select
            v-model="editForm.domain_patterns"
            multiple
            filterable
            allow-create
            placeholder="请输入域名"
            style="width: 100%"
          >
          </el-select>
        </el-form-item>
        
        <!-- XPath配置 -->
        <el-divider content-position="left">XPath配置</el-divider>
        <el-form-item label="XPath表达式" prop="xpath">
          <el-input
            v-model="editForm.xpath"
            type="textarea"
            :rows="3"
            placeholder="请输入XPath表达式"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则类型" prop="rule_type">
              <el-select v-model="editForm.rule_type" style="width: 100%">
                <el-option label="文本" value="text"></el-option>
                <el-option label="图片" value="image"></el-option>
                <el-option label="链接" value="link"></el-option>
                <el-option label="属性" value="attribute"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="字段名称" prop="field_name">
              <el-input v-model="editForm.field_name" placeholder="请输入字段名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 扩展XPath配置 -->
        <el-divider content-position="left">扩展XPath配置</el-divider>
        <el-form-item label="启用扩展配置">
          <el-switch v-model="editEnableCommentXpath" />
        </el-form-item>
        <div v-if="editEnableCommentXpath">
          <el-form-item label="文本XPath">
            <el-input v-model="editForm.comment_xpath_text" placeholder="提取文本内容的XPath" />
          </el-form-item>
          <el-form-item label="作者XPath">
            <el-input v-model="editForm.comment_xpath_author" placeholder="提取作者的XPath" />
          </el-form-item>
          <el-form-item label="评分XPath">
            <el-input v-model="editForm.comment_xpath_score" placeholder="提取评分的XPath" />
          </el-form-item>
          <el-form-item label="时间戳XPath">
            <el-input v-model="editForm.comment_xpath_timestamp" placeholder="提取时间戳的XPath" />
          </el-form-item>
          <el-form-item label="ID XPath">
            <el-input v-model="editForm.comment_xpath_comment_id" placeholder="提取ID的XPath" />
          </el-form-item>
          <el-form-item label="深度XPath">
            <el-input v-model="editForm.comment_xpath_depth" placeholder="提取深度的XPath" />
          </el-form-item>
          <el-form-item label="链接XPath">
            <el-input v-model="editForm.comment_xpath_permalink" placeholder="提取链接的XPath" />
          </el-form-item>
        </div>
        
        <!-- 状态配置 -->
        <el-divider content-position="left">状态配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="editForm.status" style="width: 100%">
                <el-option label="启用" value="active"></el-option>
                <el-option label="禁用" value="inactive"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公开规则">
              <el-switch v-model="editForm.is_public" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="updateConfig" :loading="updating">
            更新规则
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { xpathAPI as xpathApi } from '@/api/xpath'
import dayjs from 'dayjs'

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const createFormRef = ref(null)
const editFormRef = ref(null)
const loading = ref(false)
const creating = ref(false)
const updating = ref(false)
const enableCommentXpath = ref(false)
const editEnableCommentXpath = ref(false)

const createForm = ref({
  rule_id: '',
  name: '',
  description: '',
  domain_patterns: [],
  xpath: '',
  rule_type: 'text',
  field_name: '',
  comment_xpath_text: '',
  comment_xpath_author: '',
  comment_xpath_score: '',
  comment_xpath_timestamp: '',
  comment_xpath_comment_id: '',
  comment_xpath_depth: '',
  comment_xpath_permalink: '',
  status: 'active',
  is_public: false
})

const editForm = ref({})
const xpathRules = ref([])

// 表单验证规则
const formRules = {
  rule_id: [
    { required: true, message: '请输入规则ID', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  domain_patterns: [
    { required: true, message: '请输入至少一个域名', trigger: 'change' }
  ],
  xpath: [
    { required: true, message: '请输入XPath表达式', trigger: 'blur' }
  ],
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  field_name: [
    { required: true, message: '请输入字段名称', trigger: 'blur' }
  ]
}

// 获取配置列表
const fetchConfigs = async () => {
  try {
    loading.value = true
    const response = await xpathApi.getRules()
    xpathRules.value = response.data.rules || []
  } catch (error) {
    console.error('获取XPath配置列表失败:', error)
    ElMessage.error('获取XPath配置列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 计算成功率
const getSuccessRate = (config) => {
  if (!config.usage_count || config.usage_count === 0) return 0
  return Math.round((config.success_count || 0) / config.usage_count * 100)
}

// 编辑配置
const editConfig = (config) => {
  editForm.value = { ...config }
  
  // 处理comment_xpath对象到扁平化字段的映射
  if (config.comment_xpath && typeof config.comment_xpath === 'object') {
    editForm.value.comment_xpath_text = config.comment_xpath.text || ''
    editForm.value.comment_xpath_author = config.comment_xpath.author || ''
    editForm.value.comment_xpath_score = config.comment_xpath.score || ''
    editForm.value.comment_xpath_timestamp = config.comment_xpath.timestamp || ''
    editForm.value.comment_xpath_comment_id = config.comment_xpath.comment_id || ''
    editForm.value.comment_xpath_depth = config.comment_xpath.depth || ''
    editForm.value.comment_xpath_permalink = config.comment_xpath.permalink || ''
    editEnableCommentXpath.value = true
  } else {
    // 检查是否有扁平化的comment_xpath字段
    editEnableCommentXpath.value = !!(config.comment_xpath_text || config.comment_xpath_author)
  }
  
  showEditDialog.value = true
}

// 测试配置
const testConfig = async (config) => {
  try {
    ElMessage.info('正在测试XPath规则...')
    await xpathApi.testRule({ rule_id: config.rule_id, url: 'https://example.com' })
    ElMessage.success(`XPath规则 "${config.name}" 测试成功`)
  } catch (error) {
    console.error('XPath规则测试失败:', error)
    ElMessage.error('XPath规则测试失败: ' + (error.message || '未知错误'))
  }
}

// 删除配置
const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除XPath规则 "${config.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await xpathApi.deleteRule(config.rule_id)
    const index = xpathRules.value.findIndex(c => c.rule_id === config.rule_id)
    if (index > -1) {
      xpathRules.value.splice(index, 1)
    }
    ElMessage.success('XPath规则删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除XPath规则失败:', error)
      ElMessage.error('删除XPath规则失败: ' + (error.message || '未知错误'))
    }
  }
}

// 创建配置
const createConfig = async () => {
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    const configData = {
      rule_id: createForm.value.rule_id,
      name: createForm.value.name,
      description: createForm.value.description,
      domain_patterns: createForm.value.domain_patterns,
      xpath: createForm.value.xpath,
      rule_type: createForm.value.rule_type,
      field_name: createForm.value.field_name,
      status: createForm.value.status,
      is_public: createForm.value.is_public
    }
    
    // 如果启用了扩展XPath配置
    if (enableCommentXpath.value) {
      configData.comment_xpath = {
        text: createForm.value.comment_xpath_text,
        author: createForm.value.comment_xpath_author,
        score: createForm.value.comment_xpath_score,
        timestamp: createForm.value.comment_xpath_timestamp,
        comment_id: createForm.value.comment_xpath_comment_id,
        depth: createForm.value.comment_xpath_depth,
        permalink: createForm.value.comment_xpath_permalink
      }
    }
    
    const response = await xpathApi.createRule(configData)
    xpathRules.value.push(response.data)
    ElMessage.success('XPath规则创建成功')
    showCreateDialog.value = false
    resetCreateForm()
  } catch (error) {
    if (error !== false) {
      console.error('创建XPath规则失败:', error)
      ElMessage.error('创建XPath规则失败: ' + (error.message || '未知错误'))
    }
  } finally {
    creating.value = false
  }
}

// 更新配置
const updateConfig = async () => {
  try {
    await editFormRef.value.validate()
    updating.value = true
    
    const configData = { ...editForm.value }
    
    // 如果启用了扩展XPath配置
    if (editEnableCommentXpath.value) {
      configData.comment_xpath = {
        text: editForm.value.comment_xpath_text,
        author: editForm.value.comment_xpath_author,
        score: editForm.value.comment_xpath_score,
        timestamp: editForm.value.comment_xpath_timestamp,
        comment_id: editForm.value.comment_xpath_comment_id,
        depth: editForm.value.comment_xpath_depth,
        permalink: editForm.value.comment_xpath_permalink
      }
    }
    
    const response = await xpathApi.updateRule(editForm.value.rule_id, configData)
    const index = xpathRules.value.findIndex(c => c.rule_id === editForm.value.rule_id)
    if (index > -1) {
      xpathRules.value[index] = response.data
    }
    ElMessage.success('XPath规则更新成功')
    showEditDialog.value = false
  } catch (error) {
    if (error !== false) {
      console.error('更新XPath规则失败:', error)
      ElMessage.error('更新XPath规则失败: ' + (error.message || '未知错误'))
    }
  } finally {
    updating.value = false
  }
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    rule_id: '',
    name: '',
    description: '',
    domain_patterns: [],
    xpath: '',
    rule_type: 'text',
    field_name: '',
    comment_xpath_text: '',
    comment_xpath_author: '',
    comment_xpath_score: '',
    comment_xpath_timestamp: '',
    comment_xpath_comment_id: '',
    comment_xpath_depth: '',
    comment_xpath_permalink: '',
    status: 'active',
    is_public: false
  }
  enableCommentXpath.value = false
}

// 组件挂载时获取数据
onMounted(() => {
  fetchConfigs()
})
</script>

<style lang="scss" scoped>
.xpath-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
    }
  }
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.config-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
  }
  
  .config-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
  
  .config-description {
    color: var(--text-regular);
    font-size: 14px;
    margin-bottom: 16px;
  }
  
  .config-details {
    margin-bottom: 16px;
    
    .detail-item {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      font-size: 13px;
      
      .label {
        width: 80px;
        color: var(--text-secondary);
      }
      
      .value {
        color: var(--text-primary);
        flex: 1;
        word-break: break-all;
      }
    }
  }
  
  .config-actions {
    display: flex;
    gap: 8px;
  }
}
</style>