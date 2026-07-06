# LexiLearn 改动日志 🔧

> 每次修改都记录在此，包含「改了什么 / 为什么改 / 怎么恢复」。
> 配合 `git log` 可精确回退到任意版本。

---

## 2026-07-06 · 第五轮 (commit: 759e1ef)

### 🐛 修复：日历闪现

**现象**：切换/登录后，打卡页日历先折叠（空状态），过一会才显示完整数据。

**根因**：`_restoreAccountSnapshot` 在非切换模式下，异步批量循环空转。虽然每个 key 因已存在 localStorage 而被跳过（`if (!isSwitching && localStorage.getItem(k)) continue;`），但 8000+ 条目仍需 ~160 轮 `setTimeout(0)` 延迟，导致 3 秒超时先触发渲染空 UI。

**修复**：非切换模式直接调用 `_mergeLocalStorageIntoCache()` + `resolve()`，完全跳过空转循环。

### 🛡️ 修复：切换账号数据丢失（防御性安全网）

**现象**：切换账号后再切回，原账号数据全部丢失。

**防御措施**：
1. `doSwitchToAccount` 新增 email 键安全快照：无论 `_currentUser` 是否可用，始终从账号列表反查当前邮箱，额外保存 `lexi_snap_em_{email}` 快照
2. `_restoreAccountSnapshot` 新增 email 键回退：当 numeric ID 快照未找到时，自动从账号列表反查 email，尝试 email 键快照
3. 新增 `[SWITCH]` 调试日志追踪切换全过程

**恢复**：
```bash
git checkout 97e5a6a -- Lexiword.html
```

---

---

## 2026-07-06 · 第四轮 (commit: e07102b) 🔴 根因修复

### 🔴 修复：导入数据丢失（根本原因）

**问题**：导入备份后刷新页面，签到记录、生词本、书签、访问天数等数据消失。

**根因分析**：

`_mergeLocalStorageIntoCache()` 函数中，结构化数据的合并逻辑有严重缺陷：

```javascript
// ❌ 旧代码 — 有问题的逻辑
if(!Object.keys(localCache.checkin).length){  // 仅当 API 返回空时才合入！
  const ci=JSON.parse(localStorage.getItem('lexi_ci_v1')||'{}');
  if(Object.keys(ci).length) localCache.checkin = ci;
}
```

**数据流追踪**：
1. `_processImport()` 正确写入 localStorage ✅
2. 页面刷新 → `initData()` 从后端 API 获取数据
3. **后端返回哪怕一条数据** → `localCache.checkin` 非空
4. 条件判断为 false → **localStorage 中完整的导入数据被完全忽略** ❌

`states` 和 `starred` 无此问题（它们无条件覆盖），但 `checkin/sets/pins/bookmark/visitDays` 全部受影响。

**修复**：
```javascript
// ✅ 新代码 — localStorage 始终优先
const ci=JSON.parse(localStorage.getItem('lexi_ci_v1')||'{}');
if(Object.keys(ci).length) localCache.checkin = ci;
// 不再检查 API 是否为空，本地有数据就用本地的
```

| 文件 | 改动 |
|------|------|
| Lexiword.html | `_mergeLocalStorageIntoCache()` 移除所有 `!empty` 条件，改为始终从 localStorage 合并 |

**如何恢复此修改**：
```bash
git checkout f5af281 -- Lexiword.html
```

---

## 2026-07-06 · 第三轮 (commit: 9e96539)

### ✨ 新功能：快速切换账号 + 数据隔离

**需求**：底部"我的"面板增加"切换账号"，不同账号数据完全隔离，切回原账号数据不丢。

**实现机制 — 按账号 ID 做 localStorage 快照**：

```
切换账号时：存快照 → 清临时数据 → 跳转登录
登录时：    恢复快照 → API 加载 → 合并本地数据
退出登录时：清除全部（包括快照）
```

**改了什么**：

