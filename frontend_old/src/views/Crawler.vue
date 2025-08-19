<template>
  <div class="crawler-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>爬虫配置</h1>
        <p>配置和管理爬虫规则</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openCreateDialog">
          <i class="fas fa-plus"></i>
          新建配置
        </el-button>
      </div>
    </div>

    <!-- 配置列表 -->
    <div v-loading="loading" class="config-grid">
      <div
        v-for="config in configs"
        :key="config.id"
        class="config-card"
      >
        <div class="config-header">
          <h3>{{ config.name }}</h3>
          <el-switch
            v-model="config.enabled"
            @change="toggleConfig(config)"
          />
        </div>
        <p class="config-description">{{ config.description }}</p>
        <div class="config-details">
          <div class="detail-item">
            <span class="label">超时时间:</span>
            <span class="value">{{ config.timeout }}秒</span>
          </div>
          <div class="detail-item">
            <span class="label">重试次数:</span>
            <span class="value">{{ config.retry }}次</span>
          </div>
          <div class="detail-item">
            <span class="label">最大工作线程:</span>
            <span class="value">{{ config.max_workers }}</span>
          </div>
          <div class="detail-item">
            <span class="label">使用Selenium:</span>
            <span class="value">{{ config.use_selenium ? '是' : '否' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">启用XPath:</span>
            <span class="value">{{ config.enable_xpath ? '是' : '否' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">最后更新:</span>
            <span class="value">{{ formatTime(config.updated_at) }}</span>
          </div>
        </div>
        <div class="config-actions">
          <el-button size="small" @click="editConfig(config)">
            <i class="fas fa-edit"></i>
            编辑
          </el-button>
          <el-button size="small" type="info" @click="generateCommand(config)">
            <i class="fas fa-terminal"></i>
            生成命令
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
      title="新建爬虫配置"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="120px"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-form-item label="配置名称" prop="name" required>
          <el-input 
            v-model="createForm.name" 
            placeholder="请输入配置名称"
            @blur="validateConfigName"
          />
        </el-form-item>
        <el-form-item label="配置描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入配置描述"
          />
        </el-form-item>
        
        <!-- 存储配置 -->
        <el-divider content-position="left">存储配置</el-divider>
        <el-form-item label="数据目录">
          <el-input v-model="createForm.data_dir" placeholder="crawler_data" />
        </el-form-item>
        
        <!-- 爬虫核心配置 -->
        <el-divider content-position="left">爬虫核心配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="超时时间(秒)">
              <el-input-number v-model="createForm.timeout" :min="1" :max="300" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="重试次数">
              <el-input-number v-model="createForm.retry" :min="0" :max="10" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="使用Selenium">
              <el-switch v-model="createForm.use_selenium" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮件通知">
          <el-switch v-model="createForm.email_notification" />
        </el-form-item>
        
        <!-- Selenium配置 -->
        <el-divider content-position="left">Selenium配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="无头模式">
              <el-switch v-model="createForm.headless" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="页面加载等待(秒)">
              <el-input-number v-model="createForm.page_load_wait" :min="1" :max="60" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="代理服务器">
              <el-input v-model="createForm.proxy" placeholder="http://host:port" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="User Agent">
          <el-input v-model="createForm.user_agent" type="textarea" :rows="2" placeholder="请输入User Agent" />
        </el-form-item>
        
        <!-- XPath配置 -->
        <el-divider content-position="left">XPath配置</el-divider>
        <el-form-item label="启用XPath">
          <el-switch v-model="createForm.enable_xpath" />
        </el-form-item>
        <el-form-item label="规则ID列表">
          <el-select
            v-model="createForm.rule_ids"
            multiple
            filterable
            placeholder="请选择要使用的XPath规则"
            style="width: 100%"
            :loading="loadingXPathRules"
          >
            <el-option
              v-for="rule in enabledXPathRules"
              :key="rule.rule_id"
              :label="`${rule.name} (${rule.rule_id})`"
              :value="rule.rule_id"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ rule.name }}</span>
                <span style="color: #999; font-size: 12px;">{{ rule.rule_id }}</span>
              </div>
            </el-option>
          </el-select>
          <div style="font-size: 12px; color: #999; margin-top: 4px;">选择要使用的XPath规则，支持多选和搜索</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createConfig" :loading="creating">
            创建配置
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑配置对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑爬虫配置"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="120px"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-form-item label="配置名称" required>
          <el-input v-model="editForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="配置描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入配置描述"
          />
        </el-form-item>
        
        <!-- 爬虫核心配置 -->
        <el-divider content-position="left">爬虫核心配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="超时时间(秒)">
              <el-input-number v-model="editForm.timeout" :min="1" :max="300" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="重试次数">
              <el-input-number v-model="editForm.retry" :min="0" :max="10" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大工作线程">
              <el-input-number v-model="editForm.max_workers" :min="1" :max="20" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用Selenium">
              <el-switch v-model="editForm.use_selenium" />
            </el-form-item>
          </el-col>
        </el-row>
        <!-- XPath启用开关已移除 - 通过rule_ids字段控制 -->
        <el-form-item label="User Agent">
          <el-input v-model="editForm.user_agent" type="textarea" :rows="2" placeholder="请输入User Agent" />
        </el-form-item>
        
        <!-- 存储配置 -->
        <el-divider content-position="left">存储配置</el-divider>
        <el-form-item label="数据目录">
          <el-input v-model="editForm.data_dir" placeholder="crawler_data" />
        </el-form-item>
        
        <!-- Selenium配置 -->
        <el-divider content-position="left">Selenium配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="无头模式">
              <el-switch v-model="editForm.headless" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="禁用GPU">
              <el-switch v-model="editForm.selenium_disable_gpu" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="禁用dev-shm">
              <el-switch v-model="editForm.selenium_disable_dev_shm_usage" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="窗口大小">
              <el-input v-model="editForm.selenium_window_size" placeholder="1920,1080" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="页面加载超时">
              <el-input-number v-model="editForm.selenium_page_load_timeout" :min="1" :max="300" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="隐式等待">
              <el-input-number v-model="editForm.selenium_implicit_wait" :min="1" :max="60" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- XPath配置 -->
        <el-divider content-position="left">XPath配置</el-divider>
        <el-form-item label="启用XPath">
          <el-switch v-model="editForm.enable_xpath" />
        </el-form-item>
        <el-form-item label="规则ID列表">
          <el-select
            v-model="editForm.rule_ids"
            multiple
            filterable
            placeholder="请选择要使用的XPath规则"
            style="width: 100%"
            :loading="loadingXPathRules"
          >
            <el-option
              v-for="rule in enabledXPathRules"
              :key="rule.rule_id"
              :label="`${rule.name} (${rule.rule_id})`"
              :value="rule.rule_id"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ rule.name }}</span>
                <span style="color: #999; font-size: 12px;">{{ rule.rule_id }}</span>
              </div>
            </el-option>
          </el-select>
          <div style="font-size: 12px; color: #999; margin-top: 4px;">选择要使用的XPath规则，支持多选和搜索</div>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="XPath规则路径">
              <el-input v-model="editForm.xpath_rules_path" placeholder="crawler/config/xpath/xpath_rules.json" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认规则ID">
              <el-input v-model="editForm.xpath_default_rule_id" placeholder="general_article" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 脚本配置 -->
        <el-divider content-position="left">脚本配置</el-divider>
        <el-form-item label="Stealth脚本路径">
          <el-input v-model="editForm.scripts_stealth_path" placeholder="crawler/config/scripts/stealth.min.js" />
        </el-form-item>
        
        <!-- 图片存储配置 -->
        <el-divider content-position="left">图片存储配置</el-divider>
        <el-form-item label="存储类型">
          <el-select v-model="editForm.image_storage_type" style="width: 100%">
            <el-option label="GitHub" value="github"></el-option>
            <el-option label="本地" value="local"></el-option>
          </el-select>
        </el-form-item>
        <!-- GitHub配置已移除 - 未在实际业务中使用 -->
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="info" @click="generateCommandFromEdit">
            <i class="fas fa-terminal"></i>
            生成命令
          </el-button>
          <el-button type="primary" @click="updateConfig" :loading="updating">
            更新配置
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 命令生成对话框 -->
    <el-dialog
      v-model="showCommandDialog"
      title="生成爬虫命令"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="command-generator">
        <el-form :model="commandForm" label-width="100px">
          <el-form-item label="目标URL" required>
            <el-input
              v-model="commandForm.url"
              placeholder="请输入要爬取的网站URL"
              maxlength="500"
            />
          </el-form-item>
        </el-form>
        
        <div v-if="generatedCommand" class="command-result">
          <h4>生成的命令：</h4>
          <div class="command-display">
            <pre>{{ generatedCommand }}</pre>
            <el-button
              type="primary"
              size="small"
              @click="copyCommand"
              class="copy-btn"
            >
              <i class="fas fa-copy"></i>
              复制命令
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCommandDialog = false">关闭</el-button>
          <el-button
            type="primary"
            @click="generateCommandAction"
            :loading="generatingCommand"
            :disabled="!commandForm.url"
          >
            生成命令
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { crawlerAPI } from '@/api/crawler'
import { xpathAPI } from '@/api/xpath'

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showCommandDialog = ref(false)
const createFormRef = ref(null)
const editFormRef = ref(null)
const loading = ref(false)
const creating = ref(false)
const updating = ref(false)
const loadingXPathRules = ref(false)
const enabledXPathRules = ref([])
const generatingCommand = ref(false)
const generatedCommand = ref('')
const currentConfig = ref(null)

