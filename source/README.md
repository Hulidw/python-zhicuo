# 知错 · Python 易错点学习助手 · 源码包

一套可离线运行的 Python 易错点学习站点：26 个真实报错案例（错误地图）、调试工具箱、120 道专项题、错题本、学习概况，附带一个零依赖的 Node 后端。本文档说明怎么跑起来、密钥放在哪、改哪里、上线前要注意什么。

---

## 一、目录结构

```
zhichuo-python-source/
├─ README.md              本说明
├─ 启动服务.bat            Windows 一键启动（自动生成 .env）
├─ .env.example           配置模板：密钥、端口、限流等
├─ .gitignore             避免把 .env 提交到仓库
├─ server.js              后端：静态托管 + DeepSeek 流式代理
├─ dist/                  前端站点（可直接静态托管）
│  ├─ index.html          入口，注意脚本加载顺序
│  ├─ app.js              路由、六个页面、练习与案例交互
│  ├─ ai.js               AI 讲解：默认本地生成，配了密钥才走模型
│  ├─ questions.js        120 道题 + 真实执行快照（脚本生成，勿手改）
│  ├─ pitfalls.js         26 个案例 + 真实 traceback（脚本生成，勿手改）
│  ├─ style.css           全部样式
│  ├─ config.js           Supabase 与后端地址配置
│  ├─ account.js          可选的邮箱登录 / 云端同步
│  └─ adaptive.js         自适应练习入口
├─ build_pitfalls.py      重新生成错误地图数据（会真实执行示例代码）
├─ build_questions.py     重新生成题库与执行快照
├─ test.cjs               状态转换冒烟测试
├─ verify_generated.cjs   校验生成的数据结构
├─ supabase.sql           可选：邮箱登录所需的数据库表
└─ docs/
   └─ 邮箱账号接入.md      可选：Supabase 配置步骤
```

环境要求：

- **Node.js 18 或更高**（必需，后端用到全局 `fetch`；无需 `npm install`）
- **Python 3.9+**（可选，只有重新生成题库 / 错误地图时才需要；`pandas` 可选）

---

## 二、第一次运行（约 1 分钟）

1. 复制 `.env.example` 为 `.env`（双击 `启动服务.bat` 会自动完成这一步）。
2. 用记事本打开 `.env`，按需填写 `DEEPSEEK_API_KEY`。**不填也能用**，见下一节。
3. 双击 `启动服务.bat`，或在当前目录执行：

```powershell
node server.js
```

4. 浏览器打开 <http://127.0.0.1:8787>。

手机访问（同一 Wi-Fi）：执行 `ipconfig` 找到本机 IPv4，例如 `192.168.1.20`，手机打开 `http://192.168.1.20:8787`。首次访问时 Windows 防火墙弹窗请选择“允许”。

停止服务：在运行窗口按 `Ctrl+C`。端口被占用时改 `.env` 里的 `PORT`，或结束占用进程：

```powershell
Get-NetTCPConnection -LocalPort 8787 -State Listen | Select-Object OwningProcess
Stop-Process -Id <上一步的进程号> -Force
```

---

## 三、密钥与费用

### 3.1 不填密钥（默认）

`/api/health` 返回 `"mode":"local"`。此时后端只做静态文件服务，**不会向任何外部地址发请求，也不会产生费用**。页面里的「AI 讲解」由 `dist/ai.js` 用题库和真实执行轨迹在浏览器本地生成，功能完整。

### 3.2 填 DeepSeek 密钥（可选）

1. 登录 <https://platform.deepseek.com/>，进入 API keys，创建一个 key。
2. 写入 `.env`：

```
DEEPSEEK_API_KEY=sk-你的密钥
```

3. 重启 `node server.js`。`/api/health` 的 `mode` 会变成 `remote`，页面标签显示「DeepSeek 在线」。

只想在个别机器开启时，也可以临时用环境变量，不必写文件：

```powershell
$env:DEEPSEEK_API_KEY='sk-...'; node server.js
```

密钥只放在 `.env` 或服务器环境变量里。**不要写进 `dist/` 下任何 js 文件**，前端代码是公开的。

### 3.3 可选：邮箱登录（Supabase）

默认关闭。若要启用，按 [docs/邮箱账号接入.md](docs/邮箱账号接入.md) 建表，再修改 `dist/config.js`：

```js
window.APP_CONFIG = {
  supabaseUrl: 'https://xxxx.supabase.co',
  supabaseKey: 'anon/publishable 公钥',
  apiBase: ''
};
```

`anon` / publishable 公钥可以公开；**`service_role` 密钥绝对不能放进前端**。

---

## 四、全部配置项（.env）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 空 | 留空即本地模式，不联网、不计费 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 也可换成账号可用的其他模型名 |
| `DEEPSEEK_API_URL` | 官方 chat/completions | 换代理或兼容接口时改这里 |
| `PORT` | `8787` | 本地端口 |
| `HOST` | `0.0.0.0` | 改为 `127.0.0.1` 可禁止局域网访问 |
| `ALLOW_ORIGIN` | `*` | 允许跨域调用接口的前端来源；线上建议写死域名 |
| `RATE_LIMIT` | `20` | 每个 IP 每分钟最多对话次数 |
| `UPSTREAM_TIMEOUT_MS` | `120000` | 模型请求总超时，超时返回 504 |
| `DIST_DIR` | `dist` | 静态目录，可指向另一份构建产物 |

客户端中途关闭页面时，后端会立即中止上游请求，不再继续消耗 token。

---

## 五、想改功能，改哪个文件

| 想改什么 | 文件 | 说明 |
| --- | --- | --- |
| 页面路由、首页、练习、错题、统计 | `dist/app.js` | 单文件应用，`route()` 解析 hash，页面函数按名注册 |
| 错误地图与案例详情交互 | `dist/app.js` | 筛选、点击判行、修复三选一、埋错练习都在这里 |
| 调试工具箱（traceback 小测、pdb 模拟器） | `dist/app.js` | 静态章节 + 两个交互模块 |
| AI 讲解文案与本地检索 | `dist/ai.js` | 本地模式不联网；`buildContext` 负责给模型喂上下文 |
| 题目内容 | `build_questions.py` → `dist/questions.js` | 改脚本后重新生成，不要直接改生成文件 |
| 报错案例 | `build_pitfalls.py` → `dist/pitfalls.js` | 同上；构建时会真实执行代码并抓 traceback |
| 样式、移动端适配 | `dist/style.css` | 断点与组件都在末尾集中定义 |
| 后端行为、限流、跨域、日志 | `server.js` | 零依赖，读一遍即可改 |
| 邮箱登录与云端同步 | `dist/account.js` + `dist/config.js` | 未配置时自动隐藏为游客模式 |

改完 `dist` 下的文件后强制刷新（`Ctrl+F5`），或把 `index.html` 里引用处的 `?v=26` 递增，避免浏览器缓存。改 `server.js` 需要重启进程。

---

## 六、重新生成数据

```powershell
python build_pitfalls.py
python build_questions.py
```

两个脚本都会**真实执行**每个示例：错误代码必须产生预期异常，修复代码必须通过断言，否则立即中止并指出是哪一条。因此本机 Python 版本、已安装的第三方库会影响生成的 traceback 文本，这是有意设计，不要手写或替换报错内容。

---

## 七、自检

```powershell
node test.cjs
node verify_generated.cjs
```

`test.cjs` 检查练习、错题、复习等状态转换；`verify_generated.cjs` 检查题库与案例的字段完整性。它们不替代浏览器里的实际点击验证。

---

## 八、部署到线上

### 只要静态站点（最简单）

把 `dist` 里的文件上传到 GitHub Pages、Cloudflare Pages、Nginx 等任意静态托管即可。纯静态环境没有 `/api` 接口，页面会自动使用本地讲解模式，功能不受影响。

### 需要在线模型

1. 把 `server.js` 部署到能运行 Node 18+ 的服务器（或容器），配置 `DEEPSEEK_API_KEY`。
2. 在 `dist/config.js` 里把 `apiBase` 填成该服务地址，例如 `https://api.your-domain.com`。
3. 服务端把 `ALLOW_ORIGIN` 设为你的站点域名，不要长期保留 `*`。
4. 前面加一层 HTTPS 反向代理（Nginx / Caddy）。HTTPS 页面无法调用 HTTP 接口，浏览器会直接拦截。
5. 生产环境建议把 `HOST` 改为 `127.0.0.1`，由反向代理对外。

---

## 九、注意事项（请务必阅读）

1. **`.env` 不进 Git、不外发**。仓库里只保留 `.env.example`；密钥一旦泄露，立刻在平台吊销并重建。
2. 前端是公开代码，任何密钥都不能写在 `dist/` 里。Supabase 只放 anon 公钥。
3. 本地服务默认监听 `0.0.0.0`，同一网络的人都能访问。公共 Wi-Fi 下使用请改为 `127.0.0.1`。
4. 学习记录存在浏览器 `localStorage`，清缓存、换浏览器、换设备都会丢；需要跨设备请配置 Supabase 登录。
5. 修改生成文件（`questions.js`、`pitfalls.js`）会在下次构建时被覆盖，请改对应的 Python 脚本。
6. Python 版本差异会导致报错文案不同（例如 3.12 的 `Did you mean` 建议），属于正常现象。
7. 部署静态站点时若沿用旧文件名，记得让 CDN 或浏览器刷新缓存，否则用户可能仍看到旧版本。

---

## 十、常见问题

| 现象 | 原因与处理 |
| --- | --- |
| `Error: listen EADDRINUSE` | 端口被占用，改 `PORT` 或结束占用进程 |
| `fetch is not defined` | Node 低于 18，升级 Node |
| `/api/chat` 返回 503 | 未配置密钥，属正常；需要在线模型再填 key |
| 返回 401 | 密钥错误或已被吊销，重新生成 |
| 返回 402 | 平台账户余额不足 |
| 返回 429 | 触发本站限流或平台额度限制，稍后再试 |
| 返回 502 / 504 | 网络不通或模型超时，检查网络与 `UPSTREAM_TIMEOUT_MS` |
| 页面样式或脚本没更新 | `Ctrl+F5`，或递增 `index.html` 里的 `?v=` |
| 手机上打不开 | 确认同一 Wi-Fi、IP 正确、防火墙已允许 Node |
| 构建脚本中途退出 | 终端会指出是哪条案例未产生预期异常，多为 Python 版本或库版本差异 |

---

## 十一、许可与来源

本包为教学用途整理，代码可自由修改与再分发。题目与案例中的报错文本由本机 Python 实际运行生成，请在自己环境中重新构建后再对外发布。
