<template>
  <div class="state-display" :class="[`state-${state}`, { 'full-height': fullHeight }]">
    <!-- 加载状态 -->
    <div v-if="state === 'loading'" class="state-content loading-state">
      <el-icon class="state-icon loading-icon" :size="iconSize">
        <Loading />
      </el-icon>
      <div class="state-text">{{ loadingText }}</div>
      <div v-if="loadingTip" class="state-tip">{{ loadingTip }}</div>
    </div>
    
    <!-- 空数据状态 -->
    <div v-else-if="state === 'empty'" class="state-content empty-state">
      <el-icon class="state-icon empty-icon" :size="iconSize">
        <Box />
      </el-icon>
      <div class="state-text">{{ emptyText }}</div>
      <div v-if="emptyTip" class="state-tip">{{ emptyTip }}</div>
      <div v-if="showEmptyAction" class="state-actions">
        <slot name="empty-action">
          <el-button type="primary" @click="handleEmptyAction">
            {{ emptyActionText }}
          </el-button>
        </slot>
      </div>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="state === 'error'" class="state-content error-state">
      <el-icon class="state-icon error-icon" :size="iconSize">
        <Warning />
      </el-icon>
      <div class="state-text">{{ errorText }}</div>
      <div v-if="errorMessage" class="state-message">{{ errorMessage }}</div>
      <div v-if="errorTip" class="state-tip">{{ errorTip }}</div>
      <div v-if="showErrorAction" class="state-actions">
        <slot name="error-action">
          <el-button type="primary" @click="handleErrorAction">
            {{ errorActionText }}
          </el-button>
        </slot>
      </div>
    </div>
    
    <!-- 网络错误状态 -->
    <div v-else-if="state === 'network-error'" class="state-content network-error-state">
      <el-icon class="state-icon network-error-icon" :size="iconSize">
        <Connection />
      </el-icon>
      <div class="state-text">{{ networkErrorText }}</div>
      <div v-if="networkErrorTip" class="state-tip">{{ networkErrorTip }}</div>
      <div class="state-actions">
        <slot name="network-error-action">
          <el-button type="primary" @click="handleNetworkErrorAction">
            {{ networkErrorActionText }}
          </el-button>
        </slot>
      </div>
    </div>
    
    <!-- 无权限状态 -->
    <div v-else-if="state === 'no-permission'" class="state-content no-permission-state">
      <el-icon class="state-icon no-permission-icon" :size="iconSize">
        <Lock />
      </el-icon>
      <div class="state-text">{{ noPermissionText }}</div>
      <div v-if="noPermissionTip" class="state-tip">{{ noPermissionTip }}</div>
      <div v-if="showNoPermissionAction" class="state-actions">
        <slot name="no-permission-action">
          <el-button type="primary" @click="handleNoPermissionAction">
            {{ noPermissionActionText }}
          </el-button>
        </slot>
      </div>
    </div>
    
    <!-- 成功状态 -->
    <div v-else-if="state === 'success'" class="state-content success-state">
      <el-icon class="state-icon success-icon" :size="iconSize">
        <CircleCheck />
      </el-icon>
      <div class="state-text">{{ successText }}</div>
      <div v-if="successTip" class="state-tip">{{ successTip }}</div>
      <div v-if="showSuccessAction" class="state-actions">
        <slot name="success-action">
          <el-button type="primary" @click="handleSuccessAction">
            {{ successActionText }}
          </el-button>
        </slot>
      </div>
    </div>
    
    <!-- 自定义状态 -->
    <div v-else-if="state === 'custom'" class="state-content custom-state">
      <slot name="custom" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Loading,
  Box,
  Warning,
  Connection,
  Lock,
  CircleCheck
} from '@element-plus/icons-vue'

// 状态类型
type StateType = 'loading' | 'empty' | 'error' | 'network-error' | 'no-permission' | 'success' | 'custom'

// 组件属性接口
interface Props {
  state: StateType
  fullHeight?: boolean
  iconSize?: number
  
  // 加载状态
  loadingText?: string
  loadingTip?: string
  
  // 空数据状态
  emptyText?: string
  emptyTip?: string
  showEmptyAction?: boolean
  emptyActionText?: string
  
  // 错误状态
  errorText?: string
  errorMessage?: string
  errorTip?: string
  showErrorAction?: boolean
  errorActionText?: string
  
  // 网络错误状态
  networkErrorText?: string
  networkErrorTip?: string
  networkErrorActionText?: string
  
  // 无权限状态
  noPermissionText?: string
  noPermissionTip?: string
  showNoPermissionAction?: boolean
  noPermissionActionText?: string
  
  // 成功状态
  successText?: string
  successTip?: string
  showSuccessAction?: boolean
  successActionText?: string
}

