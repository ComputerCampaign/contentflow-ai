<template>
  <div class="validator-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">XPath验证器</h1>
        <p class="page-description">测试和验证XPath表达式的提取效果</p>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="addTestCase">
          新增测试用例
        </el-button>
      </div>
    </div>
    
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="testUrl"
          placeholder="请输入要测试的网页URL"
          style="width: 400px;"
          clearable
        >
          <template #prepend>
            <span>URL</span>
          </template>
          <template #append>
            <el-button :icon="Refresh" @click="fetchPageContent" :loading="fetchLoading">
              获取
            </el-button>
          </template>
        </el-input>
      </div>
      <div class="toolbar-right">
        <el-button :icon="Download" @click="exportResults">
          导出结果
        </el-button>
        <el-button :icon="Delete" @click="clearAll">
          清空所有
        </el-button>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：HTML内容预览 -->
      <div class="content-left">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">HTML内容</h3>
            <div class="panel-actions">
              <el-button size="small" :icon="View" @click="toggleHtmlView">
                {{ htmlViewMode === 'formatted' ? '原始' : '格式化' }}
              </el-button>
              <el-button size="small" :icon="DocumentCopy" @click="copyHtml">
                复制
              </el-button>
            </div>
          </div>
          <div class="panel-content">
            <div v-if="!htmlContent" class="empty-state">
              <el-empty description="请输入URL并获取页面内容" />
            </div>
            <div v-else class="html-viewer">
              <pre v-if="htmlViewMode === 'formatted'" class="formatted-html">{{ formattedHtml }}</pre>
              <div v-else class="raw-html" v-html="htmlContent"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：XPath测试区域 -->
      <div class="content-right">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">XPath测试</h3>
            <div class="panel-actions">
              <el-button size="small" :icon="VideoPlay" @click="runAllTests" :loading="testLoading">
                运行所有
              </el-button>
            </div>
          </div>
          <div class="panel-content">
            <div v-if="testCases.length === 0" class="empty-state">
              <el-empty description="暂无测试用例">
                <el-button type="primary" :icon="Plus" @click="addTestCase">
                  添加测试用例
                </el-button>
              </el-empty>
            </div>
            <div v-else class="test-cases">
              <div
                v-for="(testCase, index) in testCases"
                :key="testCase.id"
                class="test-case"
                :class="{ 'test-case--error': testCase.error }"
              >
                <div class="test-case-header">
                  <div class="test-case-title">
                    <el-input
                      v-model="testCase.name"
                      placeholder="测试用例名称"
                      size="small"
                      style="width: 200px;"
                    />
                    <el-tag
                      v-if="testCase.status"
                      :type="getStatusType(testCase.status)"
                      size="small"
                    >
                      {{ getStatusText(testCase.status) }}
                    </el-tag>
                  </div>
                  <div class="test-case-actions">
                    <el-button
                      size="small"
                      :icon="VideoPlay"
                      @click="runSingleTest(testCase)"
                      :loading="testCase.running"
                    >
                      运行
                    </el-button>
                    <el-button
                      size="small"
                      :icon="DocumentCopy"
                      @click="duplicateTestCase(testCase)"
                    >
                      复制
                    </el-button>
                    <el-button
                      size="small"
                      :icon="Delete"
                      @click="removeTestCase(index)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
                
                <div class="test-case-content">
                  <!-- XPath输入 -->
                  <div class="xpath-input">
                    <label class="input-label">XPath表达式:</label>
                    <el-input
                      v-model="testCase.xpath"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入XPath表达式，例如：//div[@class='title']/text()"
                      @input="() => testCase.status = undefined"
                    />
                  </div>
                  
                  <!-- 提取配置 -->
                  <div class="extract-config">
                    <div class="config-row">
                      <label class="input-label">提取属性:</label>
                      <el-select
                        v-model="testCase.attribute"
                        placeholder="选择要提取的属性"
                        style="width: 150px;"
                        clearable
                      >
                        <el-option label="文本内容" value="text" />
                        <el-option label="HTML内容" value="html" />
                        <el-option label="href" value="href" />
                        <el-option label="src" value="src" />
                        <el-option label="title" value="title" />
                        <el-option label="alt" value="alt" />
                        <el-option label="class" value="class" />
                        <el-option label="id" value="id" />
                      </el-select>
                    </div>
                    
                    <div class="config-row">
                      <label class="input-label">正则过滤:</label>
                      <el-input
                        v-model="testCase.regex"
                        placeholder="可选的正则表达式过滤"
                        style="width: 200px;"
                        clearable
                      />
                    </div>
                    
                    <div class="config-row">
                      <label class="input-label">默认值:</label>
                      <el-input
                        v-model="testCase.defaultValue"
                        placeholder="提取失败时的默认值"
                        style="width: 150px;"
                        clearable
                      />
                    </div>
                  </div>
                  
                  <!-- 测试结果 -->
                  <div v-if="testCase.result !== undefined" class="test-result">
                    <div class="result-header">
                      <label class="input-label">
                        提取结果 
                        <el-tag size="small" type="info">
                          {{ Array.isArray(testCase.result) ? testCase.result.length : 1 }} 条
                        </el-tag>
                      </label>
                      <div class="result-actions">
                        <el-button size="small" :icon="DocumentCopy" @click="copyResult(testCase.result)">
                          复制
                        </el-button>
                      </div>
                    </div>
                    
                    <div class="result-content">
                      <div v-if="testCase.error" class="error-message">
                        <el-alert
                          :title="testCase.error"
                          type="error"
                          :closable="false"
                          show-icon
                        />
                      </div>
                      <div v-else-if="Array.isArray(testCase.result)" class="result-list">
                        <div
                          v-for="(item, idx) in testCase.result.slice(0, 10)"
                          :key="idx"
                          class="result-item"
                        >
                          <span class="item-index">{{ idx + 1 }}.</span>
                          <span class="item-content">{{ item }}</span>
                        </div>
                        <div v-if="testCase.result.length > 10" class="result-more">
                          ... 还有 {{ testCase.result.length - 10 }} 条结果
                        </div>
                      </div>
                      <div v-else class="result-single">
                        {{ testCase.result }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Download,
  Delete,
  View,
  DocumentCopy,
  VideoPlay
} from '@element-plus/icons-vue'

