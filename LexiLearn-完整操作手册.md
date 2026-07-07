# LexiLearn 完整操作手册

> 从零搭建到当前状态的全流程记录  
> 最后更新：2026-07-06 23:43

---

## 目录

1. [项目概览](#1-项目概览)
2. [文件清单与清理建议](#2-文件清单与清理建议)
3. [操作时间线（从零到当前状态）](#3-操作时间线)
4. [技术架构图](#4-技术架构图)
5. [常见问题排查](#5-常见问题排查)
6. [后续维护指南](#6-后续维护指南)

---

## 1. 项目概览

### 是什么

LexiLearn（项目名 Lexiword）是一个**考研英语单词复习助手**，支持：
- 5560 个大纲单词的学习进度管理
- 多账号登录，数据云端同步隔离
- 打卡、收藏、集合管理
- 数据备份/恢复
- PWA 离线支持 + HBuilderX 原生 APK 打包

### 技术栈

| 层 | 技术 | 部署位置 |
|---|------|---------|
| **前端** | 纯 HTML/CSS/JS 单文件 SPA + Service Worker (PWA) | GitHub Pages |
| **后端** | Flask + SQLite + JWT (PyJWT + bcrypt) | PythonAnywhere 免费版 |
| **原生壳** | HBuilderX 5+App 云打包 | APK 安装到手机 |

### 关键地址

| 用途 | 地址 |
|------|------|
| 前端主页 | `https://minziqian48-sudo.github.io/lexiword-frontend/` |
| 登录页 | `https://minziqian48-sudo.github.io/lexiword-frontend/login.html` |
| 后端 API | `https://minziqian48.pythonanywhere.com/api/` |
| GitHub 仓库 | `https://github.com/minziqian48-sudo/lexiword-frontend` |
| PythonAnywhere 控制台 | https://www.pythonanywhere.com/minziqian48/ |
| GitHub Pages 设置 | https://github.com/minziqian48-sudo/lexiword-frontend/settings/pages |

### Git 提交历史摘要

共 **47 次提交**，按阶段划分：

```
ed52f8d  ── 初始 PWA 前端（manifest, sw.js, 图标）
e26cf50 ~ d864b09  ── 第一轮 bug 修复（数据合并格式、缓存策略）
3bcd6ff ~ 9a3c372  ── 功能增强（6项体验优化）
9e96539 ~ f6fa1b4  ── 多账号切换 + 快照机制（核心功能）
0771fb5 ~ b62dbe1  ── 致命 bug 修复（清数据卡死、竞态条件）
dd18ca8 ~ 1fc50a2  ── 缓存破坏 + 调试面板
13c4d22 ~ e07102b  ── 导入数据丢失根因修复（结构化合并逻辑缺陷）
cefd840 ~ b3f6614  ── 原生文件保存桥接 + 注册账号数据清理
045b53e ~ c9549ee  ── 多账号 localStorage 彻底隔离
b29221c ~ f5af281  ── 调试追踪日志
1bd5a1b ~ 97e5a6a  ── 区分切换账号 vs 普通刷新
759e1ef ~ b47a696  ── 日历闪现 + 切换丢数据防御
7ec7ce4  ── CORS 诊断
bdb4499  ── ★ 账号隔离修复（login 清旧数据 + 启动检测用户变化）【本次】
e6b48eb  ── ★ API 路径修复（16 处 /api/ 双重前缀 → 404）【本次】
35e71da  ── ★ 强制缓存刷新 v5 【本次】
7037bb0  ── ★ apiFetch 兼容层（自动去重 /api 前缀）【本次】
e98757d  ── ★ clearOldAppData 保留 lexi_accounts 【本次】
25bc01a  ── ★ 终极修复：QuotaExceededError 降级 + 无反馈修复 + API 兜底 【本次】
```

---

## 2. 文件清单与清理建议

### 当前文件一览

```
D:\project\Lexiword\
│
├── 📄 核心前端文件（必须保留）
│   ├── Lexiword.html          ← 主应用 SPA（3886行, 591KB）★ 核心
│   ├── login.html             ← 登录页（11KB）★ 核心
│   ├── manifest.json          ← PWA 配置（726B）★ 核心
│   ├── sw.js                  ← Service Worker（2KB）★ 核心
│   ├── favicon.png            ← 浏览器图标（687B）
│   ├── icon-192.png           ← PWA 图标 192px（5KB）
│   ├── icon-512.png           ← PWA 图标 512px（20KB）
│   └── icon-512-maskable.png  ← PWA 自适应图标（16KB）
│
├── 📄 文档
│   ├── CHANGELOG.md           ← 详细变更记录（24KB）✅ 保留
│   ├── LexiLearn-Knowledge-Base.md ← 知识库/踩坑记录（14KB）✅ 保留
│   └── overview.md            ← 项目概述（3.4KB）
│
├── 📂 backend/                ← Render.com 备份部署（独立 git 仓库）
│   ├── .git/                  ← 独立 git 历史（3次提交）
│   ├── app.py                 ← Flask 后端（25KB）
│   ├── schema.sql             ← 数据库建表 SQL（2.3KB）
│   ├── requirements.txt       ← Python 依赖（76B）
│   ├── render.yaml            ← Render 部署配置（267B）
│   └── venv/                  ← Python 虚拟环境
│
├── 📂 deploy_backend/         ← PythonAnywhere 实际部署版本
│   ├── app.py                 ← Flask 后端完整版（648行, 27KB）
│   ├── app_full.py            ← 含内嵌词库数据的完整版（6268行, 480KB）⚠️ 大文件
│   ├── schema.sql             ← 同上（2.3KB）
│   ├── requirements.txt       ← 同上（76B）
│   └── __pycache__/           ← Python 编译缓存 ⚠️ 可删
│
├── 📂 dist/                   ← 构建输出 / 旧版备份？
│   ├── index.html             ← 旧版 SPA（563KB）⚠️ 与 Lexiword.html 可能不同
│   └── login.html             ← 旧版登录页（10.7KB）
│
├── 🔧 数据处理脚本
│   ├── build_app.py           ← 词库注入脚本（2.7KB）⚠️ 一次性工具
│   ├── extract_daybook.py     ← 从 SPA 提取词库数据（1KB）⚠️ 一次性工具
│   └── daybook_data.py        ← 提取出的词库数据（434KB）⚠️ 中间产物
│
├── 🔐 SSL 证书（⚠️ 敏感文件，不应在仓库中）
│   ├── lexilearn.crt
│   ├── lexilearn.key          ← 私钥！⚠️ 应删除
│   └── lexilearn.pem
│
├── 📦 工具
│   └── uber-apk-signer.jar    ← APK 签名工具（3.2MB）⚠️ 不应在代码仓库
│
├── 📝 其他
│   ├── .gitignore
│   └── overview.md            ← AI 生成的概述报告
```

### 清理建议

| 文件/目录 | 建议 | 原因 |
|----------|------|------|
| `deploy_backend/__pycache__/` | **🗑 删除** | Python 编译缓存，可随时重建 |
| `deploy_backend/app_full.py` | **🗑 删除或移出仓库** | 480KB，含内嵌词库数据的一次性生成文件 |
| `dist/index.html`, `dist/login.html` | **🗑 删除** | 旧版构建输出，与根目录的 Lexiword.html 不一致 |
| `build_app.py` | **📦 移到 tools/ 或删除** | 一次性词库注入工具，已执行完毕 |
| `extract_daybook.py` | **📦 移到 tools/ 或删除** | 一次性提取工具 |
| `daybook_data.py` | **🗑 删除** | 434KB 中间产物，数据已注入 app_full.py |
| `lexilearn.key` | **⚠️ 必须从仓库删除** | SSL 私钥泄露风险 |
| `lexilearn.crt`, `lexilearn.pem` | **建议移出仓库** | 证书文件不应在代码仓库 |
| `uber-apk-signer.jar` (3.2MB) | **🗑 删除** | 第三方工具，不在代码仓库范围 |
| `backend/` 整个目录 | **📦 评估是否需要** | 与 deploy_backend/ 功能重复，是早期 Render 版本 |
| `overview.md` | **🗑 删除** | AI 生成的临时分析报告 |
| `.gitignore` | **✅ 保留并补充** | 应加入上述文件的忽略规则 |

### 建议的新 `.gitignore`

```markdown
# Python
__pycache__/
*.py[cod]
venv/
*.egg-info/

# 一次性工具和中间产物
build_app.py
extract_daybook.py
daybook_data.py
deploy_backend/app_full.py
dist/

# 敏感文件 - 绝对不能提交
*.key
*.pem
*.crt

# 第三方工具
*.jar

# AI 临时文件
overview.md/

# OS
.DS_Store
Thumbs.db
```

---

## 3. 操作时间线

以下按时间顺序排列，标注每一步是谁操作的。

---

### 阶段一：项目初始化与基础搭建

> 目标：让一个空白的 Web 应用跑起来，具备基本的单词学习界面。

#### Step 1 — 创建前端 SPA 骨架

**操作者：[AI 自动完成]**

创建 `Lexiword.html`，包含：
- HTML 结构：导航栏、搜索框、词库展示区、底部 Tab 栏
- CSS 样式系统：深蓝紫色主题（`#4C52E8` 主色），Design Token 变量体系，支持亮色/暗色模式切换
- JavaScript 核心：词库数据（5560个单词硬编码为 `DAYBOOK_DATA`）、本地存储读写（localStorage）、UI 渲染函数

关键代码位置：
- 第 1-200 行：HTML 骨架 + CSS Design Token
- 第 200-800 行：CSS 样式（卡片、动画、响应式、暗色模式）
- 第 800-1700 行：JavaScript 数据定义（DAYBOOK_DATA 词库数组）
- 第 1700-2400 行：API 封装函数（apiFetch, apiPost 等）
- 第 2400-3300 行：UI 渲染与事件绑定
- 第 3300-3600 行：多账号快照系统
- 第 3600-3886 行：初始化入口 + 导入导出 + 备份恢复

#### Step 2 — 创建登录页

**操作者：[AI 自动完成]**

创建 `login.html`（259 行），包含：
- 登录/注册表单
- 记住的账号列表（从 `lexi_accounts` 读取）
- Token 管理（存取 `lexiword_token`）

#### Step 3 — 创建 PWA 配置

**操作者：[AI 自动完成]**

创建三个文件：
- `manifest.json` — PWA 应用清单（名称、图标、主题色、start_url 指向 login.html）
- `sw.js` — Service Worker（预缓存静态资源，网络优先回退到缓存策略）
- `icon-192.png`, `icon-512.png`, `icon-512-maskable.png`, `favicon.png` — 应用图标

#### Step 4 — 创建 GitHub 仓库并启用 Pages

**操作者：[需要用户操作]**

```
① 在 GitHub 上新建仓库 lexiword-frontend
② git init
③ git add .
④ git commit -m "Initial commit: LexiLearn PWA frontend"
⑤ git remote add origin https://github.com/minziqian48-sudo/lexiword-frontend.git
⑥ git push -u origin main
⑦ 进入 Settings → Pages → Source 选择 "Deploy from branch: main"
⑧ 等待几分钟，访问 minziqian48-sudo.github.io/lexiword-frontend/
```

**结果**：前端通过 GitHub Pages 在线托管，全球 CDN 加速。

---

### 阶段二：后端搭建

> 目标：提供 RESTful API 支持注册、登录、数据持久化和多账号隔离。

#### Step 5 — 设计数据库 Schema

**操作者：[AI 自动完成]**

创建 `schema.sql`，共 9 张表：

```sql
users              -- 用户表（id, email, password_hash, created_at）
user_states        -- 学习状态（user_id, day, word, state, updated_at）
user_stars         -- 收藏（user_id, word, created_at）
user_checkin       -- 打卡记录（user_id, date, count, words_json）
user_sets          -- 词汇集（id, user_id, name, words_json, sort_order）
user_pins          -- 固定单词（user_id, word, pin_order）
user_bookmarks     -- 书签（user_id, word, position_pct）
user_sets_sync     -- 集合同步队列
backups            -- 备份（user_id, data_json, created_at）
```

核心设计原则：所有业务表都有 `user_id` 字段，查询时强制带 `WHERE user_id = ?`。

#### Step 6 — 编写 Flask 后端

**操作者：[AI 自动完成]**

创建 `deploy_backend/app.py`（648 行），包含 27 个 API 端点：

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/auth/register` | 注册（bcrypt 密码哈希） |
| POST | `/auth/login` | 登录（JWT token） |
| GET | `/auth/me` | 获取当前用户信息 |
| GET | `/daybook` | 公开接口：获取全部 5560 个单词 |
| GET | `/states` | 获取当前用户的学习状态 |
| PUT | `/states/:day/:word` | 更新单个单词状态 |
| PUT | `/states/batch` | 批量更新状态 |
| PUT | `/star/:word` | 收藏/取消收藏 |
| GET | `/checkin` | 获取打卡记录 |
| POST | `/checkin` | 提交打卡 |
| GET | `/sets` | 获取词汇集列表 |
| POST | `/sets/sync` | 同步词汇集 |
| GET | `/pins` | 获取固定单词 |
| PUT | `/pins` | 更新固定单词 |
| GET | `/bookmark` | 获取书签 |
| PUT | `/bookmark` | 更新书签 |
| POST | `/restore` | 从备份恢复 |
| DELETE | `/backup/:id` | 删除备份 |

关键技术决策：
- **密码**：使用 bcrypt（不自己实现哈希）
- **认证**：JWT token（payload 含 user_id, iat, exp）
- **数据库**：SQLite（免费版够用，单文件无运维）
- **CORS**：允许所有来源（`Access-Control-Allow-Origin: *`）

#### Step 7 — 部署到 PythonAnywhere

**操作者：[需要用户操作]**

```
① 注册 pythonanywhere.com 免费账号（用户名 minziqian48）
② 创建 Web 应用 → 选 Manual Configuration → Python 3.x
③ 通过 Bash 面板上传 deploy_backend/ 下的文件到项目目录
④ pip install flask pyjwt bcrypt
⑤ 在 WSGI 配置文件中设置：
   import sys; sys.path.insert(0, '/home/minziqian48/mysite')
   from app import app as application
⑥ 重载 Web App
⑦ 访问 https://minziqian48.pythonanywhere.com/api/health 验证
```

**注意**：PythonAnywhere 免费版限制较多（不能自定义域名、白名单 IP、Worker 有超时），但个人小应用足够用。

---

### 阶段三：数据流水线 —— 把 5560 个单词导入服务器

> 目标：从前端 SPA 的 JavaScript 代码中提取词库数据，注入后端数据库。

#### Step 8 — 提取词库数据

**操作者：[AI 自动完成]**

运行 `extract_daybook.py`，解析 `Lexiword.html` 中的 `const DAYBOOK_DATA = [...]` 数组，
输出为 `daybook_data.py`（434KB 的 Python 字典变量）。

#### Step 9 — 注入后端

**操作者：[AI 自动完成]**

运行 `build_app.py`，将 `daybook_data.py` 合并到 `app.py` 末尾，
生成 `app_full.py`（6268行，480KB）。这个文件同时包含 API 逻辑和完整的词库数据。

**实际部署时使用的是 `app_full.py`**，而不是精简版的 `app.py`。

---

### 阶段四：HBuilderX 原生打包（可选）

> 目标：把 Web 应用包装成 Android APK，可以安装到手机桌面。

#### Step 10 — 准备 HBuilderX 项目

**操作者：[需要用户操作]**

```
① 安装 DCloud HBuilderX
② 新建 5+App 项目，放在 D:\data\HBuilderProjects\LexiLearn\
③ 将 LexiLearn-Knowledge-Base 下的前端代码复制进去
④ 修改 manifest.json：
   - launch_path: "index.html" （原生壳入口）
   - permissions 中添加 Share, Storage, Downloader, File 等
⑤ 创建 index.html（壳页面）：
   - 检查 localStorage 中的 token
   - 有效 → plus.webview.create() 加载 GitHub Pages URL
   - 无效 → 跳转 login.html
⑥ 准备图标资源（img/icon.png, img/icon-xxxhdpi.png 等）
```

#### Step 11 — 云端打包 APK

**操作者：[需要用户操作]**

```
① HBuilderX 菜单 → 发行 → 原生App-云打包
② 使用公共测试证书（或自有证书）
③ 等待 DCloud 云端构建完成
④ 下载 APK 安装包
⑤ 手机安装测试
```

**注意事项**：
- 打包后的 APK 内部代码是**快照**，不会自动更新
- 每次修改前端代码后都需要重新打包
- 如果不需要原生能力（推送通知等），建议直接用浏览器访问 PWA + 添加到主屏幕

---

### 阶段五：Bug 修复马拉松（47 次提交的核心内容）

> 这是项目的主体部分——发现和修复各种问题。以下是按时间顺序排列的关键修复。

#### 🔴 Bug #1 — Service Worker 缓存导致用户无法获取更新

**现象**：修改了代码推送到 GitHub Pages，但用户刷新后还是旧版。

**根因**：`sw.js` 使用了强缓存策略，浏览器优先使用缓存的旧版 JS/CSS/HTML。

**修复**：
- **[AI 自动完成]** 升级缓存名 `lexilearn-v3` → `v4` → `v5`
- **[AI 自动完成]** 在 `index.html` 和 `Lexiword.html` 加入 cache-busting 参数 `?_t=Date.now()`
- **[AI 自动完成]** `sw.js` install 时删除旧版缓存

**经验**：PWA 的 SW 缓存是把双刃剑。开发阶段建议关闭 SW（注释掉注册代码），稳定后再开启。

---

#### 🔴 Bug #2 — 切换账号后卡死 / 白屏

**现象**：点击"切换账号"→ 登录另一个账号 → 白屏，JS 报错。

**根因**：
1. `_restoreAccountSnapshot()` 是异步 Promise，但 `initData()` 没有等待它完成就开始渲染
2. 快照数据量太大时同步写入 localStorage 导致主线程阻塞

**修复**：
- **[AI 自动完成]** `_clearLexiLocalStorage` 分批异步清除（每次 50ms 暂停）
- **[AI 自动完成]** `initData` await `_restoreAccountSnapshot`
- **[AI 自动完成]** 加遮罩安全网（恢复过程中显示加载动画）

---

#### 🔴 Bug #3 — 清数据后登录卡死

**现象**：退出登录清了数据 → 回到登录页 → 输入密码 → 卡住不动。

**根因**：`clearOldAppData` 清掉了 `lexi_accounts`（记住的账号列表），导致登录页渲染报错。

**修复**：
- **[AI 自动完成]** 清除数据时排除 `lexi_accounts` 键
- **[AI 自动完成]** 登录页增加防御性检查（accounts 为 null 时显示空列表）

---

#### 🔴 Bug #4 — 导入数据丢失

**现象**：备份 JSON 导入后，部分学习记录消失。

**根因**：`_mergeLocalStorageIntoCache()` 的合并逻辑有缺陷：
- 原始数据用下划线格式 `4_word`，但合并时代码期望冒号格式 `4:word`
- 合并时 localStorage 始终覆盖 API 数据（"本地优先"策略导致服务器的数据被忽略）

**修复**：
- **[AI 自动完成]** 格式转换：检测下划线 → 替换为冒号
- **[AI 自动完成]** 结构化合并：区分 states/starred/checkin/pins/bookmark 各自合并
- **[AI 自动完成]** 最终版改为：API 数据为基础 → localStorage 增量覆盖 → 结果写回内存

---

#### 🔴 Bug #5 — 日历闪现

**现象**：打开 App 时，日历区域短暂显示原始 DOM 内容后才渲染正确数据。

**根因**：`initData` 是异步的，但在它完成之前 HTML 已经显示了默认内容。

**修复**：**[AI 自动完成]** 默认隐藏日历容器，`initData` 完成后再显示。

---

#### 🔴 Bug #6 — API 路径双重 /api/ 前缀（★★★ 本次重点修复）

**现象**：Console 报错 `GET /api/api/states 404 Not Found`，所有数据请求失败。

**根因**：
```javascript
// 定义时已经包含了 /api
const API_BASE = 'https://minziqian48.pythonanywhere.com/api';

// 但调用时又加了 /api/
apiFetch('GET', '/api/states')  
// → 实际请求: .../api/api/states → 404！
```

16 处调用全部存在这个问题。

**修复（两层防护）**：

**第一层 — 修正路径** `[AI 自动完成]`
```javascript
// 修正前
apiFetch('GET', '/api/states')
// 修正后
apiFetch('GET', '/states')
```
批量替换 16 处（6 处 GET + 3 处 POST + 7 处 PUT）。

**第二层 — 兼容层** `[AI 自动完成]`
```javascript
async function apiFetch(method, path, body) {
    // ★ 新增：自动去除重复的 /api 前缀
    const cleanPath = path.replace(/^\/api\//, '/');
    const url = API_BASE + cleanPath;
    // ... 后续不变
}
```
即使 CDN 缓存的还是旧版路径，也能正确工作。

---

#### 🔴 Bug #7 — 多账号数据隔离失效（★★★ 本次核心修复）

**现象**：用户 A 学习了一段时间 → 退出 → 用户 B 登录 → B 看到 A 的学习记录。

**根因分析（三层漏洞叠加）**：

**漏洞 A：`clearOldAppData()` 是死代码**
```javascript
// login.html 第 143 行
function clearOldAppData() {
    // 正确的清除逻辑...
}
// ❌ 但是 doLogin() 和 doRegister() 从来没调用过它！
```

**漏洞 B：非切换模式不清数据**
```javascript
// Lexiword.html 第 3323 行
function _restoreAccountSnapshot(userId) {
    var isSwitching = localStorage.getItem('lexi_switching') === '1';
    
    if (isSwitching) {
        // ✅ 切换：清除 → 写入快照 → merge
        _clearLexiLocalStorage(true, true);
        // ...
    } else {
        // ❌ 直接 merge，不清除！A 的数据还在 localStorage 里！
        _mergeLocalStorageIntoCache();
    }
}
```

**漏洞 C：`_mergeLocalStorageIntoCache` 本地优先**
```javascript
// 它遍历 localStorage 全部 lexi_db_* 键
// 无条件覆盖 API 返回的数据
// 所以 A 的残留数据混进了 B 的内存缓存
```

**触发场景**：
1. 用户 A 学习 → localStorage 存满 A 的数据
2. A 退出（或不退出），用户 B **直接打开 login.html 登录**
3. `lexi_switching` 标记不存在 → isSwitching = false
4. 不清除 → merge → A 的数据混进 B 的缓存

**修复（四层防线）**：

**防线 1 — login.html 入口清数据** `[AI 自动完成]`
```javascript
async function doLogin() {
    // ... 验证邮箱密码 ...
    clearOldAppData();  // ★ 登录前清除旧数据（保留 lexi_accounts）
    setToken(data.token);
    window.location.href = 'Lexiword.html?_t=' + Date.now();
}
```

**防线 2 — 启动时检测用户变化** `[AI 自动完成]`
```javascript
function _restoreAccountSnapshot(userId) {
    var isSwitching = localStorage.getItem('lexi_switching') === '1';
    
    // ★ 新增：对比上次 userId，不同则视为切换
    var lastUser = localStorage.getItem('lexi_last_user');
    if (!isSwitching && lastUser && lastUser !== String(userId)) {
        console.warn('[STARTUP] user changed, forcing switch mode');
        isSwitching = true;
    }
    localStorage.setItem('lexi_last_user', String(userId));
    localStorage.removeItem('lexi_switching');
}
```

**防线 3 — clearOldAppData 保留账号列表** `[AI 自动完成]`
```javascript
function clearOldAppData() {
    const prefixes = ['wrev3_', 'checkin_'];  // ★ 不再包含 'lexi_'
    // 这样 lexi_accounts, lexi_snap_* 都不会被清
    for(let i=localStorage.length-1;i>=0;i--){
        const k=localStorage.key(i);
        if(k && prefixes.some(p=>k.startsWith(p))){
            localStorage.removeItem(k);
        }
    }
}
```

**防线 4 — 无快照时 API 兜底** `[AI 自动完成]`
```javascript
if (!raw) {
    // 本地没有该用户的快照？从服务器拉！
    try {
        const serverStates = await apiFetch('GET', '/states');
        // 将服务器数据写入 localCache...
        console.log('[STARTUP] loaded', Object.keys(serverStates).length, 'states from API');
    } catch(e) { console.warn('[STARTUP] API fallback failed', e); }
}
```

---

#### 🔴 Bug #8 — QuotaExceededError 快照溢出（★ 本次终极修复）

**现象**：Console 报红色错误 `Setting the value of 'lexi_snap_10' exceeded the quota`，切换账号后数据丢失。

**根因**：`_saveAccountSnapshot()` 将**全部 localStorage 数据**序列化为一个大 JSON 字符串存回去。
学得越多数据越大，超过浏览器 5MB 限额就静默失败 → 快照丢失 → 切回来没数据。

**修复 — 三级降级策略** `[AI 自动完成]`
```javascript
function _saveAccountSnapshot(userId) {
    const snap = _collectBackupData().data;
    
    try {
        // Level 1：正常保存（全量快照）
        localStorage.setItem('lexi_snap_' + userId, JSON.stringify(snap));
    } catch (e) {
        if (e.name === 'QuotaExceededError' || e.code === 22) {
            console.warn('[SNAP] quota exceeded, saving essential-only');
            try {
                // Level 2：只存核心数据（states + starred + checkin）
                const essential = {
                    states: snap.states,
                    starred: snap.starred || {},
                    checkin: snap.checkin || {}
                };
                localStorage.setItem('lexi_snap_' + userId, JSON.stringify(essential));
            } catch (e2) {
                // Level 3：放弃本地快照，依赖服务器 API
                console.error('[SNAP] essential save failed, relying on API');
            }
        }
    }
}
```

---

#### 🟡 Bug #9 — 点击单词无反馈

**现象**：点击单词卡片改变学习状态后，不知道保存成功还是失败。

**根因**：`dbSetState()` 用 `apiFetchSilent` 发请求，但 `.catch()` 是空的，错误被吞掉。

**修复** `[AI 自动完成]`
```javascript
function dbSetState(day, word, s) {
    const key = day + ':' + word;
    localCache.states[key] = parseInt(s);
    apiFetchSilent('PUT', '/states/'+day+'/'+encodeURIComponent(word), {state:s})
        .catch(err => showToast('⚠️ 状态保存失败: ' + err.message, 3000));  // ★ 新增
}
```

---

## 4. 技术架构图

### 系统全景

```
┌─────────────────────────────────────────────────────────────┐
│                        用户设备                               │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ 手机浏览器    │   │ PC 浏览器     │   │ HBuilderX APK  │  │
│  │ (PWA 离线)   │   │ (GitHub Pages)│  │ (WebView 壳)   │  │
│  └──────┬───────┘   └──────┬───────┘   └───────┬────────┘  │
│         │                   │                    │          │
│         └───────────┬───────┘────────────────────┘          │
│                     ▼                                       │
│              ┌─────────────┐                                │
│              │ Lexiword.html│ ← 3886行 SPA                   │
│              │ login.html   │ ← 259行                       │
│              │ sw.js        │ ← Service Worker               │
│              └──────┬───────┘                                │
│                     │ fetch()                               │
└─────────────────────┼───────────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    PythonAnywhere                            │
│                                                              │
│              ┌──────────────────────┐                        │
│              │   Flask (app.py)      │                        │
│              │   SQLite (db.sqlite)  │                        │
│              └──────────┬───────────┘                        │
│                         │                                    │
│  ┌──────────────────────┼──────────────────────┐             │
│  ▼                      ▼                      ▼             │
│ /auth/*               /states/*             /backup/*       │
│ 注册/登录/JWT          学习状态 CRUD         备份/恢复       │
│ /checkin/*            /sets/*               /pins/*         │
│ 打卡                   集合管理              固定单词        │
│ /star/*               /bookmark/*           /daybook        │
│ 收藏                   书签                  5560个单词(公开) │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     GitHub                                   │
│  ┌──────────────────────────────────────────────────┐        │
│  │  Repository: lexiword-frontend                   │        │
│  │  Branch: main → GitHub Pages 自动部署             │        │
│  │  URL: minziqian48-sudo.github.io/lexiword-frontend│        │
│  └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 数据流：多账号切换时的完整流程

```
用户点击"切换账号"
       │
       ▼
┌─ doLoginOther() ─────────────────────────────────┐
│ 1. _saveAccountSnapshot(当前用户ID)                │
│    → 收集全部 lexi_db_*, wrev3_*, checkin_* 数据   │
│    → JSON.stringify → localStorage('lexi_snap_N') │
│    → 配额溢出? → 降级只存 states+starred+checkin   │
│    → 还溢出? → 放弃(靠服务器兜底)                   │
│                                                  │
│ 2. _clearLexiLocalStorage(false, true)            │
│    → 删除 wrev3_*, checkin_* 数据                  │
│    → 保留 lexi_accounts (账号列表)                 │
│    → 保留 lexi_snap_* (所有快照)                   │
│                                                  │
│ 3. localStorage.setItem('lexi_switching', '1')    │
│ 4. window.location.href = 'login.html'            │
└──────────────────────────────────────────────────┘
       │
       ▼
┌─ login.html ─────────────────────────────────────┐
│ 用户选择/输入另一个账号 → doLogin()               │
│   1. clearOldAppData()                           │
│      → 删除 wrev3_*, checkin_* 残留数据           │
│      → 保留 lexi_accounts                        │
│   2. POST /auth/login → 获得 token               │
│   3. setToken(token)                             │
│   4. 跳转 Lexiword.html                          │
└──────────────────────────────────────────────────┘
       │
       ▼
┌─ Lexiword.html 启动 ─────────────────────────────┐
│ 1. 读取 token → GET /auth/me → 得到 _currentUser  │
│ 2. _restoreAccountSnapshot(新用户ID)              │
│   ├─ 读取 lexi_switching='1' → isSwitching=true   │
│   ├─ (防御) 对比 lexi_last_user → 不同? 强制切换  │
│   ├─ 读取 lexi_snap_新用户ID                       │
│   │  ├─ 有快照 → 解析 → 写入 localStorage → merge │
│   │  └─ 无快照 → GET /states 从服务器拉数据        │
│   └→ resolve() → initData() 继续                 │
│ 3. 渲染 UI → 用户看到自己的干净数据 ✅             │
└──────────────────────────────────────────────────┘
```

---

## 5. 常见问题排查

### Q1: 推送后 GitHub Pages 没更新？

**原因**：CDN 全球同步需要 5-30 分钟。
**验证**：`curl -s "https://raw.githubusercontent.com/.../main/Lexiword.html"` 查看仓库原始文件
**加速方法**：改 `sw.js` 的 CACHE_NAME 触发 SW 重装

### Q2: 开 VPN 后 API 请求失败？

**原因**：Clash/V2Ray 代理规则将 PythonAnywhere 请求转发到了奇怪域名。
**解决**：在 Clash Verge → 规则 → 添加两条前置直连规则：
```
DOMAIN-SUFFIX, pythonanywhere.com, DIRECT
DOMAIN-SUFFIX, github.io, DIRECT
```
**日常使用不需要开 VPN**，GitHub Pages 和 PythonAnywhere 国内均可直连。

### Q3: Console 出现 QuotaExceededError？

**原因**：localStorage 超过 5MB 限额（通常是快照太大）。
**现状**：已添加三级降级保护，即使溢出也不会丢失数据（降为核心数据或依赖服务器）。

### Q4: HBuilderX 打包出现 Share 模块缺失弹窗？

**原因**：manifest.json 虽然声明了 Share 权限，但云端打包时未编译进去。
**解决**：HBuilderX → manifest.json 可视化界面 → 模块权限 → 勾选 Share → 重新打包
**影响**：仅影响原生分享功能（分享到微信/QQ），不影响数据同步和备份。

### Q5: 如何确认前后端都正常？

```bash
# 健康检查
curl https://minziqian48.pythonanywhere.com/api/health
# 预期: {"status":"ok","service":"LexiLearn API"}

# 前端是否已更新
curl -s "https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html" \
  | grep -o "apiFetchSilent('PUT', '[^']*'"
# 预期: apiFetchSilent('PUT', '/states/'  (不是 /api/states/)
```

---

## 6. 后续维护指南

### 每次修改前端代码后的标准流程

```
① [AI] 修改 Lexiword.html 或 login.html
② [AI] git add + git commit (写清楚改了什么)
③ [需用户确认VPN关闭] git push origin main
④ [等待] GitHub Pages 部署（Settings/Pages 查看 Last deployed 时间）
⑤ [验证] 无痕窗口打开 ?t=随机数 参数
⑥ [可选] 如需手机生效 → HBuilderX 重新打包 APK
```

### 安全待办事项

| 优先级 | 事项 | 操作者 |
|--------|------|--------|
| 🔴 高 | 删除 `lexilearn.key` 并轮换证书 | [需用户操作] |
| 🟡 中 | 从 Git 历史中彻底清除密钥文件（git filter-repo） | [需用户操作] |
| 🟡 中 | 清理无用文件（见第 2 节清单） | [AI 自动完成] |
| 🟢 低 | 给 backend/ 和 deploy_backend/ 统一成一个目录 | [AI 自动完成] |

### 代码质量改进方向

1. **拆分单文件**：将 Lexiword.html（3886行）拆分为模块化 JS + 外部 CSS
2. **引入构建工具**：Vite/esbuild 可以解决 CDN 缓存问题（文件名 hash）
3. **TypeScript 迁移**：类型安全可以避免很多 runtime 错误
4. **单元测试**：对 _saveAccountSnapshot / _restoreAccountSnapshot / _mergeLocalStorageIntoCache 写测试
5. **CI/CD**：GitHub Actions push 后自动测试 + Lighthouse 性能评分

---

## 附录 A：本次修复的所有改动汇总

| 提交 | 改动的文件 | 行数 | 说明 |
|------|-----------|------|------|
| `bdb4499` | login.html (+3), Lexiword.html (+6) | +9 | 登录清旧数据 + 启动检测用户变化 |
| `e6b48eb` | Lexiword.html (16处路径修正) | ~16 | /api/api/ → /api/ |
| `35e71da` | Lexiword.html, login.html, sw.js | 少量 | 强制缓存刷新 v5 |
| `7037bb0` | Lexiword.html apiFetch 函数 (~+5行) | +5 | 兼容层：自动去重 /api/ 前缀 |
| `e98757d` | login.html clearOldAppData | ~-3 | 保留 lexi_accounts 不清 |
| `25bc01a` | Lexiword.html 三处函数重写 | ~+40 | QuotaExceeded 降级 + toast反馈 + API兜底 |

**总计**：约 **80 行新增/修改**，分布在 2 个核心文件中。

---

## 附录 B：关键函数索引

| 函数名 | 文件 | 行号 | 作用 |
|--------|------|------|------|
| `apiFetch()` | Lexiword.html | ~1688 | 通用 API 请求封装（含兼容层） |
| `apiPost()` | Lexiword.html | ~1715 | POST 简写 |
| `doLogin()` | login.html | ~188 | 登录流程（含 clearOldAppData） |
| `clearOldAppData()` | login.html | ~143 | 清除旧数据（保留 lexi_accounts） |
| `_saveAccountSnapshot()` | Lexiword.html | ~2890 | 保存账号快照（三级降级） |
| `_restoreAccountSnapshot()` | Lexiword.html | ~3323 | 恢复账号快照（含用户变化检测 + API兜底） |
| `_clearLexiLocalStorage()` | Lexiword.html | ~3000 | 清除指定前缀的 localStorage |
| `_mergeLocalStorageIntoCache()` | Lexiword.html | ~3050 | localStorage → 内存缓存合并 |
| `_collectBackupData()` | Lexiword.html | ~2940 | 收集全部数据用于备份/快照 |
| `dbSetState()` | Lexiword.html | ~2420 | 更新单个单词状态（含 toast 反馈） |
| `doLoginOther()` | Lexiword.html | ~3568 | 切换账号（保存快照 + 清数据 + 跳转） |
| `doLogout()` | Lexiword.html | ~3590 | 退出登录（保存快照 + 清数据） |
| `initData()` | Lexiword.html | ~3400 | 应用启动初始化（await 快照恢复） |

---

*手册结束。如有疑问，对照代码中的行号和此手册排查即可。*