// 定义属性默认值
const props = withDefaults(defineProps<Props>(), {
  state: 'loading',
  fullHeight: false,
  iconSize: 64,
  
  // 加载状态默认值
  loadingText: '加载中...',
  
  // 空数据状态默认值
  emptyText: '暂无数据',
  emptyTip: '当前没有可显示的内容',
  showEmptyAction: false,
  emptyActionText: '刷新',
  
  // 错误状态默认值
  errorText: '出现错误',
  errorTip: '请稍后重试或联系管理员',
  showErrorAction: true,
  errorActionText: '重试',
  
  // 网络错误状态默认值
  networkErrorText: '网络连接失败',
  networkErrorTip: '请检查网络连接后重试',
  networkErrorActionText: '重新连接',
  
  // 无权限状态默认值
  noPermissionText: '无访问权限',
  noPermissionTip: '您没有权限访问此内容',
  showNoPermissionAction: false,
  noPermissionActionText: '申请权限',
  
  // 成功状态默认值
  successText: '操作成功',
  showSuccessAction: false,
  successActionText: '继续'
})

// 定义事件
const emit = defineEmits<{
  emptyAction: []
  errorAction: []
  networkErrorAction: []
  noPermissionAction: []
  successAction: []
}>()

// 处理空数据操作
const handleEmptyAction = () => {
  emit('emptyAction')
}

// 处理错误操作
const handleErrorAction = () => {
  emit('errorAction')
}

// 处理网络错误操作
const handleNetworkErrorAction = () => {
  emit('networkErrorAction')
}

// 处理无权限操作
const handleNoPermissionAction = () => {
  emit('noPermissionAction')
}

// 处理成功操作
const handleSuccessAction = () => {
  emit('successAction')
}
</script>

<style lang="scss" scoped>
.state-display {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  
  &.full-height {
    min-height: 400px;
  }
  
  .state-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    max-width: 400px;
    
    .state-icon {
      margin-bottom: 16px;
      
      &.loading-icon {
        color: var(--el-color-primary);
        animation: rotate 2s linear infinite;
      }
      
      &.empty-icon {
        color: var(--el-text-color-placeholder);
      }
      
      &.error-icon {
        color: var(--el-color-danger);
      }
      
      &.network-error-icon {
        color: var(--el-color-warning);
      }
      
      &.no-permission-icon {
        color: var(--el-color-info);
      }
      
      &.success-icon {
        color: var(--el-color-success);
      }
    }
    
    .state-text {
      font-size: 16px;
      font-weight: 500;
      color: var(--el-text-color-primary);
      margin-bottom: 8px;
      line-height: 1.4;
    }
    
    .state-message {
      font-size: 14px;
      color: var(--el-color-danger);
      margin-bottom: 8px;
      padding: 8px 12px;
      background-color: var(--el-color-danger-light-9);
      border: 1px solid var(--el-color-danger-light-7);
      border-radius: 4px;
      word-break: break-word;
    }
    
    .state-tip {
      font-size: 14px;
      color: var(--el-text-color-regular);
      margin-bottom: 20px;
      line-height: 1.5;
    }
    
    .state-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      justify-content: center;
    }
  }
  
  // 不同状态的特殊样式
  &.state-loading {
    .state-content {
      .state-text {
        color: var(--el-color-primary);
      }
    }
  }
  
  &.state-empty {
    .state-content {
      .state-text {
        color: var(--el-text-color-secondary);
      }
    }
  }
  
  &.state-error {
    .state-content {
      .state-text {
        color: var(--el-color-danger);
      }
    }
  }
  
  &.state-network-error {
    .state-content {
      .state-text {
        color: var(--el-color-warning);
      }
    }
  }
  
  &.state-no-permission {
    .state-content {
      .state-text {
        color: var(--el-color-info);
      }
    }
  }
  
  &.state-success {
    .state-content {
      .state-text {
        color: var(--el-color-success);
      }
    }
  }
}

// 旋转动画
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .state-display {
    padding: 30px 16px;
    
    &.full-height {
      min-height: 300px;
    }
    
    .state-content {
      max-width: 300px;
      
      .state-icon {
        margin-bottom: 12px;
      }
      
      .state-text {
        font-size: 15px;
        margin-bottom: 6px;
      }
      
      .state-message {
        font-size: 13px;
        margin-bottom: 6px;
        padding: 6px 10px;
      }
      
      .state-tip {
        font-size: 13px;
        margin-bottom: 16px;
      }
      
      .state-actions {
        gap: 8px;
        
        .el-button {
          font-size: 13px;
        }
      }
    }
  }
}

// 紧凑模式
.state-display.compact {
  padding: 24px 16px;
  
  .state-content {
    .state-icon {
      margin-bottom: 12px;
    }
    
    .state-text {
      font-size: 14px;
      margin-bottom: 6px;
    }
    
    .state-tip {
      font-size: 13px;
      margin-bottom: 16px;
    }
  }
}
</style>