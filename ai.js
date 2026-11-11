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

  // 默认本地讲解：完全不联网；只有后端配置了 DEEPSEEK_API_KEY 才切到在线模式
  let mode = null;

  function localSteps(q) {
    return (q.steps || []).map(function (t, i) {
      const vars = Object.entries(t.variables || {}).map(function (e) { return e[0] + ' = ' + e[1]; }).join('，') || '无变量';
      return (i + 1) + '. 第 ' + t.line + ' 行' + (t.event === 'return' ? '（函数返回）' : '') + '：' + vars + (t.returned ? '，返回 ' + t.returned : '');
    }).join('\n');
  }

  function localExplain(q) {
    return [
      '【题目】' + q.category + ' · ' + q.topic + '（' + q.kind + '）',
      '【代码】', q.code || q.display || '',
      (q.steps || []).length ? '【真实执行轨迹】\n' + localSteps(q) : '',
      '【正确答案】' + q.answer,
      '【解析】' + q.explain,
      q.expected ? '【预期输出】\n' + q.expected : '',
      '【练习建议】在「执行过程」里从第 1 步点到最后一步，边点边说出每个变量的值，再回来看解析。',
    ].filter(Boolean).join('\n');
  }

  function localWrong(q, r) {
    const mine = (r && r.answer) || '未作答';
    const steps = q.steps || [];
    const last = steps[steps.length - 1];
    const lastVars = last ? Object.entries(last.variables || {}).map(function (e) { return e[0] + ' = ' + e[1]; }).join('，') : '';
    return [
      '你选的是「' + mine + '」，正确答案是「' + q.answer + '」。',
      last ? '【关键一步】执行到第 ' + last.line + ' 行时：' + (lastVars || '变量状态如上') + (last.output ? '，输出 ' + last.output : '') + '。' : '',
      '【正确思路】' + q.explain,
      '【最容易错的地方】' + q.topic + '：先确认类型、边界和返回值，再算结果。',
      '【下一步】在「执行过程」里从出错的前一步重放，看看哪个变量的值和你想的不一样。',
    ].filter(Boolean).join('\n');
  }

  function localSearch(text) {
    const pool = (typeof PITFALLS !== 'undefined' && PITFALLS.pitfalls) || [];
    const toks = (String(text).match(/[\u4e00-\u9fa5]{2,}|[A-Za-z_]{2,}/g) || []).slice(0, 10);
    if (!toks.length) return [];
    return pool.map(function (p) {
      const hay = (p.title + p.brief + p.cause + p.fix_note + p.keywords.join(' ')).toLowerCase();
      return { p: p, score: toks.reduce(function (n, t) { return n + (hay.indexOf(t.toLowerCase()) >= 0 ? 1 : 0); }, 0) };
    }).filter(function (x) { return x.score > 0; }).sort(function (a, b) { return b.score - a.score; }).slice(0, 2).map(function (x) { return x.p; });
  }

  function localFollow(text, q) {
    const hits = localSearch(text);
    if (hits.length) {
      return '在「错误地图」里找到可能相关的内容：\n\n' + hits.map(function (p) {
        return '【' + p.title + '】\n' + p.cause + '\n修复方向：' + p.fix_note;
      }).join('\n\n') + '\n\n如果对不上，把报错最后一行原样发过来，更容易定位。';
    }
    return [
      '这个问题暂时没匹配到站内案例，可以按这个顺序自查：',
      '1) 在「执行过程」里找到变量最后一次变化的位置；',
      '2) 用 print(type(x), repr(x)) 确认类型和真实值；',
      '3) 把报错最后一行的异常名和消息原样去搜索。',
      q ? '本题解析：' + q.explain : '',
    ].filter(Boolean).join('\n');
  }

  function say(text) {
    history.push({ role: 'assistant', content: text });
    const out = document.getElementById('ai-output');
    if (!out) return;
    out.className = 'ai-output';
    out.textContent = text;
  }

  function applyMode() {
    const badge = document.getElementById('ai-mode');
    if (badge) badge.textContent = mode === 'remote' ? 'DeepSeek 在线' : '本地讲解 · 不联网';
    const note = document.getElementById('ai-note');
    if (note) note.textContent = mode === 'remote'
      ? '由大模型结合本题代码与解析生成，可能有偏差，请以「执行过程」为准。'
      : '答案由本站题库与真实执行轨迹生成，不调用外部服务；仍建议对照「执行过程」验证。';
  }

  // 探测后端：配了密钥才用 DeepSeek，否则留在本地模式
  async function probeBackend() {
    try {
      const res = await fetch(endpoint().replace(/\/api\/chat$/, '/api/health'), { cache: 'no-store' });
      const data = await res.json().catch(function () { return {}; });
      mode = res.ok && data.ok === true && data.configured === true ? 'remote' : 'local';
    } catch (e) {
      mode = 'local';
    }
    applyMode();
  }

  function renderPanel(box) {
    box.innerHTML = [
      '<div class="card ai-card">',
      '<div class="row"><h3>AI 讲解</h3><span class="badge" id="ai-mode">本地讲解 · 不联网</span></div>',
      '<p class="mini" id="ai-note">答案由本站题库与真实执行轨迹生成，不调用外部服务；仍建议对照「执行过程」验证。</p>',
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
    applyMode();
    if (mode === null) probeBackend();
    if (history.length) {
      const out = document.getElementById('ai-output');
      if (out) out.textContent = history.map((m) => (m.role === 'user' ? '我：' : 'AI：') + m.content).join('\n\n');
    }
  };

  window.aiExplain = function () {
    const q = currentQuestion();
    if (!q) return;
    if (mode !== 'remote') { history.push({ role: 'user', content: '讲解这道题' }); return say(localExplain(q)); }
    send(buildContext(q, currentResult()) + '\n\n请逐步讲解这道题：先说明代码每一步执行后变量的值，再解释正确答案为什么成立，最后指出最容易出错的地方。');
  };

  window.aiWrongReason = function () {
    const q = currentQuestion();
    const r = currentResult();
    if (!q) return;
    const mine = (r && r.answer) || '未作答';
    if (mode !== 'remote') { history.push({ role: 'user', content: '我错在哪里' }); return say(localWrong(q, r)); }
    send(buildContext(q, r) + '\n\n我的答案是「' + mine + '」。请只针对我的答案，指出我从哪一步开始想错、正确思路是什么，不要重复通篇解析。');
  };

  window.aiFollowUp = function () {
    const input = document.getElementById('ai-input');
    const text = input ? input.value.trim() : '';
    if (!text) return;
    input.value = '';
    if (mode !== 'remote') { history.push({ role: 'user', content: text }); return say(localFollow(text, currentQuestion())); }
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
