# LexiLearn 项目完整知识文档
# 项目：基于 Flask + SQLite 的单词学习应用
# 日期：2026-07-06
# 
# 本文档记录了 LexiLearn 项目的完整架构、部署配置、已解决的所有问题及其解决方案。
# 将此文档提供给任何 AI，即可获得完整的项目上下文。

================================================================================
一、项目概述
================================================================================

项目名称：LexiLearn（单词学习应用）
技术栈：
  - 后端：Flask + SQLite3 + JWT Auth（部署在 PythonAnywhere 免费版）
  - 前端：单文件 HTML（Lexiword.html，约3600行），部署在 GitHub Pages
  - 移动端：HBuilderX 云打包 APK（封装 GitHub Pages URL）
  - 认证：bcrypt 密码哈希 + JWT Token（30天有效期）

URL 地址：
  - 后端 API：https://minziqian48.pythonanywhere.com/api
  - 前端页面：https://minziqian48-sudo.github.io/lexiword-frontend/login.html
  - 前端主应用：https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html
  - 健康检查：https://minziqian48.pythonanywhere.com/api/health

重要：GitHub 用户名是 minziqian48-sudo（连字符），不是 minzjqian48.sudo（点号）。

================================================================================
二、后端架构（app.py）
================================================================================

文件位置：
  - 本地开发：D:\project\Lexiword\deploy_backend\app.py
  - PythonAnywhere：/home/minziqian48/app.py
  - WSGI 配置：/var/www/minziqian48_pythonanywhere_com_wsgi.py
    （内容：import sys; sys.path.insert(0, '/home/minziqian48'); from app import app as application）

功能路线：
  POST   /api/auth/register     - 注册
  POST   /api/auth/login        - 登录
  GET    /api/auth/me           - 获取当前用户信息
  GET    /api/states            - 获取所有单词学习状态
  PUT    /api/states/<day>/<word>    - 设置单词状态
  POST   /api/states/<day>/<word>/cycle - 循环切换状态
  PUT    /api/states/batch      - 批量设置单词状态
  GET    /api/checkin           - 获取打卡记录
  POST   /api/checkin           - 打卡
  GET    /api/sets              - 获取单词合集
  POST   /api/sets              - 创建合集
  PUT    /api/sets/<id>         - 更新合集
  DELETE /api/sets/<id>         - 删除合集
  POST   /api/sets/sync         - 同步合集
  GET    /api/pins              - 获取置顶书签
  PUT    /api/pins              - 保存置顶书签
  POST   /api/pins/toggle       - 切换置顶状态
  PUT    /api/star/<word>       - 收藏/取消收藏单词
  GET    /api/bookmark          - 获取词汇书签
  PUT    /api/bookmark          - 设置词汇书签
  GET    /api/meanings/<word>   - 获取单词释义
  PUT    /api/meanings/<word>   - 设置自定义释义
  GET    /api/daybook           - 获取单词库（公开）
  POST   /api/meanings/batch    - 批量获取释义
  GET    /api/backup            - 导出备份
  POST   /api/restore           - 导入恢复
  GET    /api/health            - 健康检查

数据库表（schema.sql）：
  - users (id, email, password_hash, nickname, created_at)
  - word_states (user_id, day, word, state, updated_at) UNIQUE(user_id, day, word)
  - checkin_records (user_id, date, created_at) UNIQUE(user_id, date)
  - starred_words (user_id, word) UNIQUE(user_id, word)
  - word_sets (id, user_id, name, words JSON, created_at, updated_at)
  - pinned_bookmarks (user_id, id)
  - vocab_bookmark (user_id, word)
  - custom_meanings (user_id, word, meaning, updated_at) UNIQUE(user_id, word)
  - daybook_words (day INT, word, meaning) UNIQUE(day, word)
  - visit_records (user_id, day, visited_at)

================================================================================
三、已解决的关键问题（按时间顺序）
================================================================================

--- 问题1：CORS + 405 Method Not Allowed ---
现象：
  - 浏览器 Console 报错：PUT/POST 请求返回 405 (METHOD NOT ALLOWED)
  - flask_cors 的 CORS(app) 在 PythonAnywhere 上不生效
  - 曾尝试 catch-all OPTIONS 路由，但导致更多问题

根因分析（多轮调试）：
  尝试1：flask_cors.CORS(app) → PythonAnywhere 环境不兼容，无效
  尝试2：@app.after_request + catch-all OPTIONS 路由 → catch-all 拦截了 PUT/POST 请求主体
  尝试3：@app.after_request 单独处理 405 → after_request 在路由匹配后才运行，此时 405 已产生

