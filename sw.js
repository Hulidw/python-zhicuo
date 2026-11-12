/* 知错 Service Worker：静态资源缓存优先 + 后台更新；/api/ 请求不走缓存。
   发布新版本时把 V 与 CORE 里的版本号一起更新。 */
const V = 'zhichuo-v37';
const CORE = ['./', 'index.html', 'style.css?v=34', 'questions.js?v=27', 'pitfalls.js?v=26', 'recipes.js?v=1', 'ai.js?v=30', 'app.js?v=35', 'config.js', 'account.js?v=36', 'adaptive.js', 'manifest.webmanifest', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => Promise.allSettled(CORE.map(u => c.add(new Request(u, { cache: 'reload' }))))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || !r.url.startsWith(self.location.origin) || r.url.includes('/api/')) return;
  e.respondWith(caches.open(V).then(async c => {
    const hit = await c.match(r);
    const net = fetch(r).then(res => { if (res && res.ok) c.put(r, res.clone()); return res; }).catch(() => null);
    if (hit) { net.catch(() => {}); return hit; }
    const res = await net;
    return res || c.match('./') || new Response('离线状态：缓存资源不可用', { status: 200, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  }));
});
