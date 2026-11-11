// 本地后端：托管前端静态文件 + 可选的 DeepSeek 对话代理（流式返回）
// 零第三方依赖，Node.js 18+ 即可运行
// 未配置 DEEPSEEK_API_KEY 时不会发起任何外部请求，只做静态服务。
const http = require('http');
const fs = require('fs');
const path = require('path');

// 读取同目录 .env，避免引入 dotenv
(function loadEnv() {
  const file = path.join(__dirname, '.env');
  if (!fs.existsSync(file)) return;
  for (let line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    line = line.replace(/^\uFEFF/, '').replace(/^\s*export\s+/, '');
    if (!line || /^\s*#/.test(line)) continue;
    const m = line.match(/^\s*([A-Za-z0-9_]+)\s*=\s*(.*)$/);
    if (!m) continue;
    const key = m[1];
    const value = m[2].replace(/^["']|["']$/g, '').trim();
    if (!process.env[key]) process.env[key] = value;
  }
})();

const PORT = Number(process.env.PORT || 8787);
const HOST = process.env.HOST || '0.0.0.0';
const API_KEY = process.env.DEEPSEEK_API_KEY || '';
const API_URL = process.env.DEEPSEEK_API_URL || 'https://api.deepseek.com/chat/completions';
const MODEL = process.env.DEEPSEEK_MODEL || 'deepseek-chat';
const ALLOW_ORIGIN = process.env.ALLOW_ORIGIN || '*';
const UPSTREAM_TIMEOUT = Number(process.env.UPSTREAM_TIMEOUT_MS || 120 * 1000);
const MAX_PER_WINDOW = Number(process.env.RATE_LIMIT || 20);
const ROOT = path.resolve(__dirname, process.env.DIST_DIR || 'dist');
const STARTED_AT = Date.now();

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

const SYSTEM_PROMPT = [
  '你是一位耐心、严谨的 Python 入门教学助手，服务对象是正在学习列表、循环、函数的初学者。',
  '回答要求：',
  '1. 用简体中文，语气平和，不用夸张的鼓励语。',
  '2. 先直接回答疑问，再解释原因；必要时用 3 行以内的小代码说明。',
  '3. 讲清「执行顺序、变量当前值、边界条件」这类细节，这正是用户容易出错的地方。',
  '4. 不要编造题目里没有的信息；不确定时明确说明。',
  '5. 单次回答控制在 250 字以内，除非用户要求展开。',
].join('\n');

// 简易限流：同一 IP 每分钟最多 N 次请求
const hits = new Map();
const WINDOW = 60 * 1000;
function isRateLimited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < WINDOW);
  if (list.length >= MAX_PER_WINDOW) {
    hits.set(ip, list);
    return true;
  }
  list.push(now);
  hits.set(ip, list);
  return false;
}
setInterval(() => {
  const now = Date.now();
  for (const [ip, list] of hits) {
    const kept = list.filter((t) => now - t < WINDOW);
    if (kept.length) hits.set(ip, kept);
    else hits.delete(ip);
  }
}, WINDOW).unref();

function sendJson(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'Access-Control-Allow-Origin': ALLOW_ORIGIN,
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
  });
  res.end(body);
}

function sendText(res, status, text) {
  res.writeHead(status, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Length': Buffer.byteLength(text),
    'X-Content-Type-Options': 'nosniff',
  });
  res.end(text);
}

function readBody(req, limit = 200 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > limit) {
        const err = new Error('请求内容过大');
        err.tooLarge = true;
        req.removeAllListeners('data');
        req.resume();
        reject(err);
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

// 校验并裁剪前端传来的消息，防止把超长内容转给模型
function normalizeMessages(input) {
  if (!Array.isArray(input)) return [];
  return input
    .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .slice(-8)
    .map((m) => ({ role: m.role, content: m.content.slice(0, 4000) }));
}

function logChat(ip, status, started, note) {
  const ms = Date.now() - started;
  console.log(`[chat] ${ip} ${status} ${ms}ms${note ? ' ' + note : ''}`);
}

async function handleChat(req, res) {
  const started = Date.now();
  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || req.socket.remoteAddress || 'unknown';

  if (isRateLimited(ip)) {
    logChat(ip, 429, started);
    return sendJson(res, 429, { error: '请求过于频繁，请稍后再试。' });
  }
  if (!API_KEY) {
    logChat(ip, 503, started, 'no-key');
    return sendJson(res, 503, {
      error: '后端未配置 DEEPSEEK_API_KEY，当前使用前端本地讲解。',
    });
  }

  let payload;
  try {
    payload = JSON.parse(await readBody(req));
  } catch (err) {
    const status = err.tooLarge ? 413 : 400;
    logChat(ip, status, started);
    return sendJson(res, status, { error: err.message || '请求格式错误' });
  }

  const messages = normalizeMessages(payload.messages);
  if (!messages.length) {
    logChat(ip, 400, started);
    return sendJson(res, 400, { error: '缺少对话内容' });
  }

  // 客户端断开时中止上游请求，避免继续消耗 token；同时限制整体等待时间
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT);
  const onClose = () => {
    if (!res.writableEnded) controller.abort();
  };
  res.on('close', onClose);

  let upstream;
  try {
    upstream = await fetch(API_URL, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        stream: true,
        temperature: 0.3,
        max_tokens: 900,
        messages: [{ role: 'system', content: SYSTEM_PROMPT }, ...messages],
      }),
    });
  } catch (err) {
    clearTimeout(timer);
    res.off('close', onClose);
    const timeout = err && err.name === 'AbortError';
    logChat(ip, timeout ? 504 : 502, started, err && err.message);
    if (!res.writableEnded) {
      sendJson(res, timeout ? 504 : 502, {
        error: timeout ? '模型响应超时，请稍后重试。' : '无法连接模型服务，请检查网络或稍后重试。',
      });
    }
    return;
  }

  if (!upstream.ok) {
    clearTimeout(timer);
    res.off('close', onClose);
    let detail = '';
    try {
      detail = await upstream.text();
    } catch {}
    const status = upstream.status >= 400 ? upstream.status : 502;
    let message = '模型服务暂时不可用，请稍后重试。';
    if (status === 401) message = 'DeepSeek 密钥无效，请检查 DEEPSEEK_API_KEY。';
    else if (status === 402) message = 'DeepSeek 账户余额不足，请充值后再试。';
    else if (status === 429) message = '模型调用过于频繁，请稍后再试。';
    logChat(ip, status, started, 'upstream');
    return sendJson(res, status, { error: message, detail: detail.slice(0, 300) });
  }

  // 逐块转发上游 SSE 数据
  res.writeHead(200, {
    'Content-Type': 'text/event-stream; charset=utf-8',
    'Cache-Control': 'no-cache, no-transform',
    Connection: 'keep-alive',
    'Access-Control-Allow-Origin': ALLOW_ORIGIN,
    'X-Accel-Buffering': 'no',
  });

  const reader = upstream.body.getReader();
  const decoder = new TextDecoder();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      res.write(decoder.decode(value, { stream: true }));
    }
    logChat(ip, 200, started);
  } catch {
    logChat(ip, 499, started, 'client-closed');
  } finally {
    clearTimeout(timer);
    res.off('close', onClose);
    if (!res.writableEnded) res.end();
  }
}

function sendFile(req, res, file, stat) {
  const ext = path.extname(file).toLowerCase();
  res.writeHead(200, {
    'Content-Type': MIME[ext] || 'application/octet-stream',
    'Content-Length': stat.size,
    'Cache-Control': ext === '.html' ? 'no-cache' : 'no-cache',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
  });
  if (req.method === 'HEAD') return res.end();
  const stream = fs.createReadStream(file);
  stream.on('error', () => res.destroy());
  stream.pipe(res);
}

function serveStatic(req, res) {
  let urlPath;
  try {
    urlPath = decodeURIComponent((req.url || '/').split('?')[0]);
  } catch {
    return sendText(res, 400, 'Bad Request');
  }

  const rel = urlPath === '/' ? 'index.html' : urlPath.replace(/^\/+/, '');
  const filePath = path.resolve(ROOT, rel);
  if (filePath !== ROOT && !filePath.startsWith(ROOT + path.sep)) {
    return sendText(res, 403, 'Forbidden');
  }

  fs.stat(filePath, (err, stat) => {
    if (!err && stat.isFile()) return sendFile(req, res, filePath, stat);
    // 只有无扩展名的前端路由才回退到 index.html；缺失的 js/css 明确返回 404
    if (path.extname(rel)) return sendText(res, 404, 'Not Found');
    const index = path.join(ROOT, 'index.html');
    fs.stat(index, (e2, s2) => {
      if (e2 || !s2.isFile()) return sendText(res, 404, 'Not Found');
      sendFile(req, res, index, s2);
    });
  });
}

const server = http.createServer((req, res) => {
  const pathname = (req.url || '/').split('?')[0];

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': ALLOW_ORIGIN,
      'Access-Control-Allow-Methods': 'GET, HEAD, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    });
    return res.end();
  }

  if (pathname === '/api/chat') {
    if (req.method !== 'POST') return sendJson(res, 405, { error: '只支持 POST' });
    return handleChat(req, res);
  }

  if (pathname === '/api/health') {
    return sendJson(res, 200, {
      ok: true,
      model: MODEL,
      configured: Boolean(API_KEY),
      mode: API_KEY ? 'remote' : 'local',
      uptime: Math.round((Date.now() - STARTED_AT) / 1000),
    });
  }

  if (pathname.startsWith('/api/')) return sendJson(res, 404, { error: '接口不存在' });

  if (req.method === 'GET' || req.method === 'HEAD') return serveStatic(req, res);
  sendText(res, 405, 'Method Not Allowed');
});

server.on('clientError', (err, socket) => {
  if (socket.writable) socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
  else socket.destroy();
});

server.listen(PORT, HOST, () => {
  console.log(`服务已启动：http://127.0.0.1:${PORT}（监听 ${HOST}）`);
  console.log(`静态目录：${ROOT}`);
  console.log(`模型：${MODEL}　密钥：${API_KEY ? '已配置' : '未配置（走前端本地讲解，不发起外部请求）'}`);
});

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => {
    console.log('\n正在关闭服务…');
    server.close(() => process.exit(0));
    setTimeout(() => process.exit(0), 3000).unref();
  });
}