最终解决方案（app.py 第38-63行）：
  使用 @app.before_request 在 Flask 路由匹配之前拦截所有 OPTIONS 预检请求：

  @app.before_request
  def handle_cors_preflight():
      if request.method == 'OPTIONS':
          response = jsonify({'ok': True})
          origin = request.headers.get('Origin', '')
          response.headers['Access-Control-Allow-Origin'] = origin or '*'
          response.headers['Access-Control-Allow-Credentials'] = 'true'
          response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
          response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
          response.headers['Access-Control-Max-Age'] = '86400'
          return response

  @app.after_request
  def set_cors_headers(response):
      origin = request.headers.get('Origin', '')
      if origin:
          response.headers['Access-Control-Allow-Origin'] = origin
          response.headers['Access-Control-Allow-Credentials'] = 'true'
          response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
          response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
      return response

关键区别：
  - before_request 在路由匹配前执行 → OPTIONS 直接返回 200，Flask 看不到
  - after_request 在路由匹配后执行 → 405 已产生，无法拦截

--- 问题2：VPN 代理导致请求发到错误域名 ---
现象：
  - 浏览器请求全部发到 larkland6s.pothemer.cn（一个完全不属于项目的域名）
  - 但 GitHub 源码和 GitHub Pages 实际部署的 API_BASE 都是正确的 minziqian48.pythonanywhere.com
  - 即使无痕窗口也如此

根因：用户开启了全局 VPN，VPN 客户端在本地运行代理服务器，把所有 HTTPS 流量重定向到内部域名

解决：关闭 VPN，或在 VPN 中将以下域名加入直连白名单：
  - minziqian48.pythonanywhere.com
  - minziqian48-sudo.github.io

诊断命令：
  curl -s "https://minziqian48-sudo.github.io/lexiword-frontend/Lexiword.html" | grep "API_BASE"
  → 输出：const API_BASE = 'https://minziqian48.pythonanywhere.com/api';
  （确认 GitHub Pages 部署版本正确）

--- 问题3：app.py 语法错误导致 Flask 启动失败 → 404 ---
现象：
  - /api/health 返回 200（正常）
  - 但所有 PUT/POST 请求返回 404

根因：PythonAnywhere 错误日志显示：
  SyntaxError: closing parenthesis ')' does not match opening parenthesis '{' on line 73
  FILE "/home/minziqian48/app.py", line 74

说明：app.py 有语法错误（DAYBOOK_DATA 字典中的括号/花括号不匹配），导致 Python 加载失败。
虽然 /api/health 仍返回 200（可能是 PythonAnywhere 的 fallback），但自定义路由全部不存在。

解决：
  1. 用 python -m py_compile 验证本地 app.py 语法正确
  2. 重新生成干净的 app.py 代码
  3. 在 PythonAnywhere 的 app.py 编辑器中 Ctrl+A 全选 → Delete 清空 → 粘贴新代码 → Save

--- 问题4：Word 词库不完整 ---
现象：app.py 的 seed_daybook() 只包含 Day 1 的约 50 个单词，但完整词库有 28 天共 5567 个单词

解决：
  1. 从 Lexiword.html 中提取完整 DAYBOOK_DATA（JavaScript 格式）
  2. 转换为 Python 字典格式
  3. 生成完整的 seed_daybook() 函数（6268 行，334KB）
  4. 语法检查通过
  5. 通过 PythonAnywhere Files → Upload 上传 app_full.py，然后 mv 重命名为 app.py

提取脚本位置：D:\project\Lexiword\extract_daybook.py
生成文件：D:\project\Lexiword\daybook_data.py（5625行）
完整文件：D:\project\Lexiword\deploy_backend\app_full.py（6268行，334KB）

--- 问题5：init_db() 在 PythonAnywhere 上不执行 ---
现象：数据库表未创建

根因：init_db() 在 if __name__ == '__main__' 块内，但 PythonAnywhere 通过 WSGI 加载 app，
__name__ 不是 '__main__'，所以该块从不执行。

解决：将 init_db() 和 seed_daybook() 移到 if __name__ 块外面：
  with app.app_context():
      init_db()
      seed_daybook()

  if __name__ == '__main__':
      port = int(os.environ.get('PORT', 5000))
      app.run(host='0.0.0.0', port=port, debug=True)

