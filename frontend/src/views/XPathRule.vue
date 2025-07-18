<template>
  <div class="xpath-rule-container">
    <el-row :gutter="20">
      <!-- 左侧：规则列表 -->
      <el-col :span="8">
        <el-card class="rule-list-card">
          <template #header>
            <div class="card-header">
              <span>XPath规则列表</span>
              <el-button type="primary" size="small" @click="showCreateForm">新建规则</el-button>
            </div>
          </template>
          
          <el-tabs v-model="activeTab" @tab-click="handleTabClick">
            <el-tab-pane label="我的规则" name="user">
              <div v-if="loading" class="loading-placeholder">
                <el-skeleton :rows="5" animated />
              </div>
              
              <div v-else-if="userRules.length === 0" class="empty-data">
                <el-empty description="暂无自定义规则"></el-empty>
              </div>
              
              <el-menu
                v-else
                :default-active="activeRuleId.toString()"
                @select="handleRuleSelect"
              >
                <el-menu-item 
                  v-for="rule in userRules" 
                  :key="rule.id"
                  :index="rule.id.toString()"
                >
                  <span>{{ rule.rule_name }}</span>
                </el-menu-item>
              </el-menu>
            </el-tab-pane>
            
            <el-tab-pane label="系统规则" name="system">
              <div v-if="loading" class="loading-placeholder">
                <el-skeleton :rows="5" animated />
              </div>
              
              <div v-else-if="systemRules.length === 0" class="empty-data">
                <el-empty description="暂无系统规则"></el-empty>
              </div>
              
              <el-menu
                v-else
                :default-active="activeRuleId.toString()"
                @select="handleRuleSelect"
              >
                <el-menu-item 
                  v-for="rule in systemRules" 
                  :key="rule.id"
                  :index="rule.id.toString()"
                >
                  <span>{{ rule.name }}</span>
                </el-menu-item>
              </el-menu>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <!-- 右侧：规则详情/编辑 -->
      <el-col :span="16">
        <el-card v-if="!showForm && currentRule" class="rule-detail-card">
          <template #header>
            <div class="card-header">
              <span>{{ isUserRule ? currentRule.rule_name : currentRule.name }}</span>
              <div v-if="isUserRule" class="header-actions">
                <el-button type="primary" size="small" @click="editRule">编辑</el-button>
                <el-popconfirm
                  title="确定要删除此规则吗？"
                  @confirm="deleteRule"
                >
                  <template #reference>
                    <el-button type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="规则名称">
              {{ isUserRule ? currentRule.rule_name : currentRule.name }}
            </el-descriptions-item>
            <el-descriptions-item label="描述" v-if="currentRule.description">
              {{ currentRule.description }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间" v-if="currentRule.created_at">
              {{ formatDate(currentRule.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="rule-content">
            <h3>XPath规则内容</h3>
            <el-tabs v-model="contentTab">
              <el-tab-pane label="JSON视图" name="json">
                <pre class="json-view">{{ formatJson(currentRule.rule_content) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="原始视图" name="raw">
                <pre class="raw-view">{{ currentRule.rule_content }}</pre>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
        
        <el-card v-else-if="showForm" class="rule-form-card">
          <template #header>
            <div class="card-header">
              <span>{{ isEditing ? '编辑规则' : '创建规则' }}</span>
            </div>
          </template>
          
          <el-form :model="ruleForm" :rules="rules" ref="ruleFormRef" label-width="100px">
            <el-form-item label="规则名称" prop="rule_name">
              <el-input v-model="ruleForm.rule_name" placeholder="请输入规则名称"></el-input>
            </el-form-item>
            
            <el-form-item label="描述" prop="description">
              <el-input 
                v-model="ruleForm.description" 
                type="textarea" 
                placeholder="请输入规则描述"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="规则内容" prop="rule_content">
              <el-input 
                v-model="ruleForm.rule_content" 
                type="textarea" 
                :rows="10"
                placeholder="请输入JSON格式的XPath规则内容"
              ></el-input>
              <div class="form-tip">
                <p>规则内容必须是有效的JSON格式，例如：</p>
                <pre>{
  "title": "//h1",
  "content": "//div[@class='article-content']",
  "author": "//span[@class='author']/text()",
  "date": "//time[@class='published']/@datetime"
}</pre>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="submitRule">{{ isEditing ? '更新' : '创建' }}</el-button>
              <el-button @click="cancelForm">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-empty v-else description="请选择或创建一个XPath规则"></el-empty>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'XPathRule',
  setup() {
    const store = useStore()
    
    const loading = ref(false)
    const activeTab = ref('user')
    const contentTab = ref('json')
    const activeRuleId = ref('')
    const currentRule = ref(null)
    const showForm = ref(false)
    const isEditing = ref(false)
    const ruleFormRef = ref(null)
    
    // 表单数据
    const ruleForm = reactive({
      rule_name: '',
      description: '',
      rule_content: ''
    })
    
    // 表单验证规则
    const rules = {
      rule_name: [
        { required: true, message: '请输入规则名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      rule_content: [
        { required: true, message: '请输入规则内容', trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            try {
              if (value) {
                JSON.parse(value)
              }
              callback()
            } catch (error) {
              callback(new Error('规则内容必须是有效的JSON格式'))
            }
          }, 
          trigger: 'blur' 
        }
      ]
    }
    
    // 计算属性
    const userRules = computed(() => store.getters['xpath/userRules'])
    const systemRules = computed(() => store.getters['xpath/systemRules'])
    const isUserRule = computed(() => activeTab.value === 'user')
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    // 格式化JSON
    const formatJson = (jsonString) => {
      try {
        const obj = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString
        return JSON.stringify(obj, null, 2)
      } catch (error) {
        return jsonString
      }
    }
    
    // 处理标签页切换
    const handleTabClick = () => {
      // 切换标签页时清除当前选中的规则
      currentRule.value = null
      activeRuleId.value = ''
    }
    
    // 处理规则选择
    const handleRuleSelect = async (index) => {
      activeRuleId.value = index
      loading.value = true
      
      try {
        const response = await store.dispatch('xpath/fetchRuleDetail', {
          ruleId: index,
          isUserRule: isUserRule.value
        })
        
        currentRule.value = response.data
        showForm.value = false
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '获取规则详情失败')
      } finally {
        loading.value = false
      }
    }
    
    // 显示创建表单
    const showCreateForm = () => {
      isEditing.value = false
      showForm.value = true
      currentRule.value = null
      
      // 重置表单
      Object.assign(ruleForm, {
        rule_name: '',
        description: '',
        rule_content: ''
      })
    }
    
    // 编辑规则
    const editRule = () => {
      if (!currentRule.value || !isUserRule.value) return
      
      isEditing.value = true
      showForm.value = true
      
      // 填充表单数据
      Object.assign(ruleForm, {
        rule_name: currentRule.value.rule_name,
        description: currentRule.value.description || '',
        rule_content: typeof currentRule.value.rule_content === 'string' 
          ? currentRule.value.rule_content 
          : JSON.stringify(currentRule.value.rule_content, null, 2)
      })
    }
    
    // 删除规则
    const deleteRule = async () => {
      if (!currentRule.value || !isUserRule.value) return
      
      loading.value = true
      
      try {
        await store.dispatch('xpath/deleteRule', currentRule.value.id)
        
        // 重新加载用户规则列表
        await store.dispatch('xpath/fetchUserRules')
        
        // 清除当前选中的规则
        currentRule.value = null
        activeRuleId.value = ''
        
        ElMessage.success('规则删除成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '删除规则失败')
      } finally {
        loading.value = false
      }
    }
    
    // 提交规则
    const submitRule = () => {
      ruleFormRef.value.validate(async valid => {
        if (valid) {
          loading.value = true
          
          try {
            // 确保规则内容是有效的JSON
            const ruleContent = JSON.parse(ruleForm.rule_content)
            
            if (isEditing.value) {
              // 更新规则
              await store.dispatch('xpath/updateRule', {
                id: currentRule.value.id,
                rule_name: ruleForm.rule_name,
                description: ruleForm.description,
                rule_content: ruleContent
              })
              
              ElMessage.success('规则更新成功')
            } else {
              // 创建规则
              await store.dispatch('xpath/createRule', {
                rule_name: ruleForm.rule_name,
                description: ruleForm.description,
                rule_content: ruleContent
              })
              
              ElMessage.success('规则创建成功')
            }
            
            // 重新加载用户规则列表
            await store.dispatch('xpath/fetchUserRules')
            
            // 关闭表单
            showForm.value = false
            currentRule.value = null
            activeRuleId.value = ''
          } catch (error) {
            ElMessage.error(error.response?.data?.error || (isEditing.value ? '更新规则失败' : '创建规则失败'))
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    // 取消表单
    const cancelForm = () => {
      showForm.value = false
      
      // 如果是编辑模式，返回到规则详情
      if (isEditing.value && currentRule.value) {
        isEditing.value = false
      } else {
        // 如果是创建模式，清除当前选中的规则
        currentRule.value = null
        activeRuleId.value = ''
      }
    }
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      
      try {
        // 加载用户规则列表
        await store.dispatch('xpath/fetchUserRules')
        
        // 加载系统规则列表
        await store.dispatch('xpath/fetchSystemRules')
      } catch (error) {
        console.error('加载规则列表失败', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      loading,
      activeTab,
      contentTab,
      activeRuleId,
      currentRule,
      showForm,
      isEditing,
      ruleForm,
      rules,
      ruleFormRef,
      userRules,
      systemRules,
      isUserRule,
      formatDate,
      formatJson,
      handleTabClick,
      handleRuleSelect,
      showCreateForm,
      editRule,
      deleteRule,
      submitRule,
      cancelForm
    }
  }
}
</script>

<style scoped>
.xpath-rule-container {
  padding: 20px;
}

.rule-list-card, .rule-detail-card, .rule-form-card {
  height: calc(100vh - 180px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-placeholder {
  padding: 20px;
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.rule-content {
  margin-top: 20px;
}

.rule-content h3 {
  margin-bottom: 15px;
  color: #303133;
}

.json-view, .raw-view {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.form-tip {
  margin-top: 10px;
  color: #909399;
  font-size: 12px;
}

.form-tip pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-top: 5px;
  font-family: monospace;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}
</style>