const createForm = ref({
  name: '',
  description: '',
  // 爬虫核心配置
  timeout: 30,
  retry: 3,
  max_workers: 4,
  use_selenium: false,
  user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  // 存储配置
  data_dir: 'crawler_data',
  // Selenium配置
  selenium_headless: true,
  selenium_disable_gpu: true,
  selenium_disable_dev_shm_usage: true,
  selenium_window_size: '1920,1080',
  selenium_page_load_timeout: 30,
  selenium_implicit_wait: 10,
  // XPath配置
  enable_xpath: false,
  rule_ids: [],
  xpath_rules_path: 'crawler/config/xpath/xpath_rules.json',
  xpath_default_rule_id: 'general_article',
  // 脚本配置
  scripts_stealth_path: 'crawler/config/scripts/stealth.min.js',
  // 图片存储配置
  image_storage_type: 'github'
})

const editForm = ref({})
const configs = ref([])
const commandForm = ref({
  url: ''
})

// 验证配置名称唯一性
const validateConfigNameUnique = async (rule, value, callback) => {
  if (!value) {
    callback()
    return
  }
  
  // 检查当前配置列表中是否已存在相同名称
  const existingConfig = configs.value.find(config => config.name === value)
  if (existingConfig) {
    callback(new Error('配置名称已存在，请使用其他名称'))
    return
  }
  
  callback()
}