| 文件 | 位置 | 改动 |
|------|------|------|
| Lexiword.html | 变量 | 新增 `_currentUser` 存储当前用户信息 |
| Lexiword.html | 新函数 | `_saveAccountSnapshot(userId)` — 把当前 localStorage 存为 `lexi_snap_{userId}` |
| Lexiword.html | 新函数 | `_restoreAccountSnapshot(userId)` — 从快照恢复到 localStorage |
| Lexiword.html | 新函数 | `_clearGenericData()` — 只清临时数据，保留快照 |
| Lexiword.html | 新函数 | `doSwitchAccount()` — 切换账号入口 |
| Lexiword.html | profile-sheet | 新增"切换账号"按钮，标题显示当前邮箱 |
| Lexiword.html | `_processImport()` | 导入备份后：存快照 + 同步到后端 `/api/restore` |
| Lexiword.html | 启动代码 | 先调 `/api/auth/me` 存 `_currentUser`，再 `_restoreAccountSnapshot` |
| login.html | `doLogin()` | **移除** `clearOldAppData()` — 快照机制接管隔离 |

**如何恢复**：
```bash
git checkout 83013c5 -- Lexiword.html login.html
```

---

## 2026-07-06 · 第二轮修复 (commit: d864b09)

### 恢复：导入备份后数据显示 + 合集可用
**问题**：上一轮修多账号隔离时一刀切，`_mergeLocalStorageIntoCache()` 只合并 states/starred，漏了 sets/checkin/pins/bookmark。
导入备份后这四类数据躺在 localStorage 但从未被读入缓存。

**修改位置**：`Lexiword.html` → `_mergeLocalStorageIntoCache()` 函数（约第 3231 行）

**改了什么**：
- 原来只合并 `lexi_db_*` (states) 和 `wrev3_star_*` (starred)
- 新加了 checkin / sets / pins / bookmark / visitDays 的合并逻辑
- 每项只在 API 返回空时才从 localStorage 加载（安全，因为退出登录已清数据）

**如何恢复**：`git checkout 3bcd6ff -- Lexiword.html`（回到本轮第一版之前的状态）

---

## 2026-07-06 · 第一轮修复 (commit: e3dae30)

### 修复 1️⃣ 底部导航栏不固定
**问题**：在词库页滑动时底部 dock 栏跟着滚动，无法快速切换板块。

**根因**：`#bottom-nav` 用 flex 布局而非 `position:fixed`，HBuilderX WebView 中 flex 行为不可靠。

**修改位置**：`Lexiword.html` CSS 区域

**改了什么**：
```css
/* 原来 */
body { padding-top: var(--sat); }  /* 见修复2 */
#page-area { flex:1; overflow-y:auto; overflow-x:clip; }
#bottom-nav { display:flex; flex-shrink:0; }

/* 改为 */
body { /* 去掉 padding-top */ }
#page-area { ... /* 加上 */ padding-bottom: calc(var(--nav-h) + var(--sab)); }
#bottom-nav { ... /* 加上 */ position: fixed; bottom: 0; left: 0; right: 0; }
```

**如何恢复**：删掉 `position:fixed; bottom:0; left:0; right:0;` 三行，删掉 `padding-bottom:calc(...)`，恢复 `body{padding-top:var(--sat);}`

---

### 修复 2️⃣ App 顶部空白遮罩
**问题**：App 最上面有一块白色/灰色的空白区域（类似遮罩）。

**根因**：`body{padding-top:var(--sat)}` 在 HBuilderX WebView 中产生多余间隙。各页面 header 已经通过 `padding-top:calc(max(...))` 自行处理了安全区域。

**修改位置**：`Lexiword.html` 第 70 行

**改了什么**：
```css
/* 原来 */
body {
  ...
  padding-top: var(--sat);   /* ← 删掉这行 */
}

/* 改为：直接去掉 padding-top */
body {
  ...
  /* 无 padding-top */
}
```

