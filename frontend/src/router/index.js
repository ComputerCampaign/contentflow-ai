import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    redirect: '/dashboard',
    component: () => import('@/layout/AdminLayout.vue'),
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表板',
          icon: 'DataAnalysis'
        }
      },
      {
        path: '/tasks',
        name: 'Tasks',
        component: () => import('@/views/Tasks.vue'),
        meta: {
          title: '任务管理',
          icon: 'List'
        }
      },
      {
        path: '/crawler',
        name: 'Crawler',
        component: () => import('@/views/Crawler.vue'),
        meta: {
          title: '爬虫配置',
          icon: 'Connection'
        }
      },
      {
        path: '/xpath',
        name: 'XPath',
        component: () => import('@/views/XPath.vue'),
        meta: {
          title: 'XPath配置',
          icon: 'Position'
        }
      },



      {
        path: '/monitoring',
        name: 'Monitoring',
        component: () => import('@/views/Monitor.vue'),
        meta: {
          title: '系统监控',
          icon: 'Monitor'
        }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: {
          title: '系统设置',
          icon: 'Setting'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 数据爬取博客发布平台` : '数据爬取博客发布平台'
  
  // 如果访问登录页面且已经登录，直接跳转到仪表板
  if (to.path === '/login' && userStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  // 如果不需要认证，直接通过
  if (!to.meta.requiresAuth) {
    next()
    return
  }
  
  // 需要认证的页面
  if (!userStore.isAuthenticated) {
    // 没有token，跳转到登录页
    next('/login')
    return
  }
  
  // 有token，验证token有效性
  try {
    const isValid = await userStore.checkAuth()
    if (isValid) {
      next()
    } else {
      // token无效，跳转到登录页
      next('/login')
    }
  } catch (error) {
    // 验证失败，跳转到登录页
    console.error('Token验证失败:', error)
    next('/login')
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router