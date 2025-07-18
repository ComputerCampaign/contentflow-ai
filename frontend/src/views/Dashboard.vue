<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 用户信息卡片 -->
      <el-col :span="8">
        <el-card class="user-card">
          <template #header>
            <div class="card-header">
              <span>用户信息</span>
            </div>
          </template>
          
          <div class="user-info" v-if="currentUser">
            <h3>{{ currentUser.username }}</h3>
            <p>邮箱：{{ currentUser.email }}</p>
            <p>用户组：{{ currentUser.group ? currentUser.group.name : '未分配' }}</p>
            <p>注册时间：{{ formatDate(currentUser.created_at) }}</p>
            <p>上次登录：{{ currentUser.last_login ? formatDate(currentUser.last_login) : '首次登录' }}</p>
          </div>
          
          <div v-else class="loading-placeholder">
            <el-skeleton :rows="5" animated />
          </div>
        </el-card>
      </el-col>
      
      <!-- 任务统计卡片 -->
      <el-col :span="8">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>任务统计</span>
            </div>
          </template>
          
          <div class="stats-info" v-if="!loading">
            <div class="stat-item">
              <h2>{{ taskStats.total || 0 }}</h2>
              <p>总任务数</p>
            </div>
            
            <div class="stat-item">
              <h2>{{ taskStats.success || 0 }}</h2>
              <p>成功任务</p>
            </div>
            
            <div class="stat-item">
              <h2>{{ taskStats.failed || 0 }}</h2>
              <p>失败任务</p>
            </div>
          </div>
          
          <div v-else class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
        </el-card>
      </el-col>
      
      <!-- XPath规则统计卡片 -->
      <el-col :span="8">
        <el-card class="xpath-card">
          <template #header>
            <div class="card-header">
              <span>XPath规则</span>
            </div>
          </template>
          
          <div class="xpath-info" v-if="!loading">
            <div class="stat-item">
              <h2>{{ xpathStats.userRules || 0 }}</h2>
              <p>自定义规则</p>
            </div>
            
            <div class="stat-item">
              <h2>{{ xpathStats.systemRules || 0 }}</h2>
              <p>系统规则</p>
            </div>
            
            <div class="limit-info" v-if="currentUser && currentUser.group">
              <p>规则限制：{{ currentUser.group.max_xpath_rules === -1 ? '无限制' : currentUser.group.max_xpath_rules }}</p>
              <el-progress 
                :percentage="calculateUsagePercentage()" 
                :status="calculateUsageStatus()"
              ></el-progress>
            </div>
          </div>
          
          <div v-else class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近任务列表 -->
    <el-card class="recent-tasks-card">
      <template #header>
        <div class="card-header">
          <span>最近任务</span>
          <el-button type="primary" size="small" @click="$router.push('/crawler')">查看全部</el-button>
        </div>
      </template>
      
      <el-table v-if="!loading && tasks.length > 0" :data="recentTasks" style="width: 100%">
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
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="text" size="small" @click="viewTaskDetail(scope.row.task_id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-else-if="!loading && tasks.length === 0" class="empty-data">
        <el-empty description="暂无任务数据"></el-empty>
        <el-button type="primary" @click="$router.push('/crawler')">创建任务</el-button>
      </div>
      
      <div v-else class="loading-placeholder">
        <el-skeleton :rows="5" animated />
      </div>
    </el-card>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const loading = ref(true)
    const tasks = ref([])
    
    // 任务统计数据
    const taskStats = reactive({
      total: 0,
      success: 0,
      failed: 0
    })
    
    // XPath规则统计数据
    const xpathStats = reactive({
      userRules: 0,
      systemRules: 0
    })
    
    // 获取当前用户信息
    const currentUser = computed(() => store.getters['auth/currentUser'])
    
    // 获取最近5个任务
    const recentTasks = computed(() => tasks.value.slice(0, 5))
    
    // 计算XPath规则使用百分比
    const calculateUsagePercentage = () => {
      if (!currentUser.value || !currentUser.value.group) return 0
      
      const maxRules = currentUser.value.group.max_xpath_rules
      if (maxRules === -1) return 50 // 无限制显示为50%
      
      const userRules = xpathStats.userRules
      return Math.min(Math.round((userRules / maxRules) * 100), 100)
    }
    
    // 计算XPath规则使用状态
    const calculateUsageStatus = () => {
      if (!currentUser.value || !currentUser.value.group) return ''
      
      const maxRules = currentUser.value.group.max_xpath_rules
      if (maxRules === -1) return 'success' // 无限制显示为成功状态
      
      const userRules = xpathStats.userRules
      const percentage = (userRules / maxRules) * 100
      
      if (percentage >= 90) return 'exception'
      if (percentage >= 70) return 'warning'
      return 'success'
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    // 查看任务详情
    const viewTaskDetail = (taskId) => {
      router.push(`/crawler?task=${taskId}`)
    }
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      
      try {
        // 获取任务列表
        const tasksResponse = await store.dispatch('crawler/fetchTasks')
        tasks.value = tasksResponse.data.tasks || []
        
        // 计算任务统计
        taskStats.total = tasks.value.length
        taskStats.success = tasks.value.filter(task => task.status === 'success').length
        taskStats.failed = tasks.value.filter(task => task.status !== 'success').length
        
        // 获取XPath规则列表
        const userRulesResponse = await store.dispatch('xpath/fetchUserRules')
        const systemRulesResponse = await store.dispatch('xpath/fetchSystemRules')
        
        xpathStats.userRules = userRulesResponse.data.rules.length
        xpathStats.systemRules = systemRulesResponse.data.rules.length
      } catch (error) {
        console.error('加载仪表盘数据失败', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      loading,
      tasks,
      recentTasks,
      taskStats,
      xpathStats,
      currentUser,
      calculateUsagePercentage,
      calculateUsageStatus,
      formatDate,
      viewTaskDetail
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.el-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-card, .stats-card, .xpath-card {
  height: 300px;
}

.user-info h3 {
  margin-top: 0;
  color: #409EFF;
}

.stats-info, .xpath-info {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
  margin: 10px 0;
}

.stat-item h2 {
  margin: 0;
  color: #409EFF;
  font-size: 28px;
}

.stat-item p {
  margin: 5px 0;
  color: #606266;
}

.limit-info {
  width: 100%;
  margin-top: 20px;
  padding: 0 10px;
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

.empty-data .el-button {
  margin-top: 20px;
}
</style>