--- 问题6：WSGI 配置指向的文件 ---
确认信息：
  - WSGI configuration file：/var/www/minziqian48_pythonanywhere_com_wsgi.py
  - 内容：import sys; sys.path.insert(0, '/home/minziqian48'); from app import app as application
  - 工作目录：/home/minziqian48/
  - 要更新的文件：/home/minziqian48/app.py

================================================================================
四、前端架构（Lexiword.html）
================================================================================

文件位置：
  - 本地：D:\project\Lexiword\Lexiword.html（约3600行）
  - GitHub Pages：lexiword-frontend 仓库的 main 分支

关键配置（第1677行）：
  const API_BASE = 'https://minziqian48.pythonanywhere.com/api';

完整词库（第1717-1746行）：
  const DAYBOOK_DATA = { "1": [...196个单词], "2": [...195个], ..., "28": [...] };
  总计 28 天，5567 个单词

登录页：login.html（独立文件）
访问统计页面：stats.html
Service Worker：sw.js（缓存名 lexilearn-v4）

================================================================================
五、PythonAnywhere 部署操作流程
================================================================================

部署步骤（每次更新 app.py 后）：
  1. 打开 PythonAnywhere → Files → /home/minziqian48/
  2. 上传新文件或编辑 app.py
  3. 打开 Web 标签 → Reload（绿色按钮）
  4. 验证：浏览器访问 https://minziqian48.pythonanywhere.com/api/health
     应返回 {"ok":true,"time":...}

查看错误日志（Web 标签页底部）：
  - Error log / Server log：包含 Python 语法错误、运行时异常

文件操作（Bash Console）：
  mv /home/minziqian48/app_full.py /home/minziqian48/app.py   # 重命名覆盖
  cp /home/minziqian48/app.py /home/minziqian48/app.py.bak    # 备份

================================================================================
六、本地项目文件结构
================================================================================

D:\project\Lexiword\
  ├── Lexiword.html           # 主应用（3600行，含所有前端逻辑）
  ├── login.html               # 登录页
  ├── index.html               # 入口页（token 检测后跳转）
  ├── stats.html               # 统计页
  ├── sw.js                    # Service Worker
  ├── manifest.json            # PWA 配置
  ├── CHANGELOG.md             # 版本历史
  ├── deploy_backend/
  │   ├── app.py               # 后端核心代码
  │   ├── app_full.py          # 完整版（含5567单词词库）
  │   └── schema.sql           # 数据库建表语句
  ├── extract_daybook.py       # 词库提取脚本
  ├── build_app.py             # 构建完整 app.py 的脚本
  └── daybook_data.py          # 提取出的 Python 词库数据

HBuilderX 项目：
  D:\data\HBuilderProjects\LexiLearn\
  └── index.html               # HBuilderX APK 打包入口

================================================================================
七、Git 信息
================================================================================

仓库名：lexiword-frontend
GitHub 用户名：minziqian48-sudo
最新提交：
  - 7ec7ce4 fix: apiFetchSilent 增加错误日志 + CORS诊断
  - b47a696 docs: CHANGELOG 记录日历闪现和切换丢数据修复
  - 759e1ef fix: 修复日历闪现 + 切换账号丢数据的防御性改进
  - 97e5a6a docs: CHANGELOG 记录导入数据根因修复
  - e07102b fix(根因): 修复导入数据丢失

================================================================================
八、常见问题排查清单
================================================================================

1. 浏览器请求全部发到 larkland6s.pothemer.cn
   → 关闭全局 VPN，或添加上述域名到白名单

2. PUT/POST 返回 405
   → 确认 app.py 有 @app.before_request handle_cors_preflight()
   → 确认已 Reload PythonAnywhere Web App

3. 所有路由返回 404，但 /api/health 返回 200
   → 查看 PythonAnywhere Error Log，99% 是 app.py 语法错误

4. 数据无法同步到服务器
   → 先检查 CORS/405 问题
   → 再用无痕窗口测试，排除 Service Worker 缓存

5. 浏览器加载旧版代码
   → F12 → Application → Clear site data
   → 或 Ctrl+Shift+N 无痕窗口
   → 或访问时加 ?_t=时间戳 参数

================================================================================
九、依赖清单
================================================================================

Python 包（PythonAnywhere 需安装）：
  pip install flask bcrypt pyjwt

无需安装的：
  flask_cors（已用手动 CORS 替代）