**如何恢复**：在 `body{...}` 内加回 `padding-top:var(--sat);`

---

### 修复 3️⃣ 备份按钮卡死
**问题**：点击备份按钮后有概率界面卡住好几秒，啥都干不了。

**根因**：`_collectBackupData()` 同步扫描全部 localStorage + `JSON.stringify` 大数据 → 阻塞主线程。

**修改位置**：`Lexiword.html` → `openBackupModal()` 函数（约第 2877 行）

**改了什么**：
- **原来**：先 `_collectBackupData()` 采集数据，再显示弹窗 → 采集期间 UI 冻结
- **改为**：先立即显示弹窗（显示 spinner），再用 `setTimeout(50ms)` 异步采集数据
- 加了 `_cachedBackup` 全局缓存，`doExportCopy()` 和 `doExportFile()` 优先用缓存

**如何恢复**：
```js
// 把 openBackupModal 恢复成旧版
function openBackupModal(){
  const {count,data}=_collectBackupData();
  const json=JSON.stringify(data,null,2);
  const sizeKB=(new TextEncoder().encode(json).length/1024).toFixed(1);
  const info=document.getElementById('backup-export-info');
  if(info)info.textContent='共 '+count+' 条数据，约 '+sizeKB+' KB';
  document.getElementById('backup-import-text').value='';
  document.getElementById('backup-import-info').textContent='';
  document.getElementById('backup-modal-overlay').style.display='flex';
}
// 删掉 _cachedBackup 变量
```

---

### 修复 4️⃣ 打卡页/词库页首屏压缩
**问题**：打卡首页和词库首页需要向下滚动才能看到完整内容。

**修改位置**：`Lexiword.html` CSS 区域，多处

**改了什么（数值对照表）**：

| CSS 属性 | 旧值 | 新值 | 说明 |
|----------|------|------|------|
| `.ci-hero` padding | 28px 20px 22px | 20px 18px 16px | 打卡英雄区缩小 |
| `.ci-hero` margin-bottom | 18px | 12px | 英雄区下方间距 |
| `#ci-btn` width/height | 110px | 84px | 打卡按钮缩小 |
| `.ci-hero-date` margin-bottom | 16px | 10px | 日期区间距 |
| `.ci-hero-btn-wrap` margin-bottom | 16px | 10px | 按钮区间距 |
| `.ci-hero-title` font-size | 18px | 16px | 标题字号 |
| `.ci-stats-row` gap/margin | 10px/16px | 8px/10px | 统计卡片间距 |
| `.ci-stat-card` padding | 14px 10px | 10px 8px | 统计卡片内边距 |
| `.page-header` margin-bottom | 20px | 14px | 页面标题间距 |
| `.page-header` padding-top | max(sat,12)+4px | max(sat,10)+2px | 顶部安全区 |
| `.page-title` font-size | 24px | 22px | 页面标题字号 |
| `.view-page` padding-top | 16px | 12px | 页面顶部内边距 |
| `.log-panel` padding | 14px | 12px | 日历面板内边距 |
| `.state-filter` margin-bottom | 12px | 8px | 筛选栏间距 |
| `.filter-btn` padding | 7px 16px | 5px 13px | 筛选按钮尺寸 |
| `.sort-toggle-bar` margin-bottom | 10px | 6px | 排序栏间距 |
| `.detail-mode-bar` margin-bottom | 10px | 6px | 详情模式间距 |
| `.vocab-cn-mode-bar` margin-bottom | 10px | 6px | 中文模式间距 |

**如何恢复**：把上表「新值」全部改回「旧值」即可

---

### 修复 5️⃣ 🚨 多账号数据隔离（最严重 bug）
**问题**：用账号 A 登录后有数据，退出后用账号 B 登录，看到的是账号 A 的数据。

