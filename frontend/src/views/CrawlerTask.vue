<template>
  <div class="crawler-task-container">
    <!-- 任务创建表单 -->
    <el-card class="task-form-card">
      <template #header>
        <div class="card-header">
          <span>创建爬虫任务</span>
        </div>
      </template>
      
      <el-form :model="taskForm" :rules="rules" ref="taskFormRef" label-width="120px">
        <el-form-item label="URL" prop="url">
          <el-input v-model="taskForm.url" placeholder="请输入要爬取的URL"></el-input>
        </el-form-item>
        
        <el-form-item label="任务名称" prop="task_name">
          <el-input v-model="taskForm.task_name" placeholder="可选，默认自动生成"></el-input>
        </el-form-item>
        
        <el-form-item label="使用Selenium">
          <el-switch v-model="taskForm.use_selenium"></el-switch>
          <span class="form-tip">对于动态加载内容的网页，建议启用</span>
        </el-form-item>
        
        <el-form-item label="使用XPath解析">
          <el-switch v-model="taskForm.use_xpath"></el-switch>
          <span class="form-tip">启用后可以提取网页中的特定内容</span>
        </el-form-item>
        
        <el-form-item label="XPath规则" v-if="taskForm.use_xpath">
          <el-radio-group v-model="taskForm.is_user_rule">
            <el-radio :label="false">系统规则</el-radio>
            <el-radio :label="true">自定义规则</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="选择规则" v-if="taskForm.use_xpath">
          <el-select 
            v-model="taskForm.xpath_rule_id" 
            placeholder="请选择XPath规则"
            filterable
          >
            <el-option-group v-if="!taskForm.is_user_rule" label="系统规则">
              <el-option 
                v-for="rule in systemRules" 
                :key="rule.id" 
                :label="rule.name" 
                :value="rule.id"
              ></el-option>
            </el-option-group>
            
            <el-option-group v-else label="自定义规则">
              <el-option 
                v-for="rule in userRules" 
                :key="rule.id" 
                :label="rule.rule_name" 
                :value="rule.id"
              ></el-option>
            </el-option-group>
          </el-select>
          
          <div class="rule-actions" v-if="taskForm.is_user_rule">
            <el-button type="text" @click="$router.push('/xpath')">管理规则</el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="博客模板">
          <el-select v-model="taskForm.blog_template" placeholder="可选，选择博客生成模板">
            <el-option label="不使用模板" value=""></el-option>
            <el-option 
              v-for="template in templates" 
              :key="template.name" 
              :label="template.name" 
              :value="template.name"
            >
              <span>{{ template.name }}</span>
              <span class="template-desc">{{ template.description }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitTask">创建任务</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务"
            style="width: 200px"
            clearable
          ></el-input>
        </div>
      </template>
      
      <el-table 
        v-if="!loading && tasks.length > 0" 
        :data="filteredTasks" 
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="task_id" label="任务ID" width="180"></el-table-column>
        <el-table-column prop="url" label="URL" show-overflow-tooltip></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
              {{ scope.row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button type="text" size="small" @click.stop="viewTaskDetail(scope.row.task_id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-else-if="!loading && tasks.length === 0" class="empty-data">
        <el-empty description="暂无任务数据"></el-empty>
      </div>
      
      <div v-else class="loading-placeholder">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div class="pagination-container" v-if="tasks.length > 0">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="filteredTasks.length"
          :page-size="pageSize"
          :current-page.sync="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </el-card>
    
    <!-- 任务详情对话框 -->
    <el-dialog 
      title="任务详情" 
      v-model="taskDetailVisible" 
      width="70%"
    >
      <div v-if="currentTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentTask.task_id }}</el-descriptions-item>
          <el-descriptions-item label="URL">
            <el-link type="primary" :href="currentTask.url" target="_blank">{{ currentTask.url }}</el-link>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentTask.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentTask.status === 'success' ? 'success' : 'danger'">
              {{ currentTask.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="使用Selenium">{{ currentTask.use_selenium ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="使用XPath">{{ currentTask.use_xpath ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="XPath规则" v-if="currentTask.use_xpath">
            {{ currentTask.is_user_rule ? '自定义规则' : '系统规则' }}: {{ getXPathRuleName(currentTask.xpath_rule_id, currentTask.is_user_rule) }}
          </el-descriptions-item>
          <el-descriptions-item label="博客模板" v-if="currentTask.blog_template">
            {{ currentTask.blog_template }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="output-files" v-if="currentTask.output_files && currentTask.output_files.length > 0">
          <h3>输出文件</h3>
          <el-table :data="currentTask.output_files" style="width: 100%">
            <el-table-column prop="name" label="文件名"></el-table-column>
            <el-table-column prop="path" label="路径"></el-table-column>
            <el-table-column prop="size" label="大小">
              <template #default="scope">
                {{ formatFileSize(scope.row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <div v-else class="loading-placeholder">
        <el-skeleton :rows="5" animated />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'

export default {
  name: 'CrawlerTask',
  setup() {
    const store = useStore()
    const route = useRoute()
    
    const taskFormRef = ref(null)
    const loading = ref(false)
    const tasks = ref([])
    const searchQuery = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const taskDetailVisible = ref(false)
    const currentTask = ref(null)
    
    // 表单数据
    const taskForm = reactive({
      url: '',
      task_name: '',
      use_selenium: false,
      use_xpath: false,
      xpath_rule_id: '',
      is_user_rule: false,
      blog_template: ''
    })
    
    // 表单验证规则
    const rules = {
      url: [
        { required: true, message: '请输入URL', trigger: 'blur' },
        { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
      ]
    }
    
    // 获取XPath规则列表
    const userRules = computed(() => store.getters['xpath/userRules'])
    const systemRules = computed(() => store.getters['xpath/systemRules'])
    
    // 获取可用的博客模板
    const templates = computed(() => store.getters['crawler/availableTemplates'])
    
    // 过滤后的任务列表
    const filteredTasks = computed(() => {
      if (!searchQuery.value) return tasks.value
      
      const query = searchQuery.value.toLowerCase()
      return tasks.value.filter(task => 
        task.task_id.toLowerCase().includes(query) ||
        task.url.toLowerCase().includes(query)
      )
    })
    
    // 分页后的任务列表
    const paginatedTasks = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredTasks.value.slice(start, end)
    })
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    // 获取XPath规则名称
    const getXPathRuleName = (ruleId, isUserRule) => {
      if (isUserRule) {
        const rule = userRules.value.find(r => r.id === parseInt(ruleId))
        return rule ? rule.rule_name : ruleId
      } else {
        const rule = systemRules.value.find(r => r.id === ruleId)
        return rule ? rule.name : ruleId
      }
    }
    
    // 提交任务
    const submitTask = () => {
      taskFormRef.value.validate(async valid => {
        if (valid) {
          loading.value = true
          
          try {
            await store.dispatch('crawler/createTask', taskForm)
            
            // 重新加载任务列表
            await loadTasks()
            
            // 重置表单
            resetForm()
            
            // 显示成功消息
            ElMessage.success('任务创建成功')
          } catch (error) {
            ElMessage.error(error.response?.data?.error || '任务创建失败')
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    // 重置表单
    const resetForm = () => {
      taskFormRef.value.resetFields()
      Object.assign(taskForm, {
        url: '',
        task_name: '',
        use_selenium: false,
        use_xpath: false,
        xpath_rule_id: '',
        is_user_rule: false,
        blog_template: ''
      })
    }
    
    // 查看任务详情
    const viewTaskDetail = async (taskId) => {
      loading.value = true
      
      try {
        const response = await store.dispatch('crawler/fetchTaskDetail', taskId)
        currentTask.value = response.data
        taskDetailVisible.value = true
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '获取任务详情失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理表格行点击
    const handleRowClick = (row) => {
      viewTaskDetail(row.task_id)
    }
    
    // 处理分页变化
    const handlePageChange = (page) => {
      currentPage.value = page
    }
    
    // 加载任务列表
    const loadTasks = async () => {
      loading.value = true
      
      try {
        const response = await store.dispatch('crawler/fetchTasks')
        tasks.value = response.data.tasks || []
      } catch (error) {
        console.error('加载任务列表失败', error)
      } finally {
        loading.value = false
      }
    }
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      
      try {
        // 加载任务列表
        await loadTasks()
        
        // 加载XPath规则
        await store.dispatch('xpath/fetchUserRules')
        await store.dispatch('xpath/fetchSystemRules')
        
        // 加载博客模板
        await store.dispatch('crawler/fetchTemplates')
        
        // 检查URL参数中是否有任务ID
        const taskId = route.query.task
        if (taskId) {
          await viewTaskDetail(taskId)
        }
      } catch (error) {
        console.error('加载数据失败', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      taskFormRef,
      taskForm,
      rules,
      loading,
      tasks,
      filteredTasks,
      paginatedTasks,
      searchQuery,
      currentPage,
      pageSize,
      userRules,
      systemRules,
      templates,
      taskDetailVisible,
      currentTask,
      formatDate,
      formatFileSize,
      getXPathRuleName,
      submitTask,
      resetForm,
      viewTaskDetail,
      handleRowClick,
      handlePageChange
    }
  }
}
</script>

<style scoped>
.crawler-task-container {
  padding: 20px;
}

.task-form-card, .task-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.rule-actions {
  margin-top: 5px;
}

.template-desc {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.loading-placeholder {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.task-detail {
  padding: 10px;
}

.output-files {
  margin-top: 20px;
}

.output-files h3 {
  margin-bottom: 15px;
  color: #303133;
}

.el-table {
  --el-table-row-hover-bg-color: #f5f7fa;
}

.el-table .el-table__row {
  cursor: pointer;
}
</style>