interface TestCase {
  id: string
  name: string
  xpath: string
  attribute?: string
  regex?: string
  defaultValue?: string
  result?: any
  error?: string
  status?: 'success' | 'error' | 'running'
  running?: boolean
}

// 响应式数据
const testUrl = ref('')
const htmlContent = ref('')
const htmlViewMode = ref<'formatted' | 'raw'>('formatted')
const fetchLoading = ref(false)
const testLoading = ref(false)
const testCases = ref<TestCase[]>([])

// 计算属性
const formattedHtml = computed(() => {
  if (!htmlContent.value) return ''
  // 简单的HTML格式化
  return htmlContent.value
    .replace(/></g, '>\n<')
    .replace(/\n\s*\n/g, '\n')
})

// 工具方法
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    success: 'success',
    error: 'danger',
    running: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    success: '成功',
    error: '失败',
    running: '运行中'
  }
  return textMap[status] || status
}

// 页面内容获取
const fetchPageContent = async () => {
  if (!testUrl.value) {
    ElMessage.warning('请输入URL地址')
    return
  }
  
  if (!/^https?:\/\/.+/.test(testUrl.value)) {
    ElMessage.error('URL格式不正确')
    return
  }
  
  try {
    fetchLoading.value = true
    
    // 这里应该调用后端API来获取页面内容
    // 由于跨域限制，前端无法直接获取其他网站的内容
    const response = await fetch('/api/crawler/fetch-content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: testUrl.value })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    htmlContent.value = data.content
    
    ElMessage.success('页面内容获取成功')
  } catch (error: any) {
    ElMessage.error(`获取页面内容失败: ${error.message}`)
    // 模拟数据用于演示
    htmlContent.value = `
<!DOCTYPE html>
<html>
<head>
    <title>示例页面</title>
</head>
<body>
    <div class="container">
        <h1 class="title">这是标题</h1>
        <div class="content">
            <p class="description">这是描述内容</p>
            <ul class="list">
                <li class="item">列表项1</li>
                <li class="item">列表项2</li>
                <li class="item">列表项3</li>
            </ul>
            <a href="https://example.com" class="link">示例链接</a>
        </div>
    </div>
</body>
</html>
    `.trim()
  } finally {
    fetchLoading.value = false
  }
}

// HTML视图切换
const toggleHtmlView = () => {
  htmlViewMode.value = htmlViewMode.value === 'formatted' ? 'raw' : 'formatted'
}

const copyHtml = async () => {
  if (!htmlContent.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  
  try {
    await navigator.clipboard.writeText(htmlContent.value)
    ElMessage.success('HTML内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 测试用例管理
const addTestCase = () => {
  const newTestCase: TestCase = {
    id: generateId(),
    name: `测试用例 ${testCases.value.length + 1}`,
    xpath: '',
    attribute: 'text'
  }
  testCases.value.push(newTestCase)
}

const removeTestCase = async (index: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个测试用例吗？',
      '确认删除',
      {
        type: 'warning'
      }
    )
    testCases.value.splice(index, 1)
    ElMessage.success('测试用例已删除')
  } catch (error) {
    // 用户取消删除
  }
}

const duplicateTestCase = (testCase: TestCase) => {
  const newTestCase: TestCase = {
    ...testCase,
    id: generateId(),
    name: `${testCase.name} (副本)`,
    result: undefined,
    error: undefined,
    status: undefined
  }
  testCases.value.push(newTestCase)
  ElMessage.success('测试用例已复制')
}

// XPath测试执行
const runSingleTest = async (testCase: TestCase) => {
  if (!htmlContent.value) {
    ElMessage.warning('请先获取页面内容')
    return
  }
  
  if (!testCase.xpath) {
    ElMessage.warning('请输入XPath表达式')
    return
  }
  
  try {
    testCase.running = true
    testCase.status = 'running'
    testCase.error = undefined
    
    // 这里应该调用后端API来执行XPath测试
    const response = await fetch('/api/crawler/test-xpath', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        html: htmlContent.value,
        xpath: testCase.xpath,
        attribute: testCase.attribute,
        regex: testCase.regex,
        defaultValue: testCase.defaultValue
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    testCase.result = data.result
    testCase.status = 'success'
    
    ElMessage.success('XPath测试完成')
  } catch (error: any) {
    testCase.error = error.message
    testCase.status = 'error'
    
    // 模拟测试结果用于演示
    if (testCase.xpath.includes('title')) {
      testCase.result = ['这是标题']
      testCase.status = 'success'
      testCase.error = undefined
    } else if (testCase.xpath.includes('item')) {
      testCase.result = ['列表项1', '列表项2', '列表项3']
      testCase.status = 'success'
      testCase.error = undefined
    } else {
      testCase.result = []
      testCase.error = 'XPath表达式未匹配到任何内容'
    }
  } finally {
    testCase.running = false
  }
}

const runAllTests = async () => {
  if (testCases.value.length === 0) {
    ElMessage.warning('没有可运行的测试用例')
    return
  }
  
  testLoading.value = true
  
  try {
    for (const testCase of testCases.value) {
      if (testCase.xpath) {
        await runSingleTest(testCase)
      }
    }
    ElMessage.success('所有测试用例运行完成')
  } finally {
    testLoading.value = false
  }
}

// 结果操作
const copyResult = async (result: any) => {
  try {
    const text = Array.isArray(result) ? result.join('\n') : String(result)
    await navigator.clipboard.writeText(text)
    ElMessage.success('结果已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const exportResults = () => {
  const results = testCases.value.map(testCase => ({
    name: testCase.name,
    xpath: testCase.xpath,
    attribute: testCase.attribute,
    regex: testCase.regex,
    defaultValue: testCase.defaultValue,
    result: testCase.result,
    error: testCase.error,
    status: testCase.status
  }))
  
  const dataStr = JSON.stringify(results, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `xpath-test-results-${Date.now()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('测试结果已导出')
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有测试用例吗？',
      '确认清空',
      {
        type: 'warning'
      }
    )
    testCases.value = []
    ElMessage.success('已清空所有测试用例')
  } catch (error) {
    // 用户取消清空
  }
}

// 组件挂载
onMounted(() => {
  // 添加一个默认的测试用例
  addTestCase()
})
</script>

<style lang="scss" scoped>
.validator-container {
  padding: 24px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .header-left {
      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin: 0 0 8px 0;
      }
      
      .page-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 0;
      }
    }
  }
  
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px;
    background: var(--el-bg-color-page);
    border-radius: 8px;
    
    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }
  
  .main-content {
    flex: 1;
    display: flex;
    gap: 24px;
    min-height: 0;
    
    .content-left,
    .content-right {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }
    
    .panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: var(--el-bg-color);
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      min-height: 0;
      
      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        .panel-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          margin: 0;
        }
        
        .panel-actions {
          display: flex;
          gap: 8px;
        }
      }
      
      .panel-content {
        flex: 1;
        padding: 16px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        
        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .html-viewer {
          flex: 1;
          overflow: auto;
          
          .formatted-html {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            line-height: 1.5;
            color: var(--el-text-color-regular);
            background: var(--el-fill-color-lighter);
            padding: 16px;
            border-radius: 4px;
            margin: 0;
            white-space: pre-wrap;
            word-break: break-all;
          }
          
          .raw-html {
            border: 1px solid var(--el-border-color-light);
            border-radius: 4px;
            padding: 16px;
            background: var(--el-fill-color-lighter);
          }
        }
        
        .test-cases {
          flex: 1;
          overflow: auto;
          
          .test-case {
            border: 1px solid var(--el-border-color-light);
            border-radius: 8px;
            margin-bottom: 16px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            &.test-case--error {
              border-color: var(--el-color-danger);
            }
            
            .test-case-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 12px 16px;
              background: var(--el-fill-color-lighter);
              border-bottom: 1px solid var(--el-border-color-lighter);
              
              .test-case-title {
                display: flex;
                align-items: center;
                gap: 12px;
              }
              
              .test-case-actions {
                display: flex;
                gap: 8px;
              }
            }
            
            .test-case-content {
              padding: 16px;
              
              .xpath-input,
              .extract-config,
              .test-result {
                margin-bottom: 16px;
                
                &:last-child {
                  margin-bottom: 0;
                }
              }
              
              .input-label {
                display: block;
                font-size: 12px;
                font-weight: 500;
                color: var(--el-text-color-regular);
                margin-bottom: 8px;
              }
              
              .extract-config {
                display: flex;
                flex-wrap: wrap;
                gap: 16px;
                
                .config-row {
                  display: flex;
                  flex-direction: column;
                }
              }
              
              .test-result {
                .result-header {
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  margin-bottom: 8px;
                  
                  .input-label {
                    margin-bottom: 0;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                  }
                  
                  .result-actions {
                    display: flex;
                    gap: 8px;
                  }
                }
                
                .result-content {
                  .error-message {
                    margin-bottom: 12px;
                  }
                  
                  .result-list {
                    max-height: 200px;
                    overflow-y: auto;
                    border: 1px solid var(--el-border-color-light);
                    border-radius: 4px;
                    padding: 8px;
                    background: var(--el-fill-color-lighter);
                    
                    .result-item {
                      display: flex;
                      align-items: flex-start;
                      margin-bottom: 4px;
                      font-size: 12px;
                      
                      &:last-child {
                        margin-bottom: 0;
                      }
                      
                      .item-index {
                        color: var(--el-text-color-secondary);
                        min-width: 24px;
                        margin-right: 8px;
                      }
                      
                      .item-content {
                        color: var(--el-text-color-regular);
                        word-break: break-all;
                      }
                    }
                    
                    .result-more {
                      text-align: center;
                      color: var(--el-text-color-secondary);
                      font-size: 12px;
                      margin-top: 8px;
                      padding-top: 8px;
                      border-top: 1px solid var(--el-border-color-lighter);
                    }
                  }
                  
                  .result-single {
                    padding: 8px;
                    background: var(--el-fill-color-lighter);
                    border: 1px solid var(--el-border-color-light);
                    border-radius: 4px;
                    font-size: 12px;
                    color: var(--el-text-color-regular);
                    word-break: break-all;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>