**根因分析**：
1. `initData()` 加载 API 数据后，发现某些模块为空 → 从 localStorage 兜底
2. 退出登录只清除了 token，没清除 localStorage 中的学习数据
3. 账号 B 登录后 API 返回空 → localStorage 还留着账号 A 的数据 → 被合并进缓存

**修改位置**：
- `Lexiword.html` → `initData()` 函数（约第 3172 行）
- `Lexiword.html` → `doLogout()` 函数（约第 3262 行）
- `login.html` → `doLogin()` 函数（约第 181 行）
- `login.html` → 新增 `clearOldAppData()` 函数

**改了什么**：

**(a) initData() — 不再在 API 成功时兜底 localStorage**
```js
// 原来：API 成功后还有个 try-catch 用 localStorage 填充空模块
// 改为：直接信任 API 返回，空就是空（配合退出清数据保证安全）

// 原来（已删除）：
try {
  if(!Object.keys(localCache.checkin).length) localCache.checkin = JSON.parse(localStorage.getItem('lexi_ci_v1')||'{}');
  // ... 等 5 个模块的兜底
} catch(e){}
```

**(b) doLogout() — 退出时清除所有本地数据**
```js
// 原来：只删 token
localStorage.removeItem('lexiword_token');

// 改为：删 token + 扫一遍所有 lexi_/wrev3_/checkin_/lexilearn_ 前缀的 key 全删
```

**(c) login.html clearOldAppData() — 登录前也清理**
```js
// 新增函数，切号登录时清除旧账号的本地残留数据
function clearOldAppData() {
  const prefixes = ['lexi_','wrev3_','checkin_'];
  for(let i=localStorage.length-1;i>=0;i--){
    const k=localStorage.key(i);
    if(k && prefixes.some(p=>k.startsWith(p))){
      localStorage.removeItem(k);
    }
  }
}
// 在 setToken() 之前调用
```

**如何恢复**（不推荐，会重新引入数据泄露）：
```bash
git checkout 3bcd6ff~ -- Lexiword.html login.html
```

---

## 2026-07-06 · 第四轮 (commit: d1442f8)

### ✨ 切换账号改为「记住的账号」点选

**之前**：点"切换账号"→ 跳到登录页 → 重新输入邮箱密码  
**现在**：点"切换账号"→ 弹出已登录过的账号列表 → 点一下就切过去

**改了什么**：

| 项目 | 说明 |
|------|------|
| `lexi_accounts` (localStorage) | 存 `[{email, token, lastLogin}]` 最多 5 个 |
| `_saveAccountToList()` | 登录时/启动时自动记住账号 |
| `_getAccountList()` | 读取已记住的账号列表 |
| `openAccountPicker()` | 弹出账号选择面板，显示邮箱+日期+"(当前)" |
| `doSwitchToAccount(email, token)` | 存快照→清临时→设 token→刷新 |
| `doLoginOther()` | "登录其他账号"选项 |
| `login.html` / 启动代码 | 登录/启动时自动保存账号 |
| 新增 HTML | `#account-picker` 面板 |
| `doLogout()` | 退出时保留 `lexi_accounts`（下次还能看到） |

**如何恢复**：
```bash
git checkout 9e96539 -- Lexiword.html login.html
```

---

## 2026-07-06 · 修复 (commit: 3f33540)

### 修复：切换账号列表显示 "undefined (当前)"

**问题**：账号选择面板第一个条目显示 `undefined (当前)`，但实际登录的是 1@qq.com

**根因**：
1. `lexi_accounts` 中存入了一条 email 为空的坏数据（早期版本写入）
2. `/api/auth/me` 返回的 user 对象在某些情况下缺少 email 字段
3. `_getAccountList()` 和 `_saveAccountToList()` 都没做防御性过滤

