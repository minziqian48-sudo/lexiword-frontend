# LexiLearn 手机端 App 部署指南

## 当前架构

```
📱 手机 App (APK)
    ↓
🌐 前端 PWA (GitHub Pages)
   https://minziqian48-sudo.github.io/lexiword-frontend/
    ↓
🐍 后端 API (PythonAnywhere)
   https://minziqian48.pythonanywhere.com/api
    ↓
💾 数据库 (SQLite on PythonAnywhere, 数据不丢失)
```

## 已完成

- ✅ PWA 配置文件 (manifest.json, sw.js)
- ✅ 应用图标 (192x192, 512x512, 512x512 maskable)
- ✅ login.html 和 Lexiword.html 添加 PWA 支持
- ✅ 前端部署到 GitHub Pages (永久 HTTPS 地址)
- ✅ 后端 CORS 允许所有来源
- ✅ API 测试通过 (注册/登录正常)

## 生成 APK 步骤 (PWABuilder)

1. 打开 https://www.pwabuilder.com
2. 在输入框填入: `https://minziqian48-sudo.github.io/lexiword-frontend/`
3. 点击 "Start" 按钮
4. 等待分析完成 (约 10-20 秒)
5. 点击 "Package For Stores"
6. 选择 "Android"
7. 填写:
   - Package ID: `com.lexilearn.app`
   - App Name: `LexiLearn`
   - Version: `1.0.0`
8. 点击 "Generate Package"
9. 下载生成的 APK 文件
10. 把 APK 传到手机安装

## 关键地址

| 组件 | 地址 |
|------|------|
| 前端 PWA | https://minziqian48-sudo.github.io/lexiword-frontend/ |
| 后端 API | https://minziqian48.pythonanywhere.com/api |
| 前端 GitHub 仓库 | https://github.com/minziqian48-sudo/lexiword-frontend |
| 后端 GitHub 仓库 | https://github.com/minziqian48-sudo/lexiword-backend |

## 文件说明

| 文件 | 作用 |
|------|------|
| login.html | 登录/注册页面 |
| Lexiword.html | 主应用 (背单词/复习/收藏/打卡) |
| manifest.json | PWA 应用配置 (名称/图标/主题色) |
| sw.js | Service Worker (离线缓存支持) |
| icon-192.png | 应用图标 192x192 |
| icon-512.png | 应用图标 512x512 |
| icon-512-maskable.png | 应用图标 512x512 (适配各种形状) |
| favicon.png | 浏览器标签页图标 |

## 2026-07-06 更新

### 修复与优化

| 问题 | 解决方案 |
|------|---------|
| 导出备份缺少数据 | `_collectBackupData()` 现在扫描所有 `lexi_*`/`wrev3_*`/`checkin_*` localStorage 键，导出导入但未同步的数据、自定义释义、访问天数等 |
| HBuilderX 导出报错"未添加 share 模块" | `D:\data\HBuilderProjects\LexiLearn\manifest.json` 已添加 `Share` 权限（明天云打包时生效） |
| 词库滑轨位置不准 | 移除基于单词索引的虚拟估算，改用真实滚动比例 `scrollTop/scrollHeight` |
| 退出登录按钮常驻 | 移除顶部常驻按钮，底部导航新增"我的"面板（数据备份 + 退出登录） |
| 大量卡片点击卡顿 | `.word-card` 添加 `content-visibility:auto` + `contain:layout style paint`；非"常显"模式下延迟创建中文释义元素 |
| 大纲词详情缺少功能 | 新增 2/3/4 列切换；单词卡片新增书签按钮（与词库共用同一书签） |
| 集合不能新建 | `saveSets()` 增加 localStorage 兜底；`initData()` 后端为空时合并本地数据；创建成功显示 toast |

### HBuilderX 重新打包注意事项

明天云打包前，请确认：

1. `D:\data\HBuilderProjects\LexiLearn\manifest.json` 已包含 `Share` 权限
2. `index.html` 已恢复为正常加载远程 URL 的版本（当前可能还是数据提取工具版）
3. 打包后在手机上**清除 App 数据**再重新打开，避免旧 Service Worker 缓存影响