// 表单验证规则
const createFormRules = ref({
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 1, max: 50, message: '配置名称长度在1到50个字符', trigger: 'blur' },
    { validator: validateConfigNameUnique, trigger: 'blur' }
  ]
})

// 配置名称输入框失焦验证
const validateConfigName = () => {
  if (createFormRef.value) {
    createFormRef.value.validateField('name')
  }
}

// 获取配置列表
const fetchConfigs = async () => {
  try {
    loading.value = true
    const response = await crawlerAPI.getConfigs()
    // 后端返回的数据结构: {configs: [...], pagination: {...}}
    configs.value = response.data.configs || response.data || []
  } catch (error) {
    ElMessage.error('获取配置列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 获取启用状态的XPath规则
const fetchEnabledXPathRules = async () => {
  try {
    loadingXPathRules.value = true
    const response = await xpathAPI.getRules({ enabled: 'true' })
    enabledXPathRules.value = response.data.rules || response.data || []
  } catch (error) {
    console.error('获取XPath规则失败:', error)
    ElMessage.error('获取XPath规则失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loadingXPathRules.value = false
  }
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('MM-DD HH:mm')
}

// 切换配置状态
const toggleConfig = async (config) => {
  try {
    await crawlerAPI.updateConfig(config.id, { enabled: config.enabled })
    ElMessage.success(`配置 "${config.name}" 已${config.enabled ? '启用' : '禁用'}`)
  } catch (error) {
    config.enabled = !config.enabled // 回滚状态
    ElMessage.error('更新配置状态失败: ' + error.message)
  }
}

// 打开新建对话框
const openCreateDialog = () => {
  fetchEnabledXPathRules()
  showCreateDialog.value = true
}

// 编辑配置
const editConfig = (config) => {
  editForm.value = { ...config }
  // 处理rule_ids字段：如果是字符串，转换为数组
  if (typeof editForm.value.rule_ids === 'string') {
    editForm.value.rule_ids = editForm.value.rule_ids ? editForm.value.rule_ids.split(',').map(id => id.trim()) : []
  }
  // 获取最新的启用XPath规则列表
  fetchEnabledXPathRules()
  showEditDialog.value = true
}

// 删除配置
const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await crawlerAPI.deleteConfig(config.id)
    const index = configs.value.findIndex(c => c.id === config.id)
    if (index > -1) {
      configs.value.splice(index, 1)
    }
    ElMessage.success('配置删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除配置失败: ' + error.message)
    }
  }
}

// 创建配置
const createConfig = async () => {
  // 表单验证
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
  } catch (error) {
    ElMessage.error('请检查表单输入')
    return
  }
  
  try {
    creating.value = true
    const configData = {
      name: createForm.value.name,
      description: createForm.value.description,
      output: createForm.value.output,
      data_dir: createForm.value.data_dir,
      use_selenium: createForm.value.use_selenium,
      timeout: createForm.value.timeout,
      retry: createForm.value.retry,
      config: createForm.value.config,
      email_notification: createForm.value.email_notification,
      headless: createForm.value.headless,
      proxy: createForm.value.proxy,
      page_load_wait: createForm.value.page_load_wait,
      user_agent: createForm.value.user_agent,
      rule_ids: Array.isArray(createForm.value.rule_ids) ? createForm.value.rule_ids.join(',') : createForm.value.rule_ids,
      enable_xpath: createForm.value.enable_xpath
    }
    
    const response = await crawlerAPI.createConfig(configData)
    // 后端返回的数据结构: {config: {...}}
    const newConfig = response.data.config || response.data
    configs.value.push(newConfig)
    ElMessage.success('配置创建成功')
    showCreateDialog.value = false
    resetCreateForm()
  } catch (error) {
    // 特殊处理409冲突错误（配置名称已存在）
    if (error.response && error.response.status === 409) {
      ElMessage.error(`配置名称 "${createForm.value.name}" 已存在，请使用其他名称`)
    } else {
      ElMessage.error('创建配置失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    creating.value = false
  }
}

// 更新配置
const updateConfig = async () => {
  try {
    updating.value = true
    // 处理rule_ids：如果是数组，转换为字符串
    const updateData = { ...editForm.value }
    if (Array.isArray(updateData.rule_ids)) {
      updateData.rule_ids = updateData.rule_ids.join(',')
    }
    const response = await crawlerAPI.updateConfig(editForm.value.id, updateData)
    const index = configs.value.findIndex(c => c.id === editForm.value.id)
    if (index > -1) {
      // 后端返回的数据结构: {config: {...}}
      const updatedConfig = response.data.config || response.data
      configs.value[index] = updatedConfig
    }
    ElMessage.success('配置更新成功')
    showEditDialog.value = false
  } catch (error) {
    ElMessage.error('更新配置失败: ' + (error.response?.data?.message || error.message))
  } finally {
    updating.value = false
  }
}

// 生成命令（从配置卡片）
const generateCommand = (config) => {
  currentConfig.value = config
  commandForm.value.url = 'https://example.com' // 使用默认URL
  generatedCommand.value = ''
  showCommandDialog.value = true
  // 自动生成命令
  generateCommandAction()
}

// 生成命令（从编辑对话框）
const generateCommandFromEdit = () => {
  currentConfig.value = editForm.value
  commandForm.value.url = 'https://example.com' // 使用默认URL
  generatedCommand.value = ''
  showCommandDialog.value = true
  // 自动生成命令
  generateCommandAction()
}

// 执行命令生成
const generateCommandAction = async () => {
  if (!commandForm.value.url || !currentConfig.value) {
    ElMessage.error('请输入URL')
    return
  }
  
  try {
    generatingCommand.value = true
    // 直接在URL中拼接查询参数，避免axios参数序列化问题
    const url = `/crawler/configs/${currentConfig.value.id}/command?url=${encodeURIComponent(commandForm.value.url)}`
    const response = await crawlerAPI.getCommandDirect(url)
    generatedCommand.value = response.data.command
    ElMessage.success('命令生成成功')
  } catch (error) {
    ElMessage.error('生成命令失败: ' + (error.response?.data?.message || error.message))
  } finally {
    generatingCommand.value = false
  }
}

// 复制命令到剪贴板
const copyCommand = async () => {
  try {
    await navigator.clipboard.writeText(generatedCommand.value)
    ElMessage.success('命令已复制到剪贴板')
  } catch (error) {
    // 降级方案：创建临时文本区域
    const textArea = document.createElement('textarea')
    textArea.value = generatedCommand.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('命令已复制到剪贴板')
  }
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    name: '',
    description: '',
    data_dir: 'crawler_data',
    use_selenium: false,
    timeout: 30,
    retry: 3,
    email_notification: false,
    headless: true,
    proxy: '',
    page_load_wait: 10,
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    rule_ids: '',
    enable_xpath: false
  }
  
  // 清除表单验证状态
  if (createFormRef.value) {
    createFormRef.value.clearValidate()
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchConfigs()
  fetchEnabledXPathRules()
})
</script>

<style lang="scss" scoped>
.crawler-page {
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
      }
    }
  }
  
  .config-actions {
    display: flex;
    gap: 8px;
  }
}

// 命令生成对话框样式
.command-generator {
  .command-result {
    margin-top: 20px;
    
    h4 {
      margin: 0 0 12px 0;
      color: var(--text-primary);
      font-size: 14px;
      font-weight: 600;
    }
    
    .command-display {
      position: relative;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
      
      pre {
        margin: 0;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 13px;
        line-height: 1.5;
        color: var(--text-primary);
        white-space: pre-wrap;
        word-break: break-all;
      }
      
      .copy-btn {
        position: absolute;
        top: 8px;
        right: 8px;
      }
    }
  }
}
</style>