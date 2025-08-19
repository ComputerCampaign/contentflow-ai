/// <reference types="vite/client" />

// 声明Vue组件类型
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 声明path-browserify模块
declare module 'path-browserify' {
  const path: {
    resolve: (...paths: string[]) => string
    join: (...paths: string[]) => string
    dirname: (path: string) => string
    basename: (path: string, ext?: string) => string
    extname: (path: string) => string
    [key: string]: any
  }
  export default path
}

// 声明SCSS模块
declare module '*.scss' {
  const variables: {
    menuBg: string
    menuText: string
    menuActiveText: string
    menuHover: string
    subMenuBg: string
    subMenuHover: string
    subMenuActiveText: string
    sideBarWidth: string
    [key: string]: string
  }
  export default variables
}

// 声明环境变量
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  // 更多环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}