**改了什么**：
| 改动 | 说明 |
|------|------|
| `_getAccountList()` | 过滤掉 `!email \|\| !token` 的无效记录 |
| `_saveAccountToList()` | 入口校验，email/token 为空则不存 |
| 启动代码 | 加载前先清理一次 `lexi_accounts` 坏数据 |
| 启动代码 | 如果 `user.email` 为空，从已记住列表按 token 反查 |
| `openAccountPicker()` | 判断当前账号时优先用 token 匹配 |

**如何恢复**：`git checkout a3ec7fa -- Lexiword.html`

## 2026-07-06 · 修复 (commit: f6fa1b4)

### 修复 1️⃣ 切换账号后 App 完全卡死

**问题**：点切换账号后，界面卡在打卡页，一动也不能动。清缓存重来也一样。

**根因**：`_restoreAccountSnapshot()` 和 `_clearGenericData()` 在同一个同步调用栈里写了上千条 `lexi_db_*` 键到 localStorage，阻塞主线程数秒钟。

**修改位置**：`Lexiword.html`

**改了什么**：
```js
// _restoreAccountSnapshot() — 从同步全量写入改为分批异步
function _restoreAccountSnapshot(userId) {
  const entries = Object.entries(snap);
  const BATCH = 50;
  let i = 0;
  function writeBatch() {
    const end = Math.min(i + BATCH, entries.length);
    for (; i < end; i++) {
      const [k, v] = entries[i];
      if (!localStorage.getItem(k)) { localStorage.setItem(k, v); wrote = true; }
    }
    if (i < entries.length) setTimeout(writeBatch, 0); // yield to main thread
    else if (wrote) setTimeout(function() { _mergeLocalStorageIntoCache(); }, 50);
  }
  writeBatch();  // 每批 50 条，让出主线程
}

// _clearGenericData() — 同样分批，每批 30 条
```

**如何恢复**：`git checkout 3f33540 -- Lexiword.html`

---

### 修复 2️⃣ 登录页闪现

**问题**：每次打开 App，即使已经登录过，也要闪一下登录界面才跳转。

**根因**：HBuilderX 的 `index.html`（原生壳）始终先加载 `login.html`，然后才检测到 token → 重定向。

**修改位置**：`D:\data\HBuilderProjects\LexiLearn\index.html`

**改了什么**：
```js
// 原来：永远加载 login.html
var APP_URL = 'https://minziqian48-sudo.github.io/lexiword-frontend/login.html';

// 改为：有 token 直接进 Lexiword.html
var token = localStorage.getItem('lexiword_token');
var APP_URL = token
  ? 'https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html'
  : 'https://minziqian48-sudo.github.io/lexiword-frontend/login.html';
```

⚠️ HBuilderX 的 `index.html` 修改需要**重新云打包 APK** 才能生效。

**如何恢复**：把 `index.html` 改回始终加载 `login.html`。

---

### 预防 3️⃣ 启动时清除残留遮罩

**问题**：如果上次异常退出（崩溃/杀进程），页面可能残留 modal overlay 遮住 UI。

**改了什么**：
- 新增 `_closeAllOverlays()` 函数，枚举项目中所有可能的 overlay ID
- 在 `document.addEventListener('DOMContentLoaded', ...)` 启动时调用

**如何恢复**：删掉启动代码中的 `_closeAllOverlays()` 调用。

---

## 2026-07-06 · 修复 (commit: 0771fb5)

### 🔴 修复 1️⃣ 清数据后登录仍然卡死（最根本原因）

**问题**：清除 App 数据后重新登录，界面完全无法点击，一动也不能动。

**根因（致命）**：HTML 中存在**两个 `id="page-area"` 的元素**：
- 第一个在 1142 行，包裹 SVG 精灵图（`display:none`），但从未关闭
- 第二个在 1255 行，是实际的内容区域
- 两者嵌套在一起，都应用了 `overflow-y:auto` 的 CSS
- 在 HBuilderX WebView 中，外层不可见的滚动容器**吞噬了所有触摸事件**
- 导致内层所有按钮/链接完全收不到点击 → 界面看起来"卡死"

