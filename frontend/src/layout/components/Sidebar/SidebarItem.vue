<template>
  <div v-if="!item.hidden">
    <template
      v-if="hasOneShowingChild(item.children, item) && (!onlyOneChild.children || onlyOneChild.noShowingChildren) && !item.meta?.alwaysShow"
    >
      <app-link v-if="onlyOneChild.meta" :to="resolvePath(onlyOneChild.path)">
        <el-menu-item :index="resolvePath(onlyOneChild.path)" :class="{ 'submenu-title-noDropdown': !isNest }">
          <icon-map v-if="onlyOneChild.meta.icon" :name="onlyOneChild.meta.icon" :size="18" />
          <template #title>
            <span>{{ onlyOneChild.meta.title }}</span>
          </template>
        </el-menu-item>
      </app-link>
    </template>

    <el-sub-menu v-else ref="subMenu" :index="resolvePath(item.path)" popper-append-to-body>
      <template #title>
        <icon-map v-if="item.meta && item.meta.icon" :name="item.meta.icon" :size="18" />
        <span>{{ item.meta && item.meta.title }}</span>
      </template>
      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :is-nest="true"
        :item="child"
        :base-path="resolvePath(child.path)"
        class="nest-menu"
      />
    </el-sub-menu>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import path from 'path-browserify'
import { isExternal } from '@/utils/validate'
import AppLink from './Link.vue'
import IconMap from '@/components/common/IconMap.vue'

interface Props {
  item: any
  isNest?: boolean
  basePath?: string
}

const props = withDefaults(defineProps<Props>(), {
  isNest: false,
  basePath: ''
})

const onlyOneChild = ref<any>({})

// 判断是否只有一个显示的子菜单
const hasOneShowingChild = (children: any[] = [], parent: any) => {
  const showingChildren = children.filter((item: any) => {
    if (item.hidden) {
      return false
    } else {
      // 临时设置（如果只有一个显示的子项，则将使用）
      onlyOneChild.value = item
      return true
    }
  })

  // 当只有一个子路由器时，默认显示子路由器
  if (showingChildren.length === 1) {
    return true
  }

  // 如果没有子路由器要显示，则显示父路由器
  if (showingChildren.length === 0) {
    onlyOneChild.value = { ...parent, path: '', noShowingChildren: true }
    return true
  }

  return false
}

// 解析路径
const resolvePath = (routePath: string) => {
  if (isExternal(routePath)) {
    return routePath
  }
  if (isExternal(props.basePath)) {
    return props.basePath
  }
  return path.resolve(props.basePath, routePath)
}
</script>

<style lang="scss" scoped>
.nest-menu .el-submenu > .el-submenu__title,
.el-submenu .el-menu-item {
  min-height: 48px !important;
}

// 图标和文字的间距优化
:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  padding-left: 20px !important; // 统一一级菜单的padding-left
  
  .el-icon {
    margin-right: 8px;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

:deep(.el-submenu__title) {
  display: flex;
  align-items: center;
  padding-left: 20px !important; // 统一一级菜单的padding-left
  
  .el-icon {
    margin-right: 8px;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// 嵌套菜单的padding-left调整
.nest-menu {
  .el-menu-item,
  .el-submenu__title {
    padding-left: 40px !important; // 增加子菜单的padding-left
  }
}
</style>