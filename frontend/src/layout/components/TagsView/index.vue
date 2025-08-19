<template>
  <div id="tags-view-container" class="tags-view-container">
    <scroll-pane ref="scrollPane" class="tags-view-wrapper" @scroll="handleScroll">
      <router-link
        v-for="tag in visitedViews"
        ref="tag"
        :key="tag.path"
        :class="isActive(tag) ? 'active' : ''"
        :to="{ path: tag.path, query: tag.query }"
        tag="span"
        class="tags-view-item"
        @click.middle="!isAffix(tag) ? closeSelectedTag(tag) : ''"
        @contextmenu.prevent="openMenu(tag, $event)"
      >
        {{ tag.title }}
        <span v-if="!isAffix(tag)" class="el-icon-close" @click.prevent.stop="closeSelectedTag(tag)">
          <el-icon :size="12">
            <Close />
          </el-icon>
        </span>
      </router-link>
    </scroll-pane>
    <ul v-show="visible" :style="{ left: left + 'px', top: top + 'px' }" class="contextmenu">
      <li @click="refreshSelectedTag(selectedTag)">刷新</li>
      <li v-if="!isAffix(selectedTag)" @click="closeSelectedTag(selectedTag)">关闭</li>
      <li @click="closeOthersTags">关闭其它</li>
      <li @click="closeAllTags(selectedTag)">关闭所有</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Close } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import ScrollPane from './ScrollPane.vue'
import path from 'path-browserify'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const visible = ref(false)
const top = ref(0)
const left = ref(0)
const selectedTag = ref<any>({})
const affixTags = ref<any[]>([])
const scrollPane = ref()
const tag = ref()

// 计算属性
const visitedViews = computed(() => appStore.state.visitedViews)
const routes = computed(() => appStore.state.routes)

// 判断是否为当前激活的标签
const isActive = (tag: any) => {
  return tag.path === route.path
}

// 判断是否为固定标签
const isAffix = (tag: any) => {
  return tag.meta && tag.meta.affix
}

// 过滤固定标签
const filterAffixTags = (routes: any[], basePath = '/') => {
  let tags: any[] = []
  routes.forEach(route => {
    if (route.meta && route.meta.affix) {
      const tagPath = path.resolve(basePath, route.path)
      tags.push({
        fullPath: tagPath,
        path: tagPath,
        name: route.name,
        meta: { ...route.meta }
      })
    }
    if (route.children) {
      const tempTags = filterAffixTags(route.children, route.path)
      if (tempTags.length >= 1) {
        tags = [...tags, ...tempTags]
      }
    }
  })
  return tags
}

// 初始化固定标签
const initTags = () => {
  const affixTagsValue = affixTags.value = filterAffixTags(routes.value)
  for (const tag of affixTagsValue) {
    // 必须有标签名称
    if (tag.name) {
      appStore.addVisitedView(tag)
    }
  }
}

// 添加标签
const addTags = () => {
  const { name } = route
  if (name) {
    appStore.addView(route)
  }
  return false
}

// 移动到当前标签
const moveToCurrentTag = () => {
  const tags = tag.value
  nextTick(() => {
    for (const tag of tags) {
      if (tag.to.path === route.path) {
        scrollPane.value.moveToTarget(tag)
        // 当查询不同时
        if (tag.to.fullPath !== route.fullPath) {
          appStore.updateVisitedView(route)
        }
        break
      }
    }
  })
}

// 刷新选中的标签
const refreshSelectedTag = (view: any) => {
  appStore.delCachedView(view).then(() => {
    const { fullPath } = view
    nextTick(() => {
      router.replace({
        path: '/redirect' + fullPath
      })
    })
  })
}

// 关闭选中的标签
const closeSelectedTag = (view: any) => {
  appStore.delView(view).then(({ visitedViews }) => {
    if (isActive(view)) {
      toLastView(visitedViews, view)
    }
  })
}

