<template>
  <div class="page-container" :class="containerClass">
    <!-- 页面头部 -->
    <div v-if="showHeader" class="page-header">
      <div class="page-header-content">
        <!-- 面包屑导航 -->
        <el-breadcrumb v-if="breadcrumbs.length > 0" class="page-breadcrumb" separator="/">
          <el-breadcrumb-item
            v-for="(item, index) in breadcrumbs"
            :key="index"
            :to="item.path"
          >
            <el-icon v-if="item.icon" class="breadcrumb-icon">
              <component :is="item.icon" />
            </el-icon>
            {{ item.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 页面标题和描述 -->
        <div class="page-title-section">
          <div class="page-title-wrapper">
            <el-icon v-if="icon" class="page-icon">
              <component :is="icon" />
            </el-icon>
            <h1 class="page-title">{{ title }}</h1>
            <el-tag v-if="badge" :type="badgeType" class="page-badge">
              {{ badge }}
            </el-tag>
          </div>
          <p v-if="description" class="page-description">
            {{ description }}
          </p>
        </div>

        <!-- 页面操作按钮 -->
        <div v-if="$slots.actions" class="page-actions">
          <slot name="actions" />
        </div>
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="page-content" :class="contentClass">
      <!-- 加载状态 -->
      <div v-if="loading" class="page-loading">
        <el-skeleton :rows="skeletonRows" animated />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="page-error">
        <el-empty
          :image-size="120"
          :description="errorMessage || '加载失败'"
        >
          <el-button type="primary" @click="$emit('retry')">
            重试
          </el-button>
        </el-empty>
      </div>

      <!-- 空状态 -->
      <div v-else-if="empty" class="page-empty">
        <el-empty
          :image-size="120"
          :description="emptyMessage || '暂无数据'"
        >
          <slot name="empty-actions" />
        </el-empty>
      </div>

      <!-- 正常内容 -->
      <div v-else class="page-main">
        <slot />
      </div>
    </div>

    <!-- 页面底部 -->
    <div v-if="$slots.footer" class="page-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 面包屑项接口
interface BreadcrumbItem {
  title: string
  path?: string
  icon?: string
}

// 组件属性
interface Props {
  title: string
  description?: string
  icon?: string
  badge?: string
  badgeType?: 'success' | 'info' | 'warning' | 'danger'
  breadcrumbs?: BreadcrumbItem[]
  showHeader?: boolean
  loading?: boolean
  error?: boolean
  errorMessage?: string
  empty?: boolean
  emptyMessage?: string
  skeletonRows?: number
  fluid?: boolean
  noPadding?: boolean
  backgroundColor?: string
}

// 定义属性默认值
const props = withDefaults(defineProps<Props>(), {
  breadcrumbs: () => [],
  showHeader: true,
  loading: false,
  error: false,
  empty: false,
  skeletonRows: 5,
  fluid: false,
  noPadding: false,
  badgeType: 'info'
})

// 定义事件
defineEmits<{
  retry: []
}>()

// 计算容器样式类
const containerClass = computed(() => {
  return {
    'page-container--fluid': props.fluid,
    'page-container--no-padding': props.noPadding,
    'page-container--loading': props.loading,
    'page-container--error': props.error,
    'page-container--empty': props.empty
  }
})

// 计算内容样式类
const contentClass = computed(() => {
  return {
    'page-content--no-header': !props.showHeader
  }
})
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100%;
  background-color: var(--el-bg-color-page);
  
  &--fluid {
    .page-header-content,
    .page-content,
    .page-footer {
      max-width: none;
      padding-left: 0;
      padding-right: 0;
    }
  }
  
  &--no-padding {
    .page-content {
      padding: 0;
    }
  }
}

.page-header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 16px 0;
  
  .page-header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
}

.page-breadcrumb {
  .breadcrumb-icon {
    margin-right: 4px;
    font-size: 14px;
  }
}

.page-title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .page-icon {
    font-size: 24px;
    color: var(--el-color-primary);
  }
  
  .page-title {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.2;
  }
  
  .page-badge {
    font-size: 12px;
  }
}

.page-description {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.5;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.page-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  
  &--no-header {
    padding-top: 24px;
  }
}

.page-loading,
.page-error,
.page-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.page-main {
  min-height: 100%;
}

.page-footer {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  border-top: 1px solid var(--el-border-color-light);
  background-color: var(--el-bg-color);
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    .page-header-content {
      padding: 0 16px;
    }
    
    .page-title-wrapper {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
      
      .page-title {
        font-size: 20px;
      }
    }
    
    .page-actions {
      margin-left: 0;
      width: 100%;
      justify-content: flex-start;
    }
  }
  
  .page-content {
    padding: 16px;
  }
  
  .page-footer {
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .page-breadcrumb {
    :deep(.el-breadcrumb__item) {
      .el-breadcrumb__inner {
        font-size: 12px;
      }
    }
  }
  
  .page-title {
    font-size: 18px !important;
  }
  
  .page-description {
    font-size: 13px;
  }
}
</style>