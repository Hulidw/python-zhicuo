// AI 讲解面板：调用后端 /api/chat（DeepSeek），流式输出
(function () {
  let history = [];
  let currentId = null;
  let controller = null;

  function endpoint() {
    const base = (window.APP_CONFIG && window.APP_CONFIG.apiBase) || '';
    return base.replace(/\/$/, '') + '/api/chat';
  }

  function currentQuestion() {
    try {
      return getq(db.session.ids[db.session.index]);
    } catch (e) {
      return null;
    }
  }

  function currentResult() {
    try {
      return db.session.results[db.session.index] || null;
    } catch (e) {
      return null;
    }
  }

  // 把题目信息整理成模型可读的上下文
  function buildContext(q, r) {
    const lines = [
      '【题目】' + q.category + '专项 · ' + q.topic + ' · ' + q.kind,
      '【题干】' + q.prompt,
      '【代码】',
      q.code || q.display || '',
    ];
    if (q.options && q.options.length) lines.push('【选项】' + q.options.join(' / '));
    lines.push('【我的作答】' + ((r && r.answer) || '未作答'));
    lines.push('【正确答案】' + q.answer);
    if (q.explain) lines.push('【官方解析】' + q.explain);
    return lines.join('\n');
  }

  let backendReady = null;

  function showOffline() {
    const box = document.getElementById('ai-panel');
    if (!box) return;
    box.innerHTML = [
      '<div class="card ai-card">',
      '<div class="row"><h3>AI 讲解</h3><span class="badge">未连接</span></div>',
      '<p class="mini">AI 功能需要本地后端支持。请先在本机运行 node server.js，再通过该服务的地址打开页面。</p>',
      '</div>',
    ].join('');
  }

  // 探测后端是否可用，避免静态托管时出现报错
  async function probeBackend() {
    try {
      const res = await fetch(endpoint().replace(/\/api\/chat$/, '/api/health'), { cache: 'no-store' });
      const data = await res.json().catch(() => ({}));
      backendReady = res.ok && data.ok === true;
    } catch (e) {
      backendReady = false;
    }
    if (!backendReady) showOffline();
  }

  function renderPanel(box) {
    box.innerHTML = [
      '<div class="card ai-card">',
      '<div class="row"><h3>AI 讲解</h3><span class="badge">DeepSeek</span></div>',
      '<p class="mini">由大模型结合本题代码与解析生成，可能有偏差，请以「执行过程」为准。</p>',
      '<div class="row"><button class="primary" onclick="aiExplain()">讲解这道题</button>',
      '<button onclick="aiWrongReason()">我错在哪里</button></div>',
      '<div id="ai-output" class="ai-output"><p class="mini">点击上方按钮，或直接提问。</p></div>',
      '<label>继续追问 <input id="ai-input" placeholder="例如：为什么这里结果是 3 而不是 4？" ',
      'onkeydown="if(event.key===\'Enter\'){event.preventDefault();aiFollowUp()}"',
      '></label>',
      '<button class="wide" onclick="aiFollowUp()">发送追问</button>',
      '</div>',
    ].join('');
  }

  window.initAI = function () {
    const box = document.getElementById('ai-panel');
    if (!box) return;
    const q = currentQuestion();
    if (!q) {
      box.innerHTML = '';
      return;
    }
    if (currentId !== q.id) {
      currentId = q.id;
      history = [];
      controller = null;
    }
    renderPanel(box);
    if (backendReady === null) probeBackend();
    else if (!backendReady) showOffline();
    if (history.length) {
      const out = document.getElementById('ai-output');
      if (out) out.textContent = history.map((m) => (m.role === 'user' ? '我：' : 'AI：') + m.content).join('\n\n');
    }
  };

  window.aiExplain = function () {
    const q = currentQuestion();
    if (!q) return;
    send(buildContext(q, currentResult()) + '\n\n请逐步讲解这道题：先说明代码每一步执行后变量的值，再解释正确答案为什么成立，最后指出最容易出错的地方。');
  };

  window.aiWrongReason = function () {
    const q = currentQuestion();
    const r = currentResult();
    if (!q) return;
    const mine = (r && r.answer) || '未作答';
    send(buildContext(q, r) + '\n\n我的答案是「' + mine + '」。请只针对我的答案，指出我从哪一步开始想错、正确思路是什么，不要重复通篇解析。');
  };

  window.aiFollowUp = function () {
    const input = document.getElementById('ai-input');
    const text = input ? input.value.trim() : '';
    if (!text) return;
    input.value = '';
    send(text);
  };

  async function send(text) {
    const out = document.getElementById('ai-output');
    if (!out) return;
    if (controller) controller.abort();
    controller = new AbortController();
    history.push({ role: 'user', content: text });

    out.className = 'ai-output';
    out.textContent = '正在思考…';
    let answer = '';

    try {
      const res = await fetch(endpoint(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history }),
        signal: controller.signal,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'AI 服务暂时不可用（' + res.status + '）');
      }
      out.textContent = '';
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;
          const data = trimmed.slice(5).trim();
          if (!data || data === '[DONE]') continue;
          try {
            const json = JSON.parse(data);
            const delta = json.choices && json.choices[0] && json.choices[0].delta;
            const piece = (delta && delta.content) || '';
            if (piece) {
              answer += piece;
              out.textContent = answer;
            }
          } catch (e) {
            // 忽略心跳等非 JSON 片段
          }
        }
      }
      if (!answer) {
        out.textContent = '模型没有返回内容，请再试一次。';
        history.pop();
        return;
      }
      history.push({ role: 'assistant', content: answer });
    } catch (err) {
      if (err.name === 'AbortError') return;
      history.pop();
      out.className = 'ai-output ai-error';
      out.textContent = err.message;
    }
  }
})();
