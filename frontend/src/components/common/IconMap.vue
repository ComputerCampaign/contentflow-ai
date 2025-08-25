<template>
  <el-icon v-if="iconComponent" :size="size" :color="color">
    <component :is="iconComponent" />
  </el-icon>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  // 仪表板和概览
  Odometer,
  Monitor,
  TrendCharts,
  
  // 任务管理
  List,
  Plus,
  Edit,
  View,
  Delete,
  Refresh,
  Search,
  
  // 爬虫相关
  Connection,
  DataLine,
  Download,
  Upload,
  
  // AI相关
  ChatDotRound,
  MagicStick,
  Setting,
  
  // XPath相关
  DocumentCopy,
  Position,
  
  // 系统相关
  Tools,
  User,
  Lock,
  Key,
  
  // 监控相关
  VideoPlay,
  VideoPause,
  Warning,
  SuccessFilled,
  
  // 文件操作
  Document,
  Folder,
  FolderOpened,
  
  // 导航
  ArrowLeft,
  ArrowRight,
  More,
  
  // 状态
  CircleCheck,
  CircleClose,
  InfoFilled
} from '@element-plus/icons-vue'

interface Props {
  name: string
  size?: number | string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 16
})

// 图标映射表
const iconMap: Record<string, any> = {
  // 仪表板
  'dashboard': Odometer,
  'overview': Monitor,
  'performance': TrendCharts,
  
  // 基础操作
  'list': List,
  'plus': Plus,
  'edit': Edit,
  'view': View,
  'delete': Delete,
  'refresh': Refresh,
  'search': Search,
  
  // 爬虫任务
  'crawler-task': Connection,
  'crawler': DataLine,
  'import': Upload,
  'export': Download,
  'test': VideoPlay,
  'monitor': Monitor,
  
  // 内容任务
  'content-task': Document,
  
  // AI配置
  'ai': ChatDotRound,
  'config': Setting,
  'prompt': MagicStick,
  
  // XPath配置
  'xpath': Position,
  'detail': View,
  
  // 系统设置
  'settings': Tools,
  'system': Setting,
  'user': User,
  'users': User,
  'profile': User,
  
  // 监控
  'monitoring': Monitor,
  'logs': DocumentCopy,
  
  // 状态
  'success': CircleCheck,
  'error': CircleClose,
  'warning': Warning,
  'info': InfoFilled,
  
  // 文件
  'folder': Folder,
  'folder-open': FolderOpened,
  'document': Document,
  
  // 导航
  'arrow-left': ArrowLeft,
  'arrow-right': ArrowRight,
  'more': More
}

// 计算图标组件
const iconComponent = computed(() => {
  return iconMap[props.name] || null
})
</script>

<style scoped>
.el-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>