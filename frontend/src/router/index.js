import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Layout = () => import('../views/Layout.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const CrawlerTask = () => import('../views/CrawlerTask.vue')
const XPathRules = () => import('../views/XPathRule.vue')
const UserManagement = () => import('../views/UserManagement.vue')
const Profile = () => import('../views/Profile.vue')

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘' }
      },
      {
        path: 'crawler',
        name: 'CrawlerTask',
        component: CrawlerTask,
        meta: { title: '爬虫任务' }
      },
      {
        path: 'xpath',
        name: 'XPathRules',
        component: XPathRules,
        meta: { title: 'XPath规则' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagement,
        meta: { title: '用户管理', requiresAdmin: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile,
        meta: { title: '个人资料' }
      }
    ]
  },
  // 重定向到登录页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录
    if (!store.getters['auth/isAuthenticated']) {
      // 未登录则重定向到登录页
      next({ name: 'Login' })
    } else {
      // 检查是否需要管理员权限
      if (to.matched.some(record => record.meta.requiresAdmin)) {
        // 检查用户是否为管理员
        if (store.getters['auth/isAdmin']) {
          next()
        } else {
          // 非管理员重定向到仪表盘
          next({ name: 'Dashboard' })
        }
      } else {
        next()
      }
    }
  } else {
    // 不需要认证的路由直接放行
    next()
  }
})

export default router