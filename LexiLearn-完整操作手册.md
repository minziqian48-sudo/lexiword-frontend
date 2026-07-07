# LexiLearn 完整操作手册（权威版 v2）

> **从零重建到当前状态的全流程手册**  
> 本手册是项目唯一权威参考。任何 AI 助手或维护者阅读本手册即可完整理解项目、部署架构、已知坑，并据此从零重建/维护当前状态。  
> 最后更新：**2026-07-07 19:00**（自查修正版）
> 对应代码版本：`4685184`（Git HEAD，含本次自查修复）

---

## 目录

1. [项目概览（当前状态）](#1-项目概览当前状态)
2. [设计系统：温暖米色调（当前主题）](#2-设计系统温暖米色调当前主题)
3. [文件清单（当前真实状态）](#3-文件清单当前真实状态)
4. [技术架构](#4-技术架构)
5. [后端 Flask API](#5-后端-flask-api)
6. [前端主应用 Lexiword.html](#6-前端主应用-lexiwordhtml)
7. [登录页 login.html](#7-登录页-loginhtml)
8. [书签系统（前端多书签 / 后端单书签）](#8-书签系统前端多书签--后端单书签)
9. [数据持久化与多账号隔离](#9-数据持久化与多账号隔离)
10. [备份与分享功能](#10-备份与分享功能)
11. [自定义滚动滑轨](#11-自定义滚动滑轨)
12. [HBuilderX 原生壳与 APK](#12-hbuilderx-原生壳与-apk)
13. [部署流程（三端）](#13-部署流程三端)
14. [从零重建步骤（提示词 + 命令）](#14-从零重建步骤提示词--命令)
15. [已知问题与不一致项（必读）](#15-已知问题与不一致项必读)
16. [常见问题排查](#16-常见问题排查)
17. [维护指南](#17-维护指南)
18. [附录 A：关键函数索引](#附录-a关键函数索引)
19. [附录 B：Git 提交历史摘要](#附录-bgit-提交历史摘要)

---

## 1. 项目概览（当前状态）

### 是什么

**LexiLearn**（项目名 Lexiword）是一个**考研英语单词复习助手**，支持：
- 5560 个大纲单词的学习进度管理（4 种学习状态）
- 多账号登录，数据云端同步 + 本地隔离
- 打卡、星标、词汇集（集合）管理
- **多书签系统**（词库 / 大纲词各自最多 10 个，互相独立）
- 数据备份 / 恢复 / 分享（微信、系统分享、文件下载）
- PWA 离线支持 + HBuilderX 原生 APK 打包

### 当前视觉风格

> **温暖米色调（Bear / Linear 风格）** —— 2026-07-06 起全面重构，取代初版的深蓝紫冷色调。
> 主色：焦糖棕 `#C4956A`，背景：暖米白 `#FBF7F0`，支持亮/暗双主题。
> APP 图标：🐱 卡通白猫读书（AI 生成，见第 12 节）。

### 技术栈

| 层 | 技术 | 部署位置 |
|---|------|---------|
| **前端** | 纯 HTML/CSS/JS 单文件 SPA + Service Worker (PWA) | GitHub Pages |
| **后端** | Flask + SQLite + JWT (PyJWT + bcrypt) | PythonAnywhere 免费版 |
| **原生壳** | HBuilderX 5+App 云打包（壳加载线上 GitHub Pages URL） | APK 安装到手机 |

### 关键地址

| 用途 | 地址 |
|------|------|
| 前端主页 | `https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html` |
| 登录页 | `https://minziqian48-sudo.github.io/lexiword-frontend/login.html` |
| 后端 API | `https://minziqian48.pythonanywhere.com/api/` |
| GitHub 仓库 | `https://github.com/minziqian48-sudo/lexiword-frontend` |
| PythonAnywhere 控制台 | https://www.pythonanywhere.com/console/ |
| GitHub Pages 设置 | https://github.com/minziqian48-sudo/lexiword-frontend/settings/pages |

> ⚠️ **用户名注意**：GitHub 用户名是 `minziqian48-sudo`（连字符），不是 `minzjqian48.sudo`（点号）。`API_BASE` 和 `APP_URL` 里的地址务必用连字符版本。

---

## 2. 设计系统：温暖米色调（当前主题）

### 2.1 主应用 `Lexiword.html` 的 `:root` 设计令牌（2026-07-06 重构）

```css
:root {
  --bg:          #FBF7F0;   /* 暖米白背景 */
  --surface:     #FFFFFF;   /* 卡片/表面 */
  --surface-2:   #F5F1E8;   /* 次级表面（输入框/标签栏） */
  --surface-3:   #EDE8DC;   /* 三级表面 */
  --border:      rgba(180,150,110,.15);   /* 边框（焦糖棕透明） */
  --border-s:    rgba(180,150,110,.30);   /* 强边框（聚焦） */
  --ink:         #3D3428;   /* 主文字（暖棕黑） */
  --ink-2:       #6B5D4D;   /* 次文字 */
  --ink-3:       #9E9182;   /* 弱文字（占位/说明） */
  --accent:      #C4956A;   /* 焦糖棕主强调色 */
  --accent-2:    #A67B4F;   /* 深焦糖（渐变收尾/激活） */
  --accent-lt:   rgba(196,149,106,.12);  /* 浅强调底 */
  --accent-glow: rgba(196,149,106,.20);  /* 按钮光晕 */
  --s2-bg:#FDF0EF; --s2-bd:#D4756A; --s2-ink:#B04035;  /* 状态2：未掌握（红） */
  --s3-bg:#EFF5E8; --s3-bd:#5FA05C; --s3-ink:#3D723A;  /* 状态3：已掌握（绿） */
  --r-xs:8px; --r-sm:12px; --r-md:16px; --r-lg:22px; --r-xl:28px;
  --nav-h:60px; --topbar-h:56px; --sidebar-w:290px;
  --sh-xs: 0 1px 3px rgba(61,52,40,.05), 0 1px 2px rgba(61,52,40,.03);
  --sh-sm: 0 4px 12px rgba(61,52,40,.07);
  --sh-md: 0 8px 24px rgba(61,52,40,.10);
  --sh-lg: 0 20px 48px rgba(61,52,40,.14);
  --ease:   cubic-bezier(.4,0,.2,1);
  --spring: cubic-bezier(.34,1.56,.64,1);  /* 弹性动画曲线 */
  --sat: env(safe-area-inset-top, 0px);    /* 刘海屏安全区 */
  --sab: env(safe-area-inset-bottom, 0px);
}
[data-theme="dark"] {
  --bg:          #1A1816;   /* 深暖棕背景 */
  --surface:     #252220;
  --surface-2:   #2E2A26;
  --surface-3:   #383330;
  --border:      rgba(180,150,110,.12);
  --border-s:    rgba(180,150,110,.22);
  --ink:         #EDE6DB;
  --ink-2:       #B0A394;
  --ink-3:       #7A6E62;
  --accent:      #D4A57A;   /* 暗色模式主强调（更亮的焦糖） */
  --accent-2:    #B8875A;
  --accent-lt:   rgba(212,165,122,.12);
  --accent-glow: rgba(212,165,122,.18);
  --s2-bg:#3A202F; --s2-bd:#E07060; --s2-ink:#FF9090;
  --s3-bg:#1E2E1A; --s3-bd:#5FA05C; --s3-ink:#80D080;
}
```

### 2.2 单词卡片 4 种状态（CSS `data-state` 属性）

| 状态值 | 含义 | 背景 | 左边框 |
|--------|------|------|--------|
| `0` | 未标记 | `var(--surface)` 白 | `--border` 浅 |
| `star` | 星标 | `var(--surface)` 白（**无底色**） | 金色 `3px solid #F0A020` |
| `2` | 未掌握 | `#FCEBEB` 红底 | `#E24B4A` 红 |
| `3` | 已掌握 | `#EAF3DE` 绿底 | `#639922` 绿 |

> **重要视觉规则**：星标（`star`）**只有金色左边框、无背景色**；只有"未掌握(红)/已掌握(绿)"有底色。这是用户明确要求的（"星标不需要背景颜色，只有红绿两种背景颜色"）。

### 2.3 登录页 `login.html` 的 `:root`（同步对齐）

```css
:root {
  --bg: #FBF7F0; --surface: #FFF; --surface-2: #F5F0E8;
  --border: rgba(196,149,106,.12); --border-s: rgba(196,149,106,.28);
  --ink: #333333; --ink-2: #666666; --ink-3: #999999;
  --accent: #C4956A; --accent-2: #D4A574; --accent-lt: #FBF0E5;
  --accent-glow: rgba(196,149,106,.20);
}
[data-theme="dark"] {
  --bg:#1A1816;--surface:#242220;--surface-2:#2D2926;
  --border:rgba(196,149,106,.14);--border-s:rgba(196,149,106,.26);
  --ink:#EDE8E1;--ink-2:#B0A89C;--ink-3:#787068;
  --accent:#D4A574;--accent-2:#E0B88A;--accent-lt:rgba(212,165,116,.14);
}
```

### 2.4 已知不一致（详见第 15 节）

根目录 `manifest.json` 的 `background_color`/`theme_color` **仍是旧蓝紫色**（`#F0F2FA` / `#4C52E8`），未随主题重构更新。当前 PWA 安装时启动画面会短暂闪蓝。应在发布前改为 `#FBF7F0` / `#C4956A`。

---

## 3. 文件清单（当前真实状态）

```
D:\project\Lexiword\
│
├── 📄 核心前端（必须保留，已 Git 跟踪）
│   ├── Lexiword.html          ← 主应用 SPA（约 4221 行, ~625KB）★ 核心
│   ├── login.html             ← 登录页（266 行, 11KB）★ 核心（已暖色化）
│   ├── manifest.json          ← PWA 清单（注意：仍是旧蓝紫色，见 §15）
│   ├── sw.js                  ← Service Worker（CACHE_NAME=lexilearn-v5）
│   ├── favicon.png            ← 浏览器图标
│   ├── icon-192.png           ← PWA 图标 192px
│   ├── icon-512.png           ← PWA 图标 512px
│   └── icon-512-maskable.png  ← PWA 自适应图标
│
├── 📄 文档
│   ├── CHANGELOG.md           ← 详细改动日志 ✅ 保留
│   ├── LexiLearn-Knowledge-Base.md ← 知识库/踩坑记录 ✅ 保留（部分内容已过期，以本手册为准）
│   ├── LexiLearn-完整操作手册.md ← 本手册 ✅
│   └── overview.md            ← AI 临时概述（可删）
│
├── 📂 backend/                ← 早期 Render 备份版（独立 git 仓库，已弃用）
│   └── app.py / schema.sql / requirements.txt / render.yaml / venv/
│
├── 📂 deploy_backend/         ← PythonAnywhere 实际部署版本 ★ 权威后端
│   ├── app.py                 ← Flask 后端完整版（约 650 行）★ 实际运行的就是它
│   ├── app_full.py            ← 含内嵌词库数据的完整版（6268 行，480KB）⚠️ 大文件
│   ├── schema.sql             ← 数据库建表 SQL
│   └── requirements.txt
│
│   ⚠️ **重要**：`.gitignore` 已忽略 `backend/` 和 `deploy_backend/`，
│      即**后端代码不在 GitHub 仓库中**！它只存在于：
│      ① PythonAnywhere 的 /home/minziqian48/app.py（线上运行版）
│      ② 本地 D:\project\Lexiword\deploy_backend\（开发版）
│      从零重建时，后端不能从 git 拉取，必须单独上传到 PythonAnywhere（见 §13.2 / §14 Step 2）。
│
├── 📂 dist/                   ← 旧版构建输出 ⚠️ .gitignore 已忽略，勿依赖
│   ├── index.html             ← 562KB 旧版（2026-07-05，未更新）
│   └── login.html             ← 10.6KB（2026-07-07 曾手动同步过，但非权威）
│
├── 🔧 一次性脚本（已执行完，可归档/删除）
│   ├── build_app.py           ← 词库注入脚本
│   ├── extract_daybook.py     ← 从 SPA 提取词库
│   └── daybook_data.py        ← 提取出的词库数据（434KB 中间产物）
│
├── 🔐 SSL 证书（⚠️ 已从仓库删除，见 git 历史 26466ca）
│   ├── lexilearn.crt / lexilearn.key / lexilearn.pem  ← 已移出仓库
│
├── 📦 工具
│   └── uber-apk-signer.jar    ← APK 签名工具（已从仓库删除）
│
├── 📝 .gitignore              ← 忽略 dist/、*.key、*.jar、__pycache__ 等
└── Lexiword.html.backup       ← 2026-07-06 重构前原版备份（3957 行），可一键回退
```

### HBuilderX 项目（APK 壳）

```
D:\data\HBuilderProjects\LexiLearn\
├── index.html          ← APK 壳入口（plus 检测 + 加载线上 URL + 原生桥接）
├── manifest.json       ← 应用清单（version 1.2, code 120）
└── img/
    ├── icon.png / icon-mdpi.png / icon-hdpi.png / icon-xhdpi.png
    ├── icon-xxhdpi.png / icon-xxxhdpi.png   ← 各密度 APK 图标
    ├── icon-192.png / icon-512.png          ← PWA/iOS 图标
    └── icon-source-1024.png                 ← 卡通猫图标 1024 原图（⚠️ 带 AI 水印）
```

---

## 4. 技术架构

### 系统全景

```
┌─────────────────────────────────────────────────────────────┐
│                        用户设备                               │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ 手机浏览器    │   │ PC 浏览器     │   │ HBuilderX APK  │  │
│  │ (PWA 离线)   │   │ (GitHub Pages)│  │ (WebView 壳)   │  │
│  └──────┬───────┘   └──────┬───────┘   └───────┬────────┘  │
│         └───────────┬───────┘────────────────────┘          │
│                     ▼                                       │
│              ┌─────────────────┐                            │
│              │ Lexiword.html   │ ← 主 SPA (4081行)          │
│              │ login.html      │ ← 登录页 (267行)           │
│              │ sw.js           │ ← Service Worker          │
│              └────────┬────────┘                            │
│                       │ fetch()  HTTPS                      │
└───────────────────────┼─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    PythonAnywhere                            │
│              ┌──────────────────────┐                        │
│              │   Flask (app.py)      │                        │
│              │   SQLite (db.sqlite)  │                        │
│              └──────────┬───────────┘                        │
│  /auth/* 注册/登录/JWT    /states/* 学习状态   /backup/* 备份 │
│  /checkin/* 打卡          /sets/* 集合         /pins/* 置顶  │
│  /star/* 收藏             /bookmark/* 单书签     /daybook 5560词│
└─────────────────────────────────────────────────────────────┘
                        ▲
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Pages                              │
│  Repository: lexiword-frontend (branch: main)                │
│  URL: minziqian48-sudo.github.io/lexiword-frontend           │
└─────────────────────────────────────────────────────────────┘
```

### 数据流：打卡/改状态 → 持久化

```
用户点击单词卡片改状态
   │
   ▼ dbSetState(day, word, s)
   ├─ 1. 写入内存 localCache.states[key] = s
   ├─ 2. apiFetchSilent('PUT','/states/'+day+'/'+word, {state:s})  → 服务器
   │       └─ 失败? → showToast('⚠️ 状态保存失败')（不再吞错）
   └─ 3. 渲染卡片底色（红/绿/星标金色边）
   
退出登录 → doLogout() → _saveAccountSnapshot(用户ID)
   ├─ 收集 localCache 全部数据 → JSON → localStorage['lexi_snap_'+ID]
   ├─ 配额溢出? → 降级只存 states+starred+checkin → 还溢出? → 放弃(靠服务器)
   └─ 清本地业务数据（保留 lexi_snap_*、lexi_accounts、lexi_last_user）

重新登录 → login.html clearOldAppData()（保留 lexi_snap_* 快照！）
   ↓ 进入 Lexiword.html
   └─ _restoreAccountSnapshot() → 恢复快照 → initData() 合并服务器数据
       └─ 若"本地有数据但服务器空" → _reSyncLocalToServer() 主动回传
```

---

## 5. 后端 Flask API

**权威文件**：`deploy_backend/app.py`（部署到 PythonAnywhere 的 `/home/minziqian48/app.py`）。

### 5.1 环境变量与配置

- `API_BASE`（前端常量）= `https://minziqian48.pythonanywhere.com/api`
- JWT：PyJWT 签发，`exp` 30 天
- 密码：bcrypt 哈希
- CORS：手动 `before_request` 处理 OPTIONS 预检 + `after_request` 补头（**不用 flask_cors**，PythonAnywhere 上不兼容）

### 5.2 路由清单

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/health` | 健康检查 → `{"ok":true,"time":<unix时间戳>}` |
| POST | `/api/auth/register` | 注册（bcrypt） |
| POST | `/api/auth/login` | 登录（返回 JWT） |
| GET | `/api/auth/me` | 当前用户（token → user_id） |
| GET | `/api/daybook` | 公开：全部 5560 单词 |
| GET | `/api/states` | 学习状态（states + starred + visit_days） |
| PUT | `/api/states/<day>/<word>` | 更新单词语状态 |
| POST | `/api/states/<day>/<word>/cycle` | 循环切换状态 |
| PUT | `/api/states/batch` | 批量更新 |
| GET | `/api/checkin` | 打卡记录 |
| POST | `/api/checkin` | 提交打卡 |
| GET | `/api/sets` | 词汇集列表 |
| POST | `/api/sets` | 创建集合 |
| PUT | `/api/sets/<id>` | 更新集合 |
| DELETE | `/api/sets/<id>` | 删除集合 |
| POST | `/api/sets/sync` | 同步集合 |
| GET | `/api/pins` | 置顶书签 |
| PUT | `/api/pins` | 保存置顶 |
| POST | `/api/pins/toggle` | 切换置顶 |
| PUT | `/api/star/<word>` | 收藏/取消 |
| POST | `/api/starred` | 批量星标（回传用） |
| GET | `/api/bookmark` | 获取**单**书签 `{"word": "..."}` |
| PUT | `/api/bookmark` | 设置**单**书签 `{word: "..."}` |
| GET | `/api/meanings/<word>` | 自定义释义 |
| PUT | `/api/meanings/<word>` | 设置释义 |
| POST | `/api/meanings/batch` | 批量释义 |
| GET | `/api/backup` | 导出备份 |
| POST | `/api/restore` | 导入恢复 |

### 5.3 数据库表（`schema.sql`）

```
users            (id, email, password_hash, nickname, created_at)
word_states      (user_id, day, word, state, updated_at)  UNIQUE(user_id,day,word)
checkin_records  (user_id, date, created_at)              UNIQUE(user_id,date)
starred_words    (user_id, word)                          UNIQUE(user_id,word)
word_sets        (id, user_id, name, words JSON, created_at, updated_at)
pinned_bookmarks (user_id, id)
vocab_bookmark   (user_id PRIMARY KEY, word)   ← ⚠️ 仅单书签字段
custom_meanings  (user_id, word, meaning, updated_at)     UNIQUE(user_id,word)
daybook_words    (day, word, meaning)          UNIQUE(day,word)
visit_records    (user_id, day, visited_at)
```

> ⚠️ **书签后端限制**：`vocab_bookmark` 表只有**一个 `word` 字段**（`user_id` 是主键）。即后端只存"最后一个书签"。前端多书签数组同步到服务器时，只上传数组**最后一个**词（`saveBMs` 里 `apiFetchSilent('PUT','/bookmark',{word: arr[arr.length-1]})`）。**多书签的完整性依赖本地 localStorage**，换设备/清缓存后只能恢复最后一个书签。详见 §8、§15。

### 5.4 词库数据

5560 个单词硬编码进 `app_full.py` 的 `seed_daybook()`（28 天）。`app.py` 精简版不含词库，部署时必须用 `app_full.py` 覆盖 `app.py`，或确保 `seed_daybook` 已含完整数据。

---

## 6. 前端主应用 Lexiword.html

约 4244 行，单文件 SPA。结构区段（行号随版本浮动，以当前为准）：

| 区段 | 内容 |
|------|------|
| 1–~66 | HTML `<head>` + `:root` 设计令牌（暖米色） |
| ~67–~1240 | 全部 CSS（卡片/动画/暗色/滑轨/书签条/弹窗） |
| ~1240–~1700 | SVG 图标 `<defs>`（Lucide 风格线性图标：`ic-bookmark` `ic-save` `ic-copy` `ic-check` `ic-list` 等） |
| ~1700–~1990 | API 封装：`apiFetch` / `apiFetchSilent` / `apiPost`；`API_BASE` 常量；`localCache` 数据结构；状态切换 `dbSetState()` |
| ~1990–~2900 | 词库渲染、集合页、大纲词详情、打卡 Hero、状态切换 UI |
| ~2900–~3425 | 备份/快照/导出收集（`_collectBackupData` `doExportFile` `doExportShare` `doExportCopy`） |
| ~3426–~3528 | `initData()` 启动初始化（合并策略） |
| ~3492–~3528 | `_reSyncLocalToServer()` / `_restoreFromLocalStorage()`（离线兜底） |
| ~3599–~3863 | `_saveAccountSnapshot()` / `_clearLexiLocalStorage()`（快照管理） |
| ~3864–~4039 | 多账号切换/退出（`doLoginOther` `doLogout`）、事件绑定、调试面板 |
| ~4040–~4180+ | **书签系统 IIFE**（多书签数组 + 书签条渲染 + 跳转） |
| 其余 | 初始化入口（DOMContentLoaded）、滚动滑轨 IIFE（~3082 起） |

### 6.1 API 兼容层（关键防御）

```javascript
const API_BASE = 'https://minziqian48.pythonanywhere.com/api';
async function apiFetch(method, path, body) {
    const cleanPath = path.replace(/^\/api\//, '/');  // ★ 自动去重 /api/ 前缀
    const url = API_BASE + cleanPath;
    // ... fetch + Authorization: Bearer <token>
}
```
即使 CDN 缓存了旧版带 `/api/api/` 的路径，也能正确请求。调用一律用 `'/states'` 而非 `'/api/states'`。

### 6.2 单词状态切换

`dbSetState(day, word, s)`（~line 1778）：
```javascript
function dbSetState(day, word, s) {
  const key = day + ':' + word;
  localCache.states[key] = parseInt(s);
  apiFetchSilent('PUT', '/states/'+day+'/'+encodeURIComponent(word), {state:s})
    .then(function() { /* 成功：静默即可 */ })
    .catch(function(err) {
      console.warn('[STATE] save failed for', word, ':', err);
      showToast('⚠️ 状态保存失败，请检查网络', 2500);
    });
}
```

### 6.3 集合页搜索栏统一

集合页（`view-sets`）的搜索框使用全局 `.search-wrap` 样式，与词库页搜索栏视觉一致。集合页**不显示**单词状态筛选标签、不显示横条书签（用户要求精简）。

---

## 7. 登录页 login.html

267 行，独立文件。当前已暖色化（§2.3）。

### 关键逻辑

```javascript
const API_BASE = 'https://minziqian48.pythonanywhere.com/api';

// ★ 登录前清旧数据，但保留快照（防数据丢失的核心修复）
function clearOldAppData() {
  const prefixes = ['lexi_','wrev3_','checkin_'];
  const keep = ['lexiword_token','lexi_accounts'];
  const keepPrefixes = ['lexi_snap_','lexi_snap_em_'];  // ★ 快照必须保留
  for(let i=localStorage.length-1;i>=0;i--){
    const k=localStorage.key(i);
    if(k && prefixes.some(p=>k.startsWith(p)) && !keep.includes(k) && !keepPrefixes.some(p=>k.startsWith(p))){
      localStorage.removeItem(k);
    }
  }
}

async function doLogin() {
  // ... 验证 ...
  // 记住账号到 lexi_accounts（最多 5 个）
  clearOldAppData();              // ★ 清旧数据（保留快照）
  setToken(data.token);
  window.location.href = 'Lexiword.html?_t=' + Date.now();  // ★ cache-buster
}
```

- **自动登录**：`<script>` 顶部检测 `lexiword_token`，有则直接 `location.replace('Lexiword.html?_t='+Date.now())`，避免登录页闪现。
- **暗色切换**：`toggleDark()` 写 `lexilearn_dark` 到 localStorage。
- **logo-mark**：📖 emoji（登录页未用卡通猫图标，主应用图标才是猫）。

---

## 8. 书签系统（前端多书签 / 后端单书签）

### 8.1 数据模型

`localCache` 中书签相关字段：
```javascript
const localCache = {
  states:{}, starred:[], checkin:{}, sets:[], pins:{},
  bookmark:'',            // 旧单书签字段（遗留兼容）
  visitDays:{}, meanings:{},  // 访问记录 + 自定义释义
  bookmarks_vocab: [],     // 词库多书签数组（最多 10）
  bookmarks_db: [],        // 大纲词多书签数组（最多 10）
};
```

localStorage 键：
| 键 | 内容 |
|----|------|
| `lexi_vocab_bookmark_v1` | 旧单书签（字符串） |
| `lexi_bookmarks_vocab_v2` | 词库多书签（JSON 数组） |
| `lexi_bookmarks_db_v2` | 大纲词多书签（JSON 数组） |

### 8.2 核心常量与函数（IIFE，约 §4041 起）

```javascript
const MAX_BM = 10;   // 每个板块最多 10 个书签
const BM_KEYS = { vocab: 'lexi_bookmarks_vocab_v2', db: 'lexi_bookmarks_db_v2' };

function getBMs(type){ return localCache['bookmarks_'+type]||[]; }
function addBM(type, word){          // 添加（去重 + 上限校验）
  const arr = getBMs(type);
  if(arr.includes(word)) return false;
  if(arr.length >= MAX_BM){ showToast('最多 '+MAX_BM+' 个书签'); return false; }
  arr.push(word); saveBMs(type); showToast('已添加书签：'+word);
}
function removeBM(type, word){ ... }       // 移除
function toggleBM(type, word){ ... }       // 切换
function saveBMs(type){                     // 存 localStorage + 同步服务器（仅最后一个）
  localStorage.setItem(BM_KEYS[type], JSON.stringify(arr));
  apiFetchSilent('PUT','/bookmark',{word: arr.length?arr[arr.length-1]:''});
  renderBookmarkBar(type); refreshCardMarks(type);
}
```

### 8.3 UI 表现

- **书签条**（`bm-bar`）：渲染在搜索栏下方，横向 chip 列表，显示 `书签(N)` + 每个词的 chip（点击跳转、× 移除）。
- **卡片书签按钮**（`vocab-bm-btn`）：每张单词卡片左上角注入书签图标按钮，激活态高亮。
- **跳转**：`window._jumpBM(type, word)` 平滑滚动到目标卡片并闪动高亮（`bookmark-flash` 动画）。
- **两个板块独立**：`vocab`（词库）和 `db`（大纲词详情）各自一套书签数组、各自书签条、互不干扰。
- **入口**：词库页在 `#vocab-grid` 容器；大纲词详情页在 `#view-daybook-detail` 容器。

> 移除旧版"右侧大 rail 按钮 + 横条书签"设计，改为紧凑 chip 栏（用户 2026-07-06 要求：书签 UI 太突兀、只能一个、位置要美观）。

---

## 9. 数据持久化与多账号隔离

### 9.1 多账号隔离设计

每个业务数据 localStorage 键带 `user_id` 前缀或独立快照。账号间切换通过**快照机制**：

- **切换账号** `doLoginOther()`：
  1. `_saveAccountSnapshot(当前ID)` → 收集数据 → `localStorage['lexi_snap_'+ID]`
  2. `_clearLexiLocalStorage(false, true)` → 删 `lexi_db_/wrev3_/checkin_/lexi_ci_/lexi_sets_/lexi_pin_/lexi_bookmarks_*/...`（**保留** `lexi_snap_*`、`lexi_accounts`、`lexi_last_user`）
  3. 设 `lexi_switching='1'` → 跳 `login.html`

- **登录页** `doLogin()`：`clearOldAppData()`（保留 `lexi_snap_*` 快照）→ 跳主应用。

- **主应用启动** `_restoreAccountSnapshot(userID)`：
  - 若 `lexi_switching==='1'` 或 `lexi_last_user !== 当前ID` → 强制切换模式
  - 读 `lexi_snap_当前ID` → 写入 localStorage → merge
  - 无快照 → `GET /states` 从服务器拉

### 9.2 initData 合并策略（2026-07-07 修复核心）

```javascript
async function initData() {
  // 1. 先备份快照已恢复的数据
  const _snapStates = {...localCache.states};
  const _snapStarred = localCache.starred.slice();
  const _snapCheckin = {...localCache.checkin};
  const hadLocalData = Object.keys(_snapStates).length>0 || _snapStarred.length>0 || ...;

  // 2. 拉服务器
  const [states, checkin, sets, pins, bookmark] = await Promise.all([...]);

  // 3. ★ 合并：本地快照优先（用户最近操作），服务器补全
  localCache.states   = Object.assign({}, remoteStates, _snapStates);
  localCache.starred  = [...new Set([..._snapStarred, ...remoteStarred])];
  localCache.checkin  = Object.assign({}, remoteCheckin, _snapCheckin);
  localCache.sets     = sets.length ? sets : _snapSets;
  localCache.pins     = Object.keys(pins).length ? pins : _snapPins;
  localCache.bookmark = bookmark.word || '';

  // 4. ★ 若本地有数据但服务器空（之前同步失败）→ 主动回传
  if (hadLocalData && Object.keys(remoteStates).length===0) _reSyncLocalToServer();
}
```

### 9.3 登录后数据丢失 Bug 的根因与修复（2026-07-07）

**根因**：
1. `login.html` 旧 `clearOldAppData()` 前缀含 `'lexi_'` → 误删 `lexi_snap_*` 快照；
2. `initData()` 用空服务器数据**覆盖**了本地恢复的快照。

**修复**（已上线 `4685184`）：
- `clearOldAppData` 加 `keepPrefixes = ['lexi_snap_','lexi_snap_em_']` 保护快照；
- `initData` 改为**合并**而非覆盖；
- 新增 `_reSyncLocalToServer()`，本地有数据服务器空时主动回传。

---

## 10. 备份与分享功能

备份弹窗提供三个按钮：**下载文件** / **分享发送** / **复制 JSON**。

### 10.1 `doExportFile()` — 下载/原生保存

```javascript
function doExportFile(){
  const json = JSON.stringify(_collectBackupData().data, null, 2);
  const filename = 'LexiLearn_backup_' + new Date().toISOString().slice(0,10) + '.json';
  if (typeof plus !== 'undefined') {
    // ★ HBuilderX APK：通过壳的 _lexiExportBackup 原生桥接保存
    plus.webview.getLaunchWebview().evalJS('_lexiExportBackup(' + JSON.stringify(json) + ',' + JSON.stringify(filename) + ')');
  } else {
    _downloadBlob(new Blob([json], {...}), filename);  // 浏览器下载
  }
}
```

### 10.2 `doExportShare()` — 分享（四层适配）

| 层级 | 条件 | 行为 |
|------|------|------|
| ① | `typeof plus !== 'undefined'` | HBuilderX `plus.share.sendWithSystem({type:'file'})` → 系统分享面板（微信/QQ） |
| ② | `navigator.canShare({files:[blob]})` | Web Share API 文件分享（手机浏览器→微信） |
| ③ | `navigator.share` | Web Share API 文字分享（旧浏览器） |
| ④ | 都不支持 | 桌面 fallback → `doExportFile()` 下载 |

### 10.3 `doExportCopy()` — 复制 JSON

`_safeCopy(json, onSuccess, onFail)` 写入剪贴板，按钮显示"已复制"反馈。

### 10.4 HBuilderX 原生桥接 `index.html` 中的 `_lexiExportBackup`

壳页面 `window._lexiExportBackup = function(json, filename){...}` 用 `plus.io` 写 `_downloads/` 或 `_doc/`，再 `plus.share.sendWithSystem` 分享。详见 §12。

---

## 11. 自定义滚动滑轨

**目标**：真实反映滚动位置的自定义滑轨（非浏览器原生会"跳"的 scrollbar）。

### 11.1 HTML（主应用 `#page-area` 前）

```html
<div class="scroll-rail-wrap" id="scrollRail">
  <div class="scroll-rail-track"><div class="scroll-rail-thumb" id="scrollThumb"></div></div>
</div>
```

### 11.2 CSS（§737 起）

```css
.scroll-rail-wrap{ position:fixed; right:4px; top:calc(...); bottom:...; width:4px; z-index:60; pointer-events:none; opacity:0; transition:opacity .3s; }
.scroll-rail-wrap.visible{opacity:1;}
.scroll-rail-track{width:4px;height:100%;background:var(--border);border-radius:2px;position:relative;overflow:hidden;}
.scroll-rail-thumb{position:absolute;left:0;width:4px;border-radius:2px;background:var(--accent);min-height:24px;transition:top .1s linear;}
.scroll-rail-thumb:active{background:var(--accent-2);width:5px;box-shadow:0 0 8px rgba(196,149,106,.4);}
```

> 同时隐藏原生 scrollbar：`#page-area{ ... overflow-y:auto; ... }` 配合 `scrollbar-width:none`（或 Webkit 伪类隐藏），避免双轨。

### 11.3 JS 逻辑（§3082 起）

- `update()`：计算 `thumbTop = (scrollTop/(scrollHeight-clientHeight)) * (trackH - thumbH)`，`thumbH = max(24, clientHeight/scrollHeight * trackH)`。
- **RAF 节流**滚动监听（60fps）；停止滚动 1.2s 后淡出。
- **拖拽**：`onDragStart/Move/End` 支持鼠标 + 触摸，反算 `scrollTop = (y/maxTop)*(scrollHeight-clientHeight)`。
- 全页面长列表（词库/集合/大纲词）均生效。

---

## 12. HBuilderX 原生壳与 APK

### 12.1 壳页面 `index.html`（D:\data\HBuilderProjects\LexiLearn\index.html）

**三保险 plus 检测**（解决"启动失败/请在 5+App 环境运行"问题）：

```javascript
function openApp(){
  const wv = plus.webview.create(APP_URL, 'lexilearn-main', {/* 全屏, bounce:none */});
  wv.addEventListener('loaded', ()=> loading.off());
  wv.show();
  // ★ 暴露原生文件保存桥接
  window._lexiExportBackup = function(json, filename){
    plus.io.resolveLocalFileSystemURL('_downloads/', tryWrite, fallback);
  };
}
// 方式1: plusready 事件
document.addEventListener('plusready', ()=> openApp());
// 方式2: 100ms 轮询（最多 50 次=5秒）
var _poll = setInterval(()=>{ if(tryOpenApp()) clearInterval(_poll);
  else if(_plusChecks>=50){ /* 超时=普通浏览器 → iframe 加载线上页（调试用） */ } }, 100);
// 方式3: 立即尝试
tryOpenApp();
```

- `APP_URL` = `https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html?_t=Date.now()`（带 cache-buster 破 WebView 缓存）。
- **智能双模式**：有 `plus` → 原生 WebView 加载（分享/保存可用）；无 `plus`（HBuilderX 内置浏览器）→ 5 秒后 iframe 加载线上页（开发预览用，分享功能不可用）。
- 加载页 `#loading` 配色：`background:#FBF7F0`，spinner `border-top-color:#C4956A`（暖色）。

### 12.2 应用图标 🐱

**卡通白猫读书**图标（AI 生成，2026-07-07）。已生成 9 种尺寸到 `img/`：
`icon.png`(72) `icon-mdpi`(48) `icon-hdpi`(72) `icon-xhdpi`(96) `icon-xxhdpi`(144) `icon-xxxhdpi`(192) `icon-192`(192) `icon-512`(512) + `icon-source-1024`(原图)。

> ⚠️ **图标水印**：`icon-source-1024.png` 带"图片由AI生成"水印，会透到各尺寸。正式发布前建议用无水印图重新生成（见 §15）。

### 12.3 manifest.json（HBuilderX）

- `version.name: "1.2"`, `code: "120"`
- `launch_path: "index.html"`
- `permissions` 含 `Share`/`Storage`/`Downloader`/`File`/`Webview` 等（分享/保存必需）
- `plus.distribute.google.packagename: "plus.H5BE038E0"`
- 图标指向 `img/icon-*.png`

### 12.4 云打包流程

```
HBuilderX → 发行 → 原生App-云打包 → Android → 公共测试证书 → 打包
→ 下载 APK → 手机安装
```
- 打包后 APK 内是**代码快照**，不自动更新；前端改动需重新打包。
- 若分享模块缺失弹窗：manifest.json 可视化界面勾选 Share 模块权限后重打包。

---

## 13. 部署流程（三端）

### 13.1 前端 → GitHub Pages

```bash
cd D:\project\Lexiword
git add Lexiword.html login.html        # 注意 dist/ 被 .gitignore 忽略
git commit -m "feat/fix: ..."
git push origin main                    # ⚠️ 国内需开 VPN（连 GitHub）
```
推送后 GitHub Pages 自动部署（Settings → Pages 看 Last deployed）。CDN 同步 5–30 分钟。

### 13.2 后端 → PythonAnywhere

```
① 登录 pythonanywhere.com（minziqian48）
② Files → /home/minziqian48/ → 上传 app_full.py，重命名为 app.py
   （或编辑器中 Ctrl+A 清空 → 粘贴新代码 → Save）
③ Web 标签 → Reload（绿色按钮）
④ 验证：curl https://minziqian48.pythonanywhere.com/api/health
```

### 13.3 原生 → HBuilderX 云打包

见 §12.4。壳页面 `index.html` 已加载线上 URL，所以前端更新后**无需重新打包**即可在 APK 中看到（除非改了壳本身或图标）。

---

## 14. 从零重建步骤（提示词 + 命令）

> 目标：任何人/AI 按此流程可从零重建当前运行状态的项目。仓库已存在，重建 = 拉取 + 部署 + 配置。

### Step 1 — 拉取代码

```
① 克隆：git clone https://github.com/minziqian48-sudo/lexiword-frontend.git
② 或本地已有：cd D:\project\Lexiword && git pull origin main
③ 确认 HEAD = 4685184（git log -1）
```

### Step 2 — 部署后端（PythonAnywhere）

**提示词示例（给 AI/自己）**：
> "把 D:\project\Lexiword\deploy_backend\app_full.py 部署到 PythonAnywhere 账户 minziqian48 的 /home/minziqian48/app.py，确保 seed_daybook() 含全部 5560 词；在 Web 标签 Reload；验证 /api/health 返回 ok。"

手动步骤见 §13.2。依赖：`pip install flask bcrypt pyjwt`。

### Step 3 — 前端已自动部署（GitHub Pages）

推送即部署。验证：`curl -s "https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html" | grep -c "C4956A"` 应 > 0（确认暖色主题已上线）。

### Step 4 — 配置 HBuilderX（APK 壳）

1. 安装 HBuilderX → 导入/新建 5+App 项目到 `D:\data\HBuilderProjects\LexiLearn\`
2. 放入 `index.html`（§12.1 逻辑）、`manifest.json`（§12.3）、`img/`（§12.2 图标）
3. 云打包（§12.4）

### Step 5 — 若需从零"重做"前端（非拉取，而是 AI 生成）

> 给 AI 的核心提示词（浓缩本手册 §2 设计系统 + §6/§7/§8/§9/§10/§11 功能）：
> 
> "用纯 HTML/CSS/JS 单文件 SPA 做一个考研单词复习应用 LexiLearn。
> 视觉：温暖米色调，Design Token 见下——bg #FBF7F0、surface #FFF、accent #C4956A、ink #3D3428，暗色 bg #1A1816、accent #D4A57A；支持亮/暗主题切换。
> 功能：① 5560 词词库（28 天），4 种卡片状态（0 未标记 / star 星标金色边无底色 / 2 未掌握红底 / 3 已掌握绿底）；② 多账号登录（JWT，多账号数据隔离 + 快照机制）；③ 打卡、星标、词汇集；④ 多书签系统（词库/大纲词各自最多 10 个，独立数组，搜索栏下方紧凑 chip 栏）；⑤ 自定义滚动滑轨（真实位置 + 可拖拽 + RAF 节流，隐藏原生 scrollbar）；⑥ 备份弹窗：下载文件/分享发送（Web Share API + plus.share + 桌面 fallback）/复制 JSON；⑦ 后端 Flask API_BASE=https://minziqian48.pythonanywhere.com/api，apiFetch 自动去重 /api 前缀；⑧ 登录前 clearOldAppData 必须保留 lexi_snap_* 快照；initData 用合并策略（本地优先+服务器补全），本地有数据服务器空时主动回传；⑨ Service Worker lexilearn-v5 网络优先。"

> ⚠️ 实际项目中前端已存在（4081 行），无需重做；此提示词仅用于极端情况下的重建参考。

---

## 15. 已知问题与不一致项（必读）

| # | 问题 | 现状 | 建议 |
|---|------|------|------|
| 1 | **根 `manifest.json` 仍是旧蓝紫** | `background_color:#F0F2FA` `theme_color:#4C52E8`，PWA 安装闪蓝 | 改为 `#FBF7F0` / `#C4956A`（2 行） |
| 2 | **书签前端多 / 后端单** | 前端 `bookmarks_vocab/db` 数组最多 10；后端 `vocab_bookmark` 仅单 `word` 字段，同步只存最后一个 | 若要真正多书签云端同步，需改后端表为数组 + 新 API（当前靠本地 localStorage 保完整性） |
| 3 | **图标 AI 水印** | `icon-source-1024.png` 带"图片由AI生成"水印，透到各尺寸 | 正式发布前用无水印图重生成 9 尺寸 |
| 4 | **`lexi_vocab_bookmark_v1` 遗留字段** | 旧单书签字段仍读取兼容，新数据走 `bookmarks_vocab_v2` | 可逐步废弃，但保留读取以防旧备份 |
| 5 | **`dist/` 旧构建** | `dist/index.html` 是 2026-07-05 旧版，已被 .gitignore 忽略 | 忽略即可，不作为权威源 |
| 6 | **`backend/` 目录冗余** | 早期 Render 版，与 `deploy_backend/` 重复 | 可删除（deploy_backend 为权威） |
| 7 | **SSL 证书曾入库** | `lexilearn.key` 等已通过 `26466ca` 移出仓库 | 确认 .gitignore 含 `*.key *.pem *.crt`；如需彻底清除历史用 git filter-repo |
| 8 | **后端 `/starred` 路由缺失** | `_reSyncLocalToServer()` 调用 `POST /starred`（批量回传星标），但后端无此路由 → 404 被 `apiFetchSilent` 吞掉，星标回传走 `PUT /star/<word>` 单条路径才生效 | 低优先级；要么后端加 `/starred` 批量路由，要么前端改调已有单条接口 |
| 9 | **`_safeCopy()` 重复定义** | line 3206 和 line 3387 各有一个 `_safeCopy` 定义，第二个覆盖第一个（丢失 console.warn 日志）| 删除 line 3387–3396 的重复定义 |
| 10 | **`doExportCopy()` 重复定义** | line 2987 和 line 3375 各有一个 `doExportCopy` 定义，第二个覆盖第一个（toast 文案不同）| 删除 line 3375–3385 的重复定义 |

---

## 16. 常见问题排查

### Q1: 推送后 GitHub Pages 没更新？
CDN 同步 5–30 分钟。验证原始文件：`curl -s "https://raw.githubusercontent.com/minziqian48-sudo/lexiword-frontend/main/Lexiword.html" | grep C4956A`。加速：改 `sw.js` 的 `CACHE_NAME`（v5→v6）触发 SW 重装。

### Q2: 开 VPN 后 API 失败？
Clash/V2Ray 把 PythonAnywhere 请求转发错域名。解决：Clash Verge → 规则 → 前置直连：
```
DOMAIN-SUFFIX, pythonanywhere.com, DIRECT
DOMAIN-SUFFIX, github.io, DIRECT
```
日常使用**不需开 VPN**，GitHub Pages 和 PythonAnywhere 国内均可直连。

### Q3: APK 打开显示"请在 HBuilderX 5+App 环境中运行"？
旧版 `index.html` 用 `typeof plus` 一次判断，APK 中 plus 未注入完就走了错误分支。**已修复为三保险（plusready + 轮询 + iframe 兜底）**，重新打包即可。

### Q4: APK 打开显示"启动失败，请重启应用"？
HBuilderX **内置浏览器**（非真机/APK）无 `plus` 对象，5 秒后走 iframe 兜底加载线上页。属正常——在真机/模拟器/APK 中正常。

### Q5: 登录后打卡/状态丢失？
见 §9.3。已修复（`4685184`）。若仍丢失：检查 `clearOldAppData` 是否保留 `lexi_snap_*`；检查 `initData` 是否合并而非覆盖。

### Q6: 多书签只恢复了一个？
后端仅单书签字段（§15 #2）。换设备/清缓存后只能从服务器恢复最后一个；其余靠本地 localStorage。

### Q7: Console QuotaExceededError？
快照超 5MB 限额。`_saveAccountSnapshot` 已三级降级（全量→核心→放弃靠服务器），不丢数据。

---

## 17. 维护指南

### 每次修改前端后的标准流程

```
① 改 Lexiword.html / login.html
② git add + git commit（写清改了什么）
③ 开 VPN → git push origin main
④ 等 GitHub Pages 部署（Settings/Pages 看 Last deployed）
⑤ 无痕窗口开 ?t=随机数 验证
⑥ 如需手机原生能力变化 → HBuilderX 重新打包
```

### 安全待办

| 优先级 | 事项 |
|--------|------|
| 🔴 高 | 修复根 manifest.json 蓝紫色（§15 #1） |
| 🟡 中 | 重新生成无水印 APP 图标（§15 #3） |
| 🟡 中 | 书签后端多书签化（§15 #2） |
| 🟢 低 | 清理 backend/ 冗余目录、dist/ 旧文件 |
| 🟢 低 | 代码模块化（拆分 4081 行单文件） |

### 代码质量方向

1. 拆分 Lexiword.html 为模块 + 外部 CSS
2. 引入 Vite/esbuild（文件名 hash 解决缓存）
3. TypeScript 迁移
4. 单元测试（`_saveAccountSnapshot`/`_restoreAccountSnapshot`/`initData` 合并）
5. CI/CD：GitHub Actions 自动 Lighthouse 评分

---

## 附录 A：关键函数索引

| 函数 / 元素 | 文件 | 作用 |
|-------------|------|------|
| `apiFetch()` | Lexiword.html ~1707 | API 封装（含 /api 去重兼容层） |
| `dbSetState(day,word,s)` | Lexiword.html ~1778 | 更新单词状态（含 toast 反馈） |
| `initData()` | Lexiword.html 3426 | 启动初始化（合并策略 + 回传） |
| `_reSyncLocalToServer()` | Lexiword.html 3492 | 本地有数据服务器空时主动回传 |
| `_restoreFromLocalStorage()` | Lexiword.html 3529 | 离线兜底读 localStorage |
| `_saveAccountSnapshot(id)` | Lexiword.html ~3599 | 保存账号快照（三级降级） |
| `_clearLexiLocalStorage()` | Lexiword.html ~3724 | 清业务数据（保留快照/账号） |
| `doLoginOther()` | Lexiword.html ~3864 | 切换账号 |
| `doLogout()` | Lexiword.html ~3876 | 退出登录 |
| `doExportFile()` | Lexiword.html 3244 | 下载/原生保存备份 |
| `doExportShare()` | Lexiword.html 3298 | 四层分享 |
| `doExportCopy()` | Lexiword.html ~3375 | 复制 JSON |
| `toggleBM/addBM/removeBM` | Lexiword.html 4040+ | 多书签增删切换 |
| `renderBookmarkBar(type)` | Lexiword.html ~4094 | 渲染书签 chip 栏 |
| `window._jumpBM(type,word)` | Lexiword.html ~4151 | 跳转书签单词 |
| 滚动滑轨 JS IIFE | Lexiword.html ~3082 | 真实位置 + 拖拽 + RAF 节流 |
| `clearOldAppData()` | login.html 145 | 登录清旧数据（**保留 lexi_snap_***） |
| `doLogin()/doRegister()` | login.html ~193/~226 | 登录/注册 |
| `openApp()` / `_lexiExportBackup` | HBuilderX index.html | 壳加载 + 原生保存桥接 |
| `before_request` CORS | deploy_backend/app.py ~41 | OPTIONS 预检处理 |

---

## 附录 B：Git 提交历史摘要

当前 HEAD = `4685184`。最近关键提交：

```
4685184 fix: 修复登录后数据丢失问题（保护快照+合并策略+回传机制）   ★ 本轮
b0b1344 feat: 词库/集合页添加自定义滚动滑轨（真实位置+可拖拽+动态大小） ★ 本轮
d5a5408 fix: 登录页UI对齐温暖米色调（与主界面统一）                ★ 本轮
94d7b02 feat: UI全面重构 — 温暖米色调 + 多书签系统 + 分享功能        ★ 本轮
26466ca chore: 清理仓库 — 移除敏感文件/大文件/临时文件
25bc01a fix: 修复多账号数据隔离三大问题
e98757d fix: clearOldAppData 保留 lexi_accounts 账号列表
7037bb0 fix: apiFetch 自动去掉重复 /api 前缀
35e71da fix: 修复API路径+账号隔离+强制缓存刷新(v5)
e6b48eb fix: 修复 API 路径重复 /api 前缀导致的 404 错误
bdb4499 fix: 修复多账号数据隔离 — 登录前清旧数据 + 启动时检测用户变化
7ec7ce4 fix: apiFetchSilent 增加错误日志 + CORS诊断
```

---

*手册结束。本手册为 LexiLearn 项目唯一权威参考，任何重建/维护以本手册 + 当前 Git HEAD（4685184）为准。旧版《知识库》部分内容已过期，以本手册为准。*
