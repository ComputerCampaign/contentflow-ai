<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :fullscreen="fullscreen"
    :top="top"
    :modal="modal"
    :modal-class="modalClass"
    :append-to-body="appendToBody"
    :lock-scroll="lockScroll"
    :custom-class="customClass"
    :open-delay="openDelay"
    :close-delay="closeDelay"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :before-close="handleBeforeClose"
    :center="center"
    :align-center="alignCenter"
    :destroy-on-close="destroyOnClose"
    @open="handleOpen"
    @opened="handleOpened"
    @close="handleClose"
    @closed="handleClosed"
  >
    <!-- 自定义标题 -->
    <template v-if="$slots.title" #title>
      <slot name="title" />
    </template>
    
    <!-- 对话框内容 -->
    <div v-loading="loading" class="dialog-content">
      <!-- 内容区域 -->
      <div class="dialog-body">
        <slot :close="close" :confirm="confirm" />
      </div>
    </div>
    
    <!-- 自定义底部 -->
    <template v-if="$slots.footer || showFooter" #footer>
      <slot name="footer" :close="close" :confirm="confirm">
        <!-- 默认底部按钮 -->
        <div class="dialog-footer">
          <el-button
            v-if="showCancel"
            :size="buttonSize"
            @click="handleCancel"
          >
            {{ cancelText }}
          </el-button>
          
          <el-button
            v-if="showConfirm"
            type="primary"
            :size="buttonSize"
            :loading="confirmLoading"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </el-button>
        </div>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import type { DialogBeforeCloseFn } from 'element-plus'

// 组件属性接口
interface Props {
  modelValue: boolean
  title?: string
  width?: string | number
  fullscreen?: boolean
  top?: string
  modal?: boolean
  modalClass?: string
  appendToBody?: boolean
  lockScroll?: boolean
  customClass?: string
  openDelay?: number
  closeDelay?: number
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  showClose?: boolean
  beforeClose?: DialogBeforeCloseFn
  center?: boolean
  alignCenter?: boolean
  destroyOnClose?: boolean
  loading?: boolean
  showFooter?: boolean
  showCancel?: boolean
  showConfirm?: boolean
  cancelText?: string
  confirmText?: string
  buttonSize?: 'large' | 'default' | 'small'
  confirmLoading?: boolean
  maxHeight?: string
  draggable?: boolean
  resizable?: boolean
}

// 定义属性默认值
const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  width: '50%',
  fullscreen: false,
  top: '15vh',
  modal: true,
  appendToBody: false,
  lockScroll: true,
  openDelay: 0,
  closeDelay: 0,
  closeOnClickModal: true,
  closeOnPressEscape: true,
  showClose: true,
  center: false,
  alignCenter: false,
  destroyOnClose: false,
  loading: false,
  showFooter: true,
  showCancel: true,
  showConfirm: true,
  cancelText: '取消',
  confirmText: '确定',
  buttonSize: 'default',
  confirmLoading: false,
  maxHeight: '70vh',
  draggable: false,
  resizable: false
})

// 定义事件
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  open: []
  opened: []
  close: []
  closed: []
  cancel: []
  confirm: []
  beforeClose: [done: () => void]
}>()

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

// 处理打开前事件
const handleBeforeClose = (done: () => void) => {
  if (props.beforeClose) {
    props.beforeClose(done)
  } else {
    emit('beforeClose', done)
    done()
  }
}

// 处理打开事件
const handleOpen = () => {
  emit('open')
}

// 处理打开完成事件
const handleOpened = () => {
  emit('opened')
}

// 处理关闭事件
const handleClose = () => {
  emit('close')
}

// 处理关闭完成事件
const handleClosed = () => {
  emit('closed')
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
  close()
}

// 处理确认
const handleConfirm = () => {
  emit('confirm')
}

// 关闭对话框
const close = () => {
  visible.value = false
}

// 确认操作（不自动关闭）
const confirm = () => {
  emit('confirm')
}

// 打开对话框
const open = () => {
  visible.value = true
}

// 暴露方法
defineExpose({
  open,
  close,
  confirm
})
</script>

<style lang="scss" scoped>
:deep(.el-dialog) {
  .el-dialog__header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    
    .el-dialog__title {
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      line-height: 1.4;
    }
  }
  
  .el-dialog__body {
    padding: 0;
    
    .dialog-content {
      .dialog-body {
        padding: 24px;
        max-height: v-bind(maxHeight);
        overflow-y: auto;
        
        // 自定义滚动条样式
        &::-webkit-scrollbar {
          width: 6px;
        }
        
        &::-webkit-scrollbar-track {
          background: var(--el-fill-color-lighter);
          border-radius: 3px;
        }
        
        &::-webkit-scrollbar-thumb {
          background: var(--el-fill-color-dark);
          border-radius: 3px;
          
          &:hover {
            background: var(--el-fill-color-darker);
          }
        }
      }
    }
  }
  
  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid var(--el-border-color-lighter);
    
    .dialog-footer {
      text-align: right;
      
      .el-button {
        margin-left: 12px;
        
        &:first-child {
          margin-left: 0;
        }
      }
    }
  }
  
  // 全屏模式样式
  &.is-fullscreen {
    .el-dialog__body {
      .dialog-content {
        .dialog-body {
          max-height: calc(100vh - 120px);
        }
      }
    }
  }
  
  // 居中模式样式
  &.is-align-center {
    .el-dialog__body {
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
    
    .el-dialog__header {
      padding: 16px 20px 12px;
    }
    
    .el-dialog__body {
      .dialog-content {
        .dialog-body {
          padding: 20px;
          max-height: 60vh;
        }
      }
    }
    
    .el-dialog__footer {
      padding: 12px 20px 16px;
      
      .dialog-footer {
        text-align: center;
        
        .el-button {
          margin: 0 6px 8px 6px;
        }
      }
    }
  }
}

// 小尺寸对话框
:deep(.el-dialog.dialog-small) {
  .el-dialog__header {
    padding: 16px 20px 12px;
  }
  
  .el-dialog__body {
    .dialog-content {
      .dialog-body {
        padding: 20px;
      }
    }
  }
  
  .el-dialog__footer {
    padding: 12px 20px 16px;
  }
}

// 大尺寸对话框
:deep(.el-dialog.dialog-large) {
  .el-dialog__header {
    padding: 24px 32px 20px;
  }
  
  .el-dialog__body {
    .dialog-content {
      .dialog-body {
        padding: 32px;
      }
    }
  }
  
  .el-dialog__footer {
    padding: 20px 32px 24px;
  }
}

// 无边框模式
:deep(.el-dialog.dialog-borderless) {
  .el-dialog__header {
    border-bottom: none;
  }
  
  .el-dialog__footer {
    border-top: none;
  }
}

// 简洁模式
:deep(.el-dialog.dialog-simple) {
  .el-dialog__header {
    padding-bottom: 8px;
    border-bottom: none;
  }
  
  .el-dialog__footer {
    padding-top: 8px;
    border-top: none;
  }
}
</style>