// 关闭其他标签
const closeOthersTags = () => {
  router.push(selectedTag.value)
  appStore.delOthersViews(selectedTag.value).then(() => {
    moveToCurrentTag()
  })
}

// 关闭所有标签
const closeAllTags = (view: any) => {
  appStore.delAllViews().then(({ visitedViews }) => {
    if (affixTags.value.some(tag => tag.path === view.path)) {
      return
    }
    toLastView(visitedViews, view)
  })
}

// 跳转到最后一个视图
const toLastView = (visitedViews: any[], view: any) => {
  const latestView = visitedViews.slice(-1)[0]
  if (latestView) {
    router.push(latestView.fullPath)
  } else {
    // 现在默认是如果没有标签视图，则重定向到主页，
    // 您可以根据需要进行调整。
    if (view.name === 'Dashboard') {
      // 重新加载主页
      router.replace({ path: '/redirect' + view.fullPath })
    } else {
      router.push('/')
    }
  }
}

// 打开菜单
const openMenu = (tag: any, e: MouseEvent) => {
  const menuMinWidth = 105
  const offsetLeft = (e.target as HTMLElement).getBoundingClientRect().left // container margin left
  const offsetWidth = (e.target as HTMLElement).offsetWidth // container width
  const maxLeft = offsetWidth - menuMinWidth // left boundary
  const leftValue = e.clientX - offsetLeft + 15 // 15: margin right

  if (leftValue > maxLeft) {
    left.value = maxLeft
  } else {
    left.value = leftValue
  }

  top.value = e.clientY
  visible.value = true
  selectedTag.value = tag
}

// 关闭菜单
const closeMenu = () => {
  visible.value = false
}

// 处理滚动
const handleScroll = () => {
  closeMenu()
}

// 监听路由变化
watch(
  route,
  () => {
    addTags()
    moveToCurrentTag()
  }
)

// 监听右键菜单显示状态
watch(
  visible,
  (value) => {
    if (value) {
      document.body.addEventListener('click', closeMenu)
    } else {
      document.body.removeEventListener('click', closeMenu)
    }
  }
)

onMounted(() => {
  initTags()
  addTags()
})
</script>

<style lang="scss" scoped>
.tags-view-container {
  height: 34px;
  width: 100%;
  background: #fff;
  border-bottom: 1px solid #d8dce5;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.12), 0 0 3px 0 rgba(0, 0, 0, 0.04);

  .tags-view-wrapper {
    .tags-view-item {
      display: inline-block;
      position: relative;
      cursor: pointer;
      height: 26px;
      line-height: 26px;
      border: 1px solid #d8dce5;
      color: #495057;
      background: #fff;
      padding: 0 8px;
      font-size: 12px;
      margin-left: 5px;
      margin-top: 4px;

      &:first-of-type {
        margin-left: 15px;
      }

      &:last-of-type {
        margin-right: 15px;
      }

      &.active {
        background-color: #42b983;
        color: #fff;
        border-color: #42b983;

        &::before {
          content: '';
          background: #fff;
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          position: relative;
          margin-right: 2px;
        }
      }
    }
  }

  .contextmenu {
    margin: 0;
    background: #fff;
    z-index: 3000;
    position: absolute;
    list-style-type: none;
    padding: 5px 0;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 400;
    color: #333;
    box-shadow: 2px 2px 3px 0 rgba(0, 0, 0, 0.3);

    li {
      margin: 0;
      padding: 7px 16px;
      cursor: pointer;

      &:hover {
        background: #eee;
      }
    }
  }
}
</style>

<style lang="scss">
// reset element css of el-icon-close
.tags-view-wrapper {
  .tags-view-item {
    .el-icon-close {
      width: 16px;
      height: 16px;
      vertical-align: 2px;
      border-radius: 50%;
      text-align: center;
      transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
      transform-origin: 100% 50%;

      &:before {
        transform: scale(0.6);
        display: inline-block;
        vertical-align: -3px;
      }

      &:hover {
        background-color: #b4bccc;
        color: #fff;
      }
    }
  }
}
</style>