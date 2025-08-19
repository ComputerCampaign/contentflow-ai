<template>
  <div class="form-container">
    <!-- 表单标题 -->
    <div v-if="title || $slots.title" class="form-header">
      <slot name="title">
        <h3 class="form-title">{{ title }}</h3>
      </slot>
      <div v-if="description" class="form-description">
        {{ description }}
      </div>
    </div>
    
    <!-- 表单主体 -->
    <el-form
      ref="formRef"
      :model="modelValue"
      :rules="rules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      :size="size"
      :disabled="disabled"
      :validate-on-rule-change="validateOnRuleChange"
      :hide-required-asterisk="hideRequiredAsterisk"
      :show-message="showMessage"
      :inline-message="inlineMessage"
      :status-icon="statusIcon"
      :scroll-to-error="scrollToError"
      @validate="handleValidate"
    >
      <!-- 表单内容插槽 -->
      <slot :form="modelValue" :validate="validate" :resetFields="resetFields" />
      
      <!-- 表单操作按钮 -->
      <div v-if="showActions" class="form-actions">
        <slot name="actions" :form="modelValue" :validate="validate" :resetFields="resetFields">
          <!-- 默认操作按钮 -->
          <el-button
            v-if="showReset"
            :size="size"
            @click="handleReset"
          >
            {{ resetText }}
          </el-button>
          
          <el-button
            v-if="showCancel"
            :size="size"
            @click="handleCancel"
          >
            {{ cancelText }}
          </el-button>
          
          <el-button
            type="primary"
            :size="size"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            {{ submitText }}
          </el-button>
        </slot>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { ElForm, FormRules, FormValidateCallback } from 'element-plus'
import { ElMessage } from 'element-plus'

// 组件属性接口
interface Props {
  modelValue: Record<string, any>
  rules?: FormRules
  title?: string
  description?: string
  labelWidth?: string | number
  labelPosition?: 'left' | 'right' | 'top'
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
  validateOnRuleChange?: boolean
  hideRequiredAsterisk?: boolean
  showMessage?: boolean
  inlineMessage?: boolean
  statusIcon?: boolean
  scrollToError?: boolean
  showActions?: boolean
  showReset?: boolean
  showCancel?: boolean
  resetText?: string
  cancelText?: string
  submitText?: string
  submitLoading?: boolean
  autoValidate?: boolean
  successMessage?: string
  errorMessage?: string
}

// 定义属性默认值
const props = withDefaults(defineProps<Props>(), {
  labelWidth: '120px',
  labelPosition: 'right',
  size: 'default',
  disabled: false,
  validateOnRuleChange: true,
  hideRequiredAsterisk: false,
  showMessage: true,
  inlineMessage: false,
  statusIcon: false,
  scrollToError: false,
  showActions: true,
  showReset: true,
  showCancel: false,
  resetText: '重置',
  cancelText: '取消',
  submitText: '提交',
  submitLoading: false,
  autoValidate: true,
  successMessage: '操作成功',
  errorMessage: '请检查表单数据'
})

// 定义事件
const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  validate: [prop: string, isValid: boolean, message: string]
  submit: [form: Record<string, any>]
  reset: []
  cancel: []
  success: [form: Record<string, any>]
  error: [errors: any]
}>()

// 响应式数据
const formRef = ref<InstanceType<typeof ElForm>>()

// 表单验证
const validate = (callback?: FormValidateCallback): Promise<boolean> => {
  return new Promise((resolve) => {
    if (!formRef.value) {
      resolve(false)
      return
    }
    
    formRef.value.validate((valid, fields) => {
      if (callback) {
        callback(valid, fields)
      }
      
      if (!valid && fields) {
        emit('error', fields)
        if (props.errorMessage) {
          ElMessage.error(props.errorMessage)
        }
      }
      
      resolve(valid)
    })
  })
}

// 验证指定字段
const validateField = (props: string | string[], callback?: FormValidateCallback): Promise<boolean> => {
  return new Promise((resolve) => {
    if (!formRef.value) {
      resolve(false)
      return
    }
    
    formRef.value.validateField(props, (errorMessage) => {
      const valid = !errorMessage
      
      if (callback) {
        const messageStr = typeof errorMessage === 'string' ? errorMessage : (errorMessage ? '验证失败' : '')
        callback(valid, errorMessage ? { [Array.isArray(props) ? props[0] : props]: [{ message: messageStr, field: Array.isArray(props) ? props[0] : props }] } : {})
      }
      
      resolve(valid)
    })
  })
}

// 重置表单
const resetFields = () => {
  formRef.value?.resetFields()
  emit('reset')
}

// 清空验证信息
const clearValidate = (props?: string | string[]) => {
  formRef.value?.clearValidate(props)
}

// 滚动到指定字段
const scrollToField = (prop: string) => {
  formRef.value?.scrollToField(prop)
}

// 处理验证事件
const handleValidate = (prop: string, isValid: boolean, message: string) => {
  emit('validate', prop, isValid, message)
}

// 处理提交
const handleSubmit = async () => {
  if (props.autoValidate) {
    const valid = await validate()
    if (!valid) {
      return
    }
  }
  
  emit('submit', props.modelValue)
  
  // 如果没有监听submit事件，显示成功消息
  await nextTick()
  if (props.successMessage) {
    ElMessage.success(props.successMessage)
  }
  emit('success', props.modelValue)
}

// 处理重置
const handleReset = () => {
  resetFields()
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}

// 暴露方法
defineExpose({
  validate,
  validateField,
  resetFields,
  clearValidate,
  scrollToField,
  formRef
})
</script>

<style lang="scss" scoped>
.form-container {
  .form-header {
    margin-bottom: 24px;
    
    .form-title {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      line-height: 1.4;
    }
    
    .form-description {
      color: var(--el-text-color-regular);
      font-size: 14px;
      line-height: 1.5;
    }
  }
  
  :deep(.el-form) {
    .el-form-item {
      margin-bottom: 22px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .el-form-item__label {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    
    .el-form-item__content {
      .el-input,
      .el-select,
      .el-textarea,
      .el-date-picker,
      .el-time-picker,
      .el-cascader,
      .el-color-picker {
        width: 100%;
      }
    }
    
    // 内联表单项样式
    &.el-form--inline {
      .el-form-item {
        margin-right: 16px;
        margin-bottom: 16px;
        
        .el-form-item__content {
          .el-input,
          .el-select {
            width: auto;
            min-width: 160px;
          }
        }
      }
    }
  }
  
  .form-actions {
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid var(--el-border-color-lighter);
    text-align: right;
    
    .el-button {
      margin-left: 12px;
      
      &:first-child {
        margin-left: 0;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .form-container {
    :deep(.el-form) {
      .el-form-item__label {
        text-align: left !important;
      }
    }
    
    .form-actions {
      text-align: center;
      
      .el-button {
        margin: 0 6px 8px 6px;
      }
    }
  }
}

// 紧凑模式
.form-container.compact {
  :deep(.el-form) {
    .el-form-item {
      margin-bottom: 16px;
    }
  }
  
  .form-actions {
    margin-top: 24px;
    padding-top: 16px;
  }
}

// 卡片模式
.form-container.card {
  padding: 24px;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
}
</style>