import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { setupRouterGuard } from './permission'

// 布局组件
const Layout = () => import('@/layout/index.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/login.vue'),
    meta: {
      title: '登录',
      hidden: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/register.vue'),
    meta: {
      title: '注册',
      hidden: true
    }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/forgot-password.vue'),
    meta: {
      title: '忘记密码',
      hidden: true
    }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    component: Layout,
    meta: {
      title: '仪表板',
      icon: 'dashboard',
      alwaysShow: true
    },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '仪表板',
          icon: 'dashboard',
          affix: true
        }
      }
    ]
  },
  {
    path: '/crawler-tasks',
    component: Layout,
    redirect: '/crawler-tasks/list',
    meta: {
      title: '爬虫任务',
      icon: 'crawler-task'
    },
    children: [
      {
        path: 'list',
        name: 'CrawlerTaskList',
        component: () => import('@/views/crawler-task/List.vue'),
        meta: {
          title: '爬虫任务列表',
          icon: 'list'
        }
      },
      {
        path: 'create',
        name: 'CrawlerTaskCreate',
        component: () => import('@/views/crawler-task/Create.vue'),
        meta: {
          title: '创建爬虫任务',
          icon: 'plus',
          hidden: true
        }
      },
      {
        path: 'edit/:id',
        name: 'CrawlerTaskEdit',
        component: () => import('@/views/crawler-task/Edit.vue'),
        meta: {
          title: '编辑爬虫任务',
          icon: 'edit',
          hidden: true,
          activeMenu: '/crawler-tasks/list'
        }
      },

      {
        path: 'monitor',
        name: 'CrawlerTaskMonitor',
        component: () => import('@/views/crawler-task/Monitor.vue'),
        meta: {
          title: '爬虫任务监控',
          icon: 'monitor'
        }
      }
    ]
  },
  {
    path: '/content-tasks',
    component: Layout,
    redirect: '/content-tasks/list',
    meta: {
      title: '文本生成任务',
      icon: 'content-task'
    },
    children: [
      {
        path: 'list',
        name: 'ContentTaskList',
        component: () => import('@/views/content-task/List.vue'),
        meta: {
          title: '文本生成任务列表',
          icon: 'list'
        }
      },
      {
        path: 'create',
        name: 'ContentTaskCreate',
        component: () => import('@/views/content-task/Create.vue'),
        meta: {
          title: '创建文本生成任务',
          icon: 'plus',
          hidden: true
        }
      },
      {
        path: 'edit/:id',
        name: 'ContentTaskEdit',
        component: () => import('@/views/content-task/Edit.vue'),
        meta: {
          title: '编辑文本生成任务',
          icon: 'edit',
          hidden: true,
          activeMenu: '/content-tasks/list'
        }
      },
      {
        path: 'detail/:id',
        name: 'ContentTaskDetail',
        component: () => import('@/views/content-task/Detail.vue'),
        meta: {
          title: '文本生成任务详情',
          icon: 'detail',
          hidden: true,
          activeMenu: '/content-tasks/list'
        }
      },
      {
        path: 'monitor',
        name: 'ContentTaskMonitor',
        component: () => import('@/views/content-task/Monitor.vue'),
        meta: {
          title: '文本生成任务监控',
          icon: 'monitor'
        }
      }
    ]
  },
  {
    path: '/crawler',
    component: Layout,
    redirect: '/crawler/list',
    meta: {
      title: '爬虫配置',
      icon: 'crawler'
    },
    children: [
      {
        path: 'list',
        name: 'CrawlerList',
        component: () => import('@/views/crawler/List.vue'),
        meta: {
          title: '配置列表',
          icon: 'list'
        }
      },

      {
        path: 'detail/:id',
        name: 'CrawlerDetail',
        component: () => import('@/views/crawler/Detail.vue'),
        meta: {
          title: '配置详情',
          icon: 'detail',
          hidden: true,
          activeMenu: '/crawler/list'
        }
      },
      {
        path: 'test',
        name: 'CrawlerTest',
        component: () => import('@/views/crawler/Test.vue'),
        meta: {
          title: '配置测试',
          icon: 'test'
        }
      },
      {
        path: 'import',
        name: 'CrawlerImport',
        component: () => import('@/views/crawler/Import.vue'),
        meta: {
          title: '导入导出',
          icon: 'import'
        }
      }
    ]
  },
  {
    path: '/xpath',
    component: Layout,
    redirect: '/xpath/list',
    meta: {
      title: 'XPath配置',
      icon: 'xpath'
    },
    children: [
      {
        path: 'list',
        name: 'XPathList',
        component: () => import('@/views/xpath/List.vue'),
        meta: {
          title: 'XPath列表',
          icon: 'list'
        }
      },
      {
        path: 'create',
        name: 'XPathCreate',
        component: () => import('@/views/xpath/Create.vue'),
        meta: {
          title: '创建XPath',
          icon: 'plus',
          hidden: true
        }
      },
      {
        path: 'edit/:id',
        name: 'XPathEdit',
        component: () => import('@/views/xpath/Edit.vue'),
        meta: {
          title: '编辑XPath',
          icon: 'edit',
          hidden: true,
          activeMenu: '/xpath/list'
        }
      },
      {
        path: 'detail/:id',
        name: 'XPathDetail',
        component: () => import('@/views/xpath/Detail.vue'),
        meta: {
          title: 'XPath详情',
          icon: 'detail',
          hidden: true,
          activeMenu: '/xpath/list'
        }
      },
      {
        path: 'test',
        name: 'XPathTest',
        component: () => import('@/views/xpath/Test.vue'),
        meta: {
          title: 'XPath测试',
          icon: 'test'
        }
      }
    ]
  },
  {
    path: '/ai',
    component: Layout,
    redirect: '/ai/list',
    meta: {
      title: 'AI配置',
      icon: 'ai'
    },
    children: [
      {
        path: 'list',
        name: 'AIList',
        component: () => import('@/views/ai/List.vue'),
        meta: {
          title: 'AI模型列表',
          icon: 'list'
        }
      },
      {
        path: 'create',
        name: 'AICreate',
        component: () => import('@/views/ai/Create.vue'),
        meta: {
          title: '创建AI模型',
          icon: 'plus',
          hidden: true
        }
      },
      {
        path: 'edit/:id',
        name: 'AIEdit',
        component: () => import('@/views/ai/Edit.vue'),
        meta: {
          title: '编辑AI模型',
          icon: 'edit',
          hidden: true,
          activeMenu: '/ai/list'
        }
      },
      {
        path: 'detail/:id',
        name: 'AIDetail',
        component: () => import('@/views/ai/Detail.vue'),
        meta: {
          title: 'AI模型详情',
          icon: 'detail',
          hidden: true,
          activeMenu: '/ai/list'
        }
      },
      {
        path: 'test/:id',
        name: 'AITest',
        component: () => import('@/views/ai/Test.vue'),
        meta: {
          title: 'AI模型测试',
          icon: 'test',
          hidden: true,
          activeMenu: '/ai/list'
        }
      },
      {
        path: '',
        name: 'AIConfig',
        component: () => import('@/views/ai/index.vue'),
        meta: {
          title: '提示词管理',
          icon: 'config'
        }
      },
      {
        path: 'prompt/create',
        name: 'PromptCreate',
        component: () => import('@/views/ai/prompt/Create.vue'),
        meta: {
          title: '新建提示词',
          icon: 'plus',
          hidden: true,
          activeMenu: '/ai'
        }
      },
      {
        path: 'prompt/edit/:key',
        name: 'PromptEdit',
        component: () => import('@/views/ai/prompt/Edit.vue'),
        meta: {
          title: '编辑提示词',
          icon: 'edit',
          hidden: true,
          activeMenu: '/ai'
        }
      },
      {
        path: 'prompt/:key',
        name: 'PromptDetail',
        component: () => import('@/views/ai/prompt/Detail.vue'),
        meta: {
          title: '提示词详情',
          icon: 'detail',
          hidden: true,
          activeMenu: '/ai'
        }
      }
    ]
  },
  {
    path: '/monitoring',
    component: Layout,
    redirect: '/monitoring/overview',
    meta: {
      title: '系统监控',
      icon: 'monitoring'
    },
    children: [
      {
        path: 'overview',
        name: 'MonitoringOverview',
        component: () => import('@/views/monitoring/Overview.vue'),
        meta: {
          title: '监控概览',
          icon: 'overview'
        }
      },
      {
        path: 'logs',
        name: 'MonitoringLogs',
        component: () => import('@/views/monitoring/Logs.vue'),
        meta: {
          title: '系统日志',
          icon: 'logs'
        }
      },
      {
        path: 'performance',
        name: 'MonitoringPerformance',
        component: () => import('@/views/monitoring/Performance.vue'),
        meta: {
          title: '性能监控',
          icon: 'performance'
        }
      }
    ]
  },
  {
    path: '/settings',
    component: Layout,
    redirect: '/settings/system',
    meta: {
      title: '系统设置',
      icon: 'settings',
      permissions: ['admin']
    },
    children: [
      {
        path: 'system',
        name: 'SystemSettings',
        component: () => import('@/views/settings/System.vue'),
        meta: {
          title: '系统设置',
          icon: 'system'
        }
      },
      {
        path: 'user',
        name: 'UserSettings',
        component: () => import('@/views/settings/User.vue'),
        meta: {
          title: '用户设置',
          icon: 'user'
        }
      },
      {
        path: 'user-management',
        name: 'UserManagement',
        component: () => import('@/views/settings/UserManagement.vue'),
        meta: {
          title: '用户管理',
          icon: 'users',
          permissions: ['user:manage']
        }
      }
    ]
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Layout,
    children: [
      {
        path: '',
        name: 'ProfileIndex',
        component: () => import('@/views/profile/index.vue'),
        meta: {
          title: '个人资料',
          icon: 'profile',
          hidden: true
        }
      }
    ]
  },
  // 错误页面
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '403 - 无权限',
      hidden: true
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '404 - 页面不存在',
      hidden: true
    }
  },
  {
    path: '/500',
    name: 'ServerError',
    component: () => import('@/views/error/500.vue'),
    meta: {
      title: '500 - 服务器错误',
      hidden: true
    }
  },
  // 捕获所有未匹配的路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 设置路由守卫
setupRouterGuard(router)

export { routes }
export default router