**修复**：将第一个 `id="page-area"` 改为 `id="svg-sprite"` 并补全关闭标签

```diff
- <div id="page-area" class="page-area">
+ <div id="svg-sprite">
  <svg ...>
  ...
  </svg>
+</div>   ← 新增：关闭 svg-sprite 容器
```

**如何恢复**：`git checkout f6fa1b4 -- Lexiword.html` （不推荐，会恢复 bug）

---

### 🔴 修复 2️⃣ 账号快照恢复完全失效

**问题**：切换账号后，原账号的数据永远无法从快照恢复。

**根因**：第 3318 行 `const snap = JSON.parse(snap)` 中变量名写错：
- `snap` 在赋值前就被引用 → `ReferenceError`
- 被 `try-catch` 静默吞掉 → 函数永远不执行任何操作

```diff
- const snap = JSON.parse(snap);   // snap 未定义！ReferenceError
+ const snap = JSON.parse(raw);    // 正确：解析原始字符串
```

**如何恢复**：改回 `JSON.parse(snap)`（不推荐）

---

### 🛡️ 新增 3️⃣ 启动安全网超时

**功能**：如果启动异步链（API → initData → switchNav）在 **3 秒内未完成**，强制渲染 UI。

**原因防御**：
- API 超时无响应
- 某个 `.then()` 内部抛出未被捕获的异常
- Promise 链中断但没触发 `.catch()`

```js
setTimeout(function() {
  if (!_startupDone) {
    _dataReady = true;
    switchNav(localStorage.getItem('lexi_last_view') || 'checkin');
  }
}, 3000);
```

---

## 2026-07-06 · 修复 (commit: f67f5b9)

### 修复：清数据后仍卡死 — 进一步排查

**问题**：修复重复 `id="page-area"` 后，清数据重新登录仍然无法点击。

**排查结果**：
1. `#svg-sprite` 容器虽然包着 `display:none` 的 SVG，但**容器本身没有显式隐藏**，仍可能拦截触摸事件
2. HBuilderX WebView 可能缓存了旧版页面

**修复内容**：
| 文件 | 改动 |
|------|------|
| `Lexiword.html` | `<div id="svg-sprite">` 改为 `<div id="svg-sprite" style="display:none">` |
| `HBuilderX/index.html` | APP_URL 追加 `?_t=Date.now()` 破坏 WebView 缓存 |
| `HBuilderX/index.html` | 添加 `Cache-Control: no-cache, no-store, must-revalidate` 等 meta |

**注意**：HBuilderX `index.html` 修改后**必须重新云打包 APK** 才能生效。

---

## 2026-07-06 · 修复 (commit: dd18ca8)

### 修复：浏览器验证也卡死 — 全面缓存破坏 + 调试面板

**问题**：用户反馈用浏览器直接验证（清数据 → 登录）仍然卡在打卡页无法点击。说明问题不在 HBuilderX WebView 缓存，而在页面本身或浏览器/SW 缓存了旧版。

**修复内容**：
| 文件 | 改动 |
|------|------|
| `login.html` | 登录/自动登录跳转改为 `Lexiword.html?_t=Date.now()`，破坏缓存 |
| `Lexiword.html` | 添加 no-cache meta tags |
| `login.html` | 添加 no-cache meta tags |
| `sw.js` | 缓存名 `lexilearn-v3` → `lexilearn-v4`，强制浏览器安装新 Service Worker |
| `Lexiword.html` | 顶部新增调试面板：全局错误捕获 + 启动流程日志 + 强制渲染按钮 |
| `Lexiword.html` | 启动 IIFE 各环节加 `_lexiDebugLog` 日志点 |

**用户如何验证**：
1. 清掉浏览器缓存/Service Worker（或直接用隐私模式/无痕窗口）
2. 打开登录页： `https://minziqian48-sudo.github.io/lexiword-frontend/login.html?_t=1`
3. 登录后观察顶部绿色调试面板，看最后停在哪个日志

---

## 2026-07-06 · 修复 (commit: b5e08fe)

### 修复：主脚本块语法错误导致所有函数未定义

**问题**：用浏览器清数据登录后仍然卡住，调试面板报错 `switchNav is not defined`、`openProfileSheet is not defined`。根因是主 `<script>` 块存在语法错误，导致整个脚本块无法执行，所有全局函数都没有被定义。

**根因**：`_saveAccountToList` 函数结束后残留了重复的代码行和多余的右花括号：

```javascript
function _saveAccountToList(email, token) {
  ...
  localStorage.setItem('lexi_accounts', JSON.stringify(list));
}
  localStorage.setItem('lexi_accounts', JSON.stringify(list));  // ← 多余
}                                                              // ← 多余
function _removeAccount(email) { ... }
```

**修复内容**：

| 文件 | 改动 |
|------|------|
| `Lexiword.html` | 删除 `_saveAccountToList` 后的重复代码和多余 `}`，修复语法错误 |
| `Lexiword.html` | 用 `node --check` 验证主脚本块语法通过 |

**影响范围**：该语法错误导致整个主 JS 块无法执行，因此 `switchNav`、`openProfileSheet`、`initData`、API 封装等全部失效，页面只能显示静态 HTML，所有点击无响应。

**回滚**：如需回滚，使用前一个 commit：
```bash
git checkout dd18ca8 -- Lexiword.html
```

---

## 2026-07-06 · 清理 (commit: 1fc50a2)

### 移除临时调试面板并清理启动日志

**改动内容**：

| 文件 | 改动 |
|------|------|
| `Lexiword.html` | 删除 body 顶部绿色调试面板（错误捕获、启动日志、强制渲染按钮） |
| `Lexiword.html` | 清理启动 IIFE 中残留的 `_lexiDebugLog` 日志调用 |
| `Lexiword.html` | 保留 3 秒启动安全网超时机制 |

**说明**：调试面板是为排查卡死问题临时添加的，问题定位后已移除，避免影响正常 UI。

---

## 版本对照

| Git Commit | 日期 | 说明 |
|------------|------|------|
| `1fc50a2` | 07-06 | 清理：移除临时调试面板和启动日志 |
| `b5e08fe` | 07-06 | 修复：主脚本块语法错误导致所有函数未定义 |
| `dd18ca8` | 07-06 | 修复：浏览器也卡死 — 全面缓存破坏 + 调试面板 + SW v4 |
| `f67f5b9` | 07-06 | 修复：svg-sprite 显式 display:none + HBuilderX 缓存破坏 |
| `0771fb5` | 07-06 | 🔴 修复：清数据后卡死（重复page-area ID）+ 快照恢复bug + 启动安全网 |
| `f6fa1b4` | 07-06 | 修复：切换卡死 + 登录页闪现 |
| `3f33540` | 07-06 | 修复：切换账号 undefined |
| `a3ec7fa` | 07-06 | 第四轮：记住账号点选切换 |
| `d864b09` | 07-06 | 第二轮：恢复本地数据合并（补全数据类型） |
| `e3dae30` | 07-06 | 第一轮：5 项修复（底部导航/遮罩/备份/首屏/数据隔离） |
| `3bcd6ff` | 07-06 | 文档更新 |
| `9a3c372` | 07-06 | 上一批 6 项优化 |

---

## 回滚命令速查

```bash
cd /d/project/Lexiword

# 回退到快照机制之前（切换账号功能加入前）
git checkout 83013c5 -- Lexiword.html login.html

# 回退到本轮所有修改之前
git checkout 3bcd6ff -- Lexiword.html login.html

# 只回退某个文件到任意版本
git checkout <commit-hash> -- <文件名>

# 查看所有改动历史
git log --oneline

# 查看某次提交的详细 diff
git show <commit-hash>
```
