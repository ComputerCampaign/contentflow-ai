# 智能爬虫内容管理系统 - 前端

基于 Vue 3 + Element Plus 构建的现代化前端应用，提供美观的用户界面和丰富的功能。

## 🚀 功能特性

### 核心功能
- 🔐 **用户认证** - 美观的登录页面，支持记住密码
- 📊 **仪表板** - 数据可视化展示，实时监控系统状态
- 🕷️ **爬虫管理** - 配置和管理爬虫任务
- 📈 **系统监控** - 实时性能监控和日志查看
- ⚙️ **系统设置** - 全面的系统配置选项

### 技术特性
- 🎨 **现代化UI** - 基于 Element Plus 的美观界面
- 📱 **响应式设计** - 完美适配各种设备
- 🌙 **主题切换** - 支持明暗主题切换
- 🔄 **状态管理** - 使用 Pinia 进行状态管理
- 🛡️ **类型安全** - TypeScript 支持
- 📦 **模块化** - 组件化开发，易于维护

## 🛠️ 技术栈

- **框架**: Vue 3 (Composition API)
- **UI库**: Element Plus
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **图表库**: Chart.js
- **样式**: SCSS
- **构建工具**: Vite
- **图标**: Font Awesome

## 📦 安装和运行

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖
```bash
cd frontend
npm install
```

### 开发模式
```bash
npm run dev
```
访问 http://localhost:3000

### 生产构建
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # 公共组件
│   ├── layout/            # 布局组件
│   │   └── AdminLayout.vue # 后台管理布局
│   ├── router/            # 路由配置
│   │   └── index.js       # 路由定义
│   ├── stores/            # Pinia状态管理
│   │   └── user.js        # 用户状态
│   ├── styles/            # 样式文件
│   │   ├── index.scss     # 全局样式
│   │   └── variables.scss # SCSS变量
│   ├── utils/             # 工具函数
│   │   └── api.js         # API请求封装
│   ├── views/             # 页面组件
│   │   ├── Login.vue      # 登录页面
│   │   ├── Dashboard.vue  # 仪表板
│   │   ├── Tasks.vue      # 任务管理
│   │   ├── Crawler.vue    # 爬虫配置
│   │   ├── XPath.vue      # XPath配置
│   │   ├── Monitor.vue    # 系统监控
│   │   └── Settings.vue   # 系统设置
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML模板
├── package.json           # 依赖配置
├── vite.config.js         # Vite配置
└── README.md              # 项目说明
```

## 🎨 设计特色

### 登录页面
- 大背景图设计，右侧登录窗口
- 动态背景动画效果
- 毛玻璃效果和渐变设计
- 响应式布局适配

### 后台管理
- 可折叠侧边栏导航
- 面包屑导航和通知中心
- 统一的卡片式布局
- 丰富的交互动画

### 数据可视化
- Chart.js 图表集成
- 实时数据更新
- 多种图表类型支持
- 响应式图表设计

## 🔧 配置说明

### API配置
在 `src/utils/api.js` 中配置后端API地址：
```javascript
const API_BASE_URL = 'http://localhost:8000/api'
```

### 主题配置
在 `src/styles/variables.scss` 中自定义主题颜色和样式变量。

### 路由配置
在 `src/router/index.js` 中添加新的路由规则。

## 🚀 部署

### 构建生产版本
```bash
npm run build
```

### 部署到服务器
将 `dist` 目录下的文件部署到 Web 服务器即可。

### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 开发指南

### 代码规范
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case

### 组件开发
- 使用 Composition API
- 合理使用 ref 和 reactive
- 组件间通信使用 props/emit
- 复杂状态使用 Pinia 管理

### 样式开发
- 使用 SCSS 预处理器
- 遵循 BEM 命名规范
- 使用 CSS 变量支持主题切换
- 响应式设计优先

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📞 联系

如有问题，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**享受编码的乐趣！** 🎉