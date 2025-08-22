import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'



// 应用状态接口
interface AppState {
  // 主题设置
  theme: 'light' | 'dark' | 'auto'
  primaryColor: string
  
  // 语言设置
  language: string
  
  // 侧边栏
  sidebar: {
    opened: boolean
    withoutAnimation: boolean
  }
  
  // 布局模式
  layout: 'vertical' | 'horizontal' | 'mix'
  
  // 设备类型
  device: 'desktop' | 'tablet' | 'mobile'
  
  // 加载状态
  loading: {
    global: boolean
    [key: string]: boolean
  }
  
  // 访问的视图（用于标签页）
  visitedViews: any[]
  
  // 缓存的视图
  cachedViews: string[]
  
  // 错误日志
  errorLogs: any[]
  
  // 网络状态
  online: boolean
  
  // 全屏状态
  fullscreen: boolean
  
  // 页面设置
  tagsView: boolean
  fixedHeader: boolean
  sidebarLogo: boolean
  
  // 路由
  routes: any[]
}



export const useAppStore = defineStore('app', () => {
  // 应用状态
  const state = reactive<AppState>({
    theme: (localStorage.getItem('app-theme') as any) || 'light',
    primaryColor: localStorage.getItem('app-primary-color') || '#409EFF',
    language: localStorage.getItem('app-language') || 'zh-cn',
    sidebar: {
      opened: localStorage.getItem('app-sidebar-opened') !== 'false',
      withoutAnimation: false
    },
    layout: (localStorage.getItem('app-layout') as any) || 'vertical',
    device: 'desktop',
    loading: {
      global: false
    },
    visitedViews: JSON.parse(localStorage.getItem('app-visited-views') || '[]'),
    cachedViews: [],
    errorLogs: [],
    online: navigator.onLine,
    fullscreen: false,
    tagsView: localStorage.getItem('app-tags-view') !== 'false',
    fixedHeader: localStorage.getItem('app-fixed-header') !== 'false',
    sidebarLogo: localStorage.getItem('app-sidebar-logo') !== 'false',
    routes: []
  })
  
  // 计算属性
  const isDark = computed(() => {
    if (state.theme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return state.theme === 'dark'
  })
  
  const isMobile = computed(() => state.device === 'mobile')
  const isTablet = computed(() => state.device === 'tablet')
  const isDesktop = computed(() => state.device === 'desktop')

  // 方法
  const setTheme = (newTheme: 'light' | 'dark' | 'auto'): void => {
    state.theme = newTheme
    localStorage.setItem('app-theme', newTheme)
    
    // 应用主题到DOM
    const html = document.documentElement
    if (isDark.value) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }
  
  const setPrimaryColor = (color: string): void => {
    state.primaryColor = color
    localStorage.setItem('app-primary-color', color)
    
    // 应用主色调到CSS变量
    document.documentElement.style.setProperty('--el-color-primary', color)
  }
  
  const setLanguage = (lang: string): void => {
    state.language = lang
    localStorage.setItem('app-language', lang)
  }
  
  const toggleSidebar = (withoutAnimation = false): void => {
    state.sidebar.opened = !state.sidebar.opened
    state.sidebar.withoutAnimation = withoutAnimation
    localStorage.setItem('app-sidebar-opened', String(state.sidebar.opened))
  }
  
  const closeSidebar = (withoutAnimation = false): void => {
    state.sidebar.opened = false
    state.sidebar.withoutAnimation = withoutAnimation
    localStorage.setItem('app-sidebar-opened', 'false')
  }
  
  const setLayout = (newLayout: 'vertical' | 'horizontal' | 'mix'): void => {
    state.layout = newLayout
    localStorage.setItem('app-layout', newLayout)
  }
  
  const setDevice = (newDevice: 'desktop' | 'tablet' | 'mobile'): void => {
    state.device = newDevice
  }
  
  const setLoading = (key: string, value: boolean): void => {
    state.loading[key] = value
  }
  
  const setGlobalLoading = (value: boolean): void => {
    state.loading.global = value
  }

  // 标签页视图管理
  const addVisitedView = (view: any): void => {
    if (state.visitedViews.some(v => v.path === view.path)) return
    state.visitedViews.push({
      ...view,
      title: view.meta?.title || 'No Title'
    })
    
    // 持久化
    localStorage.setItem('app-visited-views', JSON.stringify(state.visitedViews))
  }
  
  const addCachedView = (view: any): void => {
    if (state.cachedViews.includes(view.name as string)) return
    if (view.meta?.keepAlive) {
      state.cachedViews.push(view.name as string)
    }
  }
  
  const delVisitedView = (view: any): Promise<any[]> => {
    return new Promise(resolve => {
      for (const [i, v] of state.visitedViews.entries()) {
        if (v.path === view.path) {
          state.visitedViews.splice(i, 1)
          break
        }
      }
      localStorage.setItem('app-visited-views', JSON.stringify(state.visitedViews))
      resolve([...state.visitedViews])
    })
  }
  
  const delCachedView = (view: any): Promise<string[]> => {
    return new Promise(resolve => {
      const index = state.cachedViews.indexOf(view.name as string)
      index > -1 && state.cachedViews.splice(index, 1)
      resolve([...state.cachedViews])
    })
  }
  
  const delOthersVisitedViews = (view: any): Promise<any[]> => {
    return new Promise(resolve => {
      state.visitedViews = state.visitedViews.filter(v => {
        return v.meta?.affix || v.path === view.path
      })
      localStorage.setItem('app-visited-views', JSON.stringify(state.visitedViews))
      resolve([...state.visitedViews])
    })
  }
  
  const delOthersCachedViews = (view: any): Promise<string[]> => {
    return new Promise(resolve => {
      const index = state.cachedViews.indexOf(view.name as string)
      if (index > -1) {
        state.cachedViews = state.cachedViews.slice(index, index + 1)
      } else {
        state.cachedViews = []
      }
      resolve([...state.cachedViews])
    })
  }
  
  const delAllVisitedViews = (): Promise<any[]> => {
    return new Promise(resolve => {
      const affixTags = state.visitedViews.filter(tag => tag.meta?.affix)
      state.visitedViews = affixTags
      localStorage.setItem('app-visited-views', JSON.stringify(state.visitedViews))
      resolve([...state.visitedViews])
    })
  }
  
  const delAllCachedViews = (): Promise<string[]> => {
    return new Promise(resolve => {
      state.cachedViews = []
      resolve([...state.cachedViews])
    })
  }
  
  const updateVisitedView = (view: any): void => {
    for (let v of state.visitedViews) {
      if (v.path === view.path) {
        v = Object.assign(v, view)
        break
      }
    }
    localStorage.setItem('app-visited-views', JSON.stringify(state.visitedViews))
  }
  
  const addView = (view: any): void => {
    addVisitedView(view)
    addCachedView(view)
  }
  
  const delView = (view: any): Promise<{ visitedViews: any[]; cachedViews: string[] }> => {
    return new Promise(resolve => {
      delVisitedView(view)
      delCachedView(view)
      resolve({
        visitedViews: [...state.visitedViews],
        cachedViews: [...state.cachedViews]
      })
    })
  }
  
  const delOthersViews = (view: any): Promise<{ visitedViews: any[]; cachedViews: string[] }> => {
    return new Promise(resolve => {
      delOthersVisitedViews(view)
      delOthersCachedViews(view)
      resolve({
        visitedViews: [...state.visitedViews],
        cachedViews: [...state.cachedViews]
      })
    })
  }
  
  const delAllViews = (): Promise<{ visitedViews: any[]; cachedViews: string[] }> => {
    return new Promise(resolve => {
      delAllVisitedViews()
      delAllCachedViews()
      resolve({
        visitedViews: [...state.visitedViews],
        cachedViews: [...state.cachedViews]
      })
    })
  }
  
  // 错误日志管理
  const addErrorLog = (log: any): void => {
    state.errorLogs.push(log)
  }
  
  const clearErrorLogs = (): void => {
    state.errorLogs = []
  }
  
  // 网络状态管理
  const setOnlineStatus = (status: boolean): void => {
    state.online = status
  }
  
  // 全屏管理
  const toggleFullscreen = (): void => {
    if (document.fullscreenElement) {
      document.exitFullscreen()
      state.fullscreen = false
    } else {
      document.documentElement.requestFullscreen()
      state.fullscreen = true
    }
  }
  

  
  // 修改设置
  const changeSetting = ({ key, value }: { key: string; value: any }): void => {
    if (key in state) {
      ;(state as any)[key] = value
      localStorage.setItem(`app-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, String(value))
    }
  }
  
  // 设置路由
  const setRoutes = (routes: any[]): void => {
    state.routes = routes
  }

  // 初始化应用
  const initApp = (): void => {
    // 应用主题
    setTheme(state.theme)
    setPrimaryColor(state.primaryColor)
    
    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', () => {
      if (state.theme === 'auto') {
        setTheme('auto')
      }
    })
    
    // 监听网络状态
    window.addEventListener('online', () => setOnlineStatus(true))
    window.addEventListener('offline', () => setOnlineStatus(false))
    
    // 监听全屏状态
    document.addEventListener('fullscreenchange', () => {
      state.fullscreen = !!document.fullscreenElement
    })
    
    // 监听窗口大小变化
    const handleResize = () => {
      const width = window.innerWidth
      const prevDevice = state.device
      
      if (width < 768) {
        setDevice('mobile')
        // 移动端自动关闭侧边栏
        if (prevDevice !== 'mobile') {
          closeSidebar(true)
        }
      } else if (width < 1024) {
        setDevice('tablet')
        // 从移动端切换到平板时，恢复侧边栏状态
        if (prevDevice === 'mobile') {
          const savedState = localStorage.getItem('app-sidebar-opened')
          if (savedState !== 'false') {
            state.sidebar.opened = true
            state.sidebar.withoutAnimation = true
          }
        }
      } else {
        setDevice('desktop')
        // 从移动端切换到桌面时，恢复侧边栏状态
        if (prevDevice === 'mobile') {
          const savedState = localStorage.getItem('app-sidebar-opened')
          if (savedState !== 'false') {
            state.sidebar.opened = true
            state.sidebar.withoutAnimation = true
          }
        }
      }
    }
    
    window.addEventListener('resize', handleResize)
    handleResize()
  }
  
  // 重置应用状态
  const resetAppState = (): void => {
    // 清除本地存储
    const keys = [
      'app-theme',
      'app-primary-color',
      'app-language',
      'app-sidebar-opened',
      'app-layout',
      'app-visited-views',
      'app-tags-view',
      'app-fixed-header',
      'app-sidebar-logo'
    ]
    keys.forEach(key => localStorage.removeItem(key))
    
    // 重置状态
    Object.assign(state, {
      theme: 'light',
      primaryColor: '#409EFF',
      language: 'zh-cn',
      sidebar: {
        opened: true,
        withoutAnimation: false
      },
      layout: 'vertical',
      device: 'desktop',
      loading: { global: false },
      visitedViews: [],
      cachedViews: [],
      errorLogs: [],
      online: navigator.onLine,
      fullscreen: false,
      tagsView: true,
      fixedHeader: true,
      sidebarLogo: true,
      routes: []
    })
  }

  return {
    // 状态
    state,
    
    // 计算属性
    isDark,
    isMobile,
    isTablet,
    isDesktop,
    
    // 方法
    setTheme,
    setPrimaryColor,
    setLanguage,
    toggleSidebar,
    closeSidebar,
    setLayout,
    setDevice,
    setLoading,
    setGlobalLoading,
    addVisitedView,
    addCachedView,
    delVisitedView,
    delCachedView,
    delOthersVisitedViews,
    delOthersCachedViews,
    delAllVisitedViews,
    delAllCachedViews,
    updateVisitedView,
    addView,
    delView,
    delOthersViews,
    delAllViews,
    addErrorLog,
    clearErrorLogs,
    setOnlineStatus,
    toggleFullscreen,
    changeSetting,
    setRoutes,
    initApp,
    resetAppState
  }
})