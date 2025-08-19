import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置 NProgress
NProgress.configure({ 
  showSpinner: false,
  minimum: 0.2,
  speed: 500
})

// 白名单路由（不需要登录即可访问）
const whiteList = ['/login', '/register', '/forgot-password', '/404', '/403']

// 权限映射表
const permissionMap: Record<string, string[]> = {
  '/dashboard': ['dashboard:view'],
  '/tasks': ['task:view'],
  '/tasks/create': ['task:create'],
  '/tasks/edit': ['task:edit'],
  '/crawler': ['crawler:view'],
  '/crawler/create': ['crawler:create'],
  '/crawler/edit': ['crawler:edit'],
  '/xpath': ['xpath:view'],
  '/xpath/create': ['xpath:create'],
  '/xpath/edit': ['xpath:edit'],
  '/ai-config': ['ai:config'],
  '/monitoring': ['monitoring:view'],
  '/settings': ['settings:view'],
  '/settings/system': ['settings:system'],
  '/settings/user': ['settings:user'],
  '/profile': ['profile:view']
}

// 检查用户是否有访问权限
function hasPermission(userPermissions: string[], requiredPermissions: string[]): boolean {
  if (!requiredPermissions || requiredPermissions.length === 0) {
    return true
  }
  
  // 超级管理员拥有所有权限
  if (userPermissions.includes('*') || userPermissions.includes('admin:*')) {
    return true
  }
  
  // 检查是否有任一所需权限
  return requiredPermissions.some(permission => 
    userPermissions.includes(permission) ||
    userPermissions.some(userPerm => {
      // 支持通配符权限，如 task:* 包含 task:view, task:create 等
      if (userPerm.endsWith(':*')) {
        const prefix = userPerm.slice(0, -1)
        return permission.startsWith(prefix)
      }
      return false
    })
  )
}

// 获取页面标题
function getPageTitle(title?: string): string {
  const defaultTitle = 'ContentFlow AI'
  if (title) {
    return `${title} - ${defaultTitle}`
  }
  return defaultTitle
}

// 设置路由守卫
export function setupRouterGuard(router: Router): void {
  // 全局前置守卫
  router.beforeEach(async (to, from, next) => {
    // 开始进度条
    NProgress.start()
    
    const userStore = useUserStore()
    const appStore = useAppStore()
    
    // 设置页面标题
    document.title = getPageTitle(to.meta?.title as string)
    
    // 设置页面加载状态
    appStore.setLoading('page', true)
    
    try {
      // 检查是否有 token
      const hasToken = userStore.token
      
      if (hasToken) {
        if (to.path === '/login') {
          // 已登录用户访问登录页，重定向到首页
          next({ path: '/dashboard' })
        } else {
          // 检查用户信息是否存在
          if (!userStore.userInfo?.id) {
            try {
              // 获取用户信息
              await userStore.getUserInfo()
            } catch (error) {
              console.error('获取用户信息失败:', error)
              // token 可能已过期，清除用户信息并重定向到登录页
              await userStore.logout()
              ElMessage.error('登录状态已过期，请重新登录')
              next({ path: '/login', query: { redirect: to.fullPath } })
              return
            }
          }
          
          // 检查路由权限
          const requiredPermissions = permissionMap[to.path] || []
          const userPermissions = userStore.permissions
          
          if (hasPermission(userPermissions, requiredPermissions)) {
            // 添加访问记录
            if (to.meta?.title) {
              appStore.addVisitedView({
                path: to.path,
                name: to.name as string,
                title: to.meta.title as string
              })
            }
            
            // 添加页面缓存
            if (to.meta?.keepAlive && to.name) {
              appStore.addCachedView(to.name as string)
            }
            
            next()
          } else {
            // 没有权限，跳转到 403 页面
            ElMessage.error('您没有访问该页面的权限')
            next({ path: '/403' })
          }
        }
      } else {
        // 没有 token
        if (whiteList.includes(to.path)) {
          // 在白名单中，直接访问
          next()
        } else {
          // 不在白名单中，重定向到登录页
          next({ path: '/login', query: { redirect: to.fullPath } })
        }
      }
    } catch (error) {
      console.error('路由守卫错误:', error)
      appStore.addErrorLog({
        message: '路由守卫执行失败',
        stack: error instanceof Error ? error.stack || '' : '',
        url: to.fullPath
      })
      
      // 发生错误时的处理
      if (whiteList.includes(to.path)) {
        next()
      } else {
        next({ path: '/login' })
      }
    }
  })
  
  // 全局后置守卫
  router.afterEach((to, from) => {
    const appStore = useAppStore()
    
    // 结束进度条
    NProgress.done()
    
    // 设置页面加载状态
    appStore.setLoading('page', false)
    
    // 记录路由跳转日志（开发环境）
    if (import.meta.env.DEV) {
      console.log(`路由跳转: ${from.path} -> ${to.path}`)
    }
  })
  
  // 路由错误处理
  router.onError((error) => {
    const appStore = useAppStore()
    
    console.error('路由错误:', error)
    
    // 记录错误日志
    appStore.addErrorLog({
      message: '路由加载失败',
      stack: error.stack || '',
      url: window.location.href
    })
    
    // 结束进度条
    NProgress.done()
    
    // 设置页面加载状态
    appStore.setLoading('page', false)
    
    ElMessage.error('页面加载失败，请刷新重试')
  })
}

// 动态添加路由权限
export function addRoutePermission(path: string, permissions: string[]): void {
  permissionMap[path] = permissions
}

// 检查当前用户是否有指定权限
export function checkPermission(permission: string | string[]): boolean {
  const userStore = useUserStore()
  const userPermissions = userStore.permissions
  
  if (typeof permission === 'string') {
    return hasPermission(userPermissions, [permission])
  } else {
    return hasPermission(userPermissions, permission)
  }
}

// 权限指令
export const permissionDirective = {
  mounted(el: HTMLElement, binding: { value: string | string[] }) {
    const { value } = binding
    if (value && !checkPermission(value)) {
      el.style.display = 'none'
    }
  },
  updated(el: HTMLElement, binding: { value: string | string[] }) {
    const { value } = binding
    if (value && !checkPermission(value)) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}