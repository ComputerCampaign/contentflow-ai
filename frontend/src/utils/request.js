import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import Cookies from 'js-cookie'
import NProgress from 'nprogress'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    NProgress.start()
    
    // 添加token到请求头
    const token = Cookies.get('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    NProgress.done()
    
    // 后端返回的数据结构适配
    const data = response.data
    
    // 如果后端返回的是标准格式 {success: true, data: {}, message: ''}
    if (data.hasOwnProperty('success')) {
      if (data.success) {
        return {
          ...response,
          data: data.data || data
        }
      } else {
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(new Error(data.message || '请求失败'))
      }
    }
    
    // 直接返回数据
    return response
  },
  async (error) => {
    NProgress.done()
    
    const { response } = error
    const userStore = useUserStore()
    
    if (response) {
      const { status, data } = response
      
      switch (status) {
        case 400:
          ElMessage.error(data.message || '请求参数错误')
          break
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          // 清除token并跳转到登录页
          userStore.logout()
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422:
          // 表单验证错误
          if (data.errors) {
            const errorMessages = Object.values(data.errors).flat()
            ElMessage.error(errorMessages.join(', '))
          } else {
            ElMessage.error(data.message || '数据验证失败')
          }
          break
        case 429:
          ElMessage.error('请求过于频繁，请稍后再试')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.message || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (error.message === 'Network Error') {
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

// 封装常用的请求方法
const http = {
  get: (url, params = {}, config = {}) => {
    return request.get(url, { params, ...config })
  },
  
  post: (url, data = {}, config = {}) => {
    return request.post(url, data, config)
  },
  
  put: (url, data = {}, config = {}) => {
    return request.put(url, data, config)
  },
  
  patch: (url, data = {}, config = {}) => {
    return request.patch(url, data, config)
  },
  
  delete: (url, config = {}) => {
    return request.delete(url, config)
  },
  
  upload: (url, formData, config = {}) => {
    return request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  download: async (url, filename, config = {}) => {
    try {
      const response = await request.get(url, {
        responseType: 'blob',
        ...config
      })
      
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
      
      return response
    } catch (error) {
      ElMessage.error('文件下载失败')
      throw error
    }
  }
}

export default http
export { request }