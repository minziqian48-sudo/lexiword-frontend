# LexiLearn 改动日志 🔧

> 每次修改都记录在此，包含「改了什么 / 为什么改 / 怎么恢复」。
> 配合 `git log` 可精确回退到任意版本。

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

## 版本对照

| Git Commit | 日期 | 说明 |
|------------|------|------|
| `9e96539` | 07-06 | 第三轮：多账号切换+快照隔离 |
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
