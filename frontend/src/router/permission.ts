import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { routes } from './index'

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
  '/crawler-tasks': ['task:view'],
  '/crawler-tasks/create': ['task:create'],
  '/crawler-tasks/edit': ['task:edit'],
  '/crawler-tasks/detail': ['task:view'],
  '/crawler-tasks/monitor': ['task:view'],
  '/content-tasks': ['task:view'],
  '/content-tasks/create': ['task:create'],
  '/content-tasks/edit': ['task:edit'],
  '/content-tasks/detail': ['task:view'],
  '/content-tasks/monitor': ['task:view'],
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
  '/settings/user-management': ['user:manage'],
  '/profile': ['profile:view']
}

// 检查用户是否有访问权限
function hasPermission(userPermissions: string[], requiredPermissions: string[]): boolean {
  if (!requiredPermissions || requiredPermissions.length === 0) {
    return true
  }
  
  // 超级管理员拥有所有权限
  if (userPermissions.includes('*')) {
    return true
  }
  
  // 特殊处理：admin:* 权限可以访问所有页面
  if (userPermissions.includes('admin:*')) {
    return true
  }
  
  // 检查是否有任一所需权限
  return requiredPermissions.some(permission => {
    // 直接匹配权限
    if (userPermissions.includes(permission)) {
      return true
    }
    
    // 检查通配符权限
    return userPermissions.some(userPerm => {
      if (userPerm.endsWith(':*')) {
        const prefix = userPerm.slice(0, -1) // 移除 '*'
        return permission.startsWith(prefix)
      }
      return false
    })
  })
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
          // 已登录用户访问登录页，需要找到一个有权限的页面进行重定向
          // 检查用户信息是否存在
          if (!userStore.userInfo?.id) {
            try {
              // 获取用户信息
              await userStore.getUserInfo()
              // 初始化路由数据
              appStore.setRoutes(routes)
            } catch (error) {
              console.error('获取用户信息失败:', error)
              // token 可能已过期，清除用户信息并重定向到登录页
              await userStore.logout()
              ElMessage.error('登录状态已过期，请重新登录')
              next({ path: '/login', query: { redirect: to.fullPath } })
              return
            }
          }
          
          // 查找用户有权限访问的第一个页面
          const userPermissions = userStore.permissions
          let redirectPath = '/dashboard' // 默认重定向到dashboard
          
          // 检查用户是否有dashboard权限
          if (!hasPermission(userPermissions, ['dashboard:view'])) {
            // 没有dashboard权限，查找其他有权限的页面
            const availableRoutes = [
              { path: '/profile', permissions: ['profile:view'] },
              { path: '/crawler-tasks', permissions: ['task:view'] },
              { path: '/content-tasks', permissions: ['task:view'] },
              { path: '/crawler', permissions: ['crawler:view'] },
              { path: '/xpath', permissions: ['xpath:view'] },
              { path: '/ai-config', permissions: ['ai:config'] },
              { path: '/monitoring', permissions: ['monitoring:view'] },
              { path: '/settings', permissions: ['settings:view'] }
            ]
            
            for (const route of availableRoutes) {
              if (hasPermission(userPermissions, route.permissions)) {
                redirectPath = route.path
                break
              }
            }
            
            // 如果没有找到任何有权限的页面，重定向到403
            if (redirectPath === '/dashboard' && !hasPermission(userPermissions, ['dashboard:view'])) {
              ElMessage.error('您没有访问任何页面的权限，请联系管理员')
              next({ path: '/403' })
              return
            }
          }
          
          next({ path: redirectPath })
        } else {
          // 检查用户信息是否存在
          if (!userStore.userInfo?.id) {
            try {
              // 获取用户信息
              await userStore.getUserInfo()
              // 初始化路由数据
              appStore.setRoutes(routes)
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