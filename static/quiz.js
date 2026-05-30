// Quiz client - vanilla JS only.
// Phase 0: fetch answer-STRIPPED questions từ /api/questions/public và chấm điểm
// SERVER-SIDE qua /api/check (đáp án không còn lộ trong payload).
const PAGE_SIZE = 50;
const state = {
  all: [],
  filtered: [],
  idx: 0,
  answers: {}, // id -> chosen index
  results: {}, // id -> { ok, correct_idx, explain, sources, choice }  (từ server)
  page: 0,
  reviewMode: false,
  submitting: false,
};

// Chấm 1 câu qua server (/api/check) — dùng cho submit() và backfill.
async function gradeOne(id) {
  const choice = state.answers[id];
  try {
    const r = await fetch('/api/check', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ id: id, choice: choice }) });
    const res = await r.json();
    state.results[id] = { ok: !!res.ok, correct_idx: res.correct_idx, explain: res.explain || '', sources: res.sources || [], choice: choice };
  } catch(e) {
    state.results[id] = { ok: null, correct_idx: null, explain: '', sources: [], choice: choice };
  }
}
async function gradeBatch(ids, conc) {
  conc = conc || 5;
  for (let i = 0; i < ids.length; i += conc) {
    await Promise.all(ids.slice(i, i + conc).map(gradeOne));
  }
}

function $(id) { return document.getElementById(id); }
function save() {
  try { localStorage.setItem('quiz_progress', JSON.stringify({ idx: state.idx, answers: state.answers, results: state.results })); } catch(e){}
}
function load() {
  try {
    const raw = localStorage.getItem('quiz_progress');
    if (!raw) return;
    const p = JSON.parse(raw);
    if (p && typeof p === 'object') { state.idx = p.idx|0; state.answers = p.answers || {}; state.results = p.results || {}; }
  } catch(e){}
}
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  try { localStorage.setItem('theme', t); } catch(e){}
}

async function init() {
  const t = (function(){ try { return localStorage.getItem('theme'); } catch(e){ return null; } })() || 'light';
  setTheme(t);
  load();
  let resp;
  try {
    resp = await fetch('/api/questions/public');
    if (!resp.ok) throw new Error('public endpoint ' + resp.status);
  } catch(e){
    // Backward-compat fallback (cũ vẫn ship đáp án) — chỉ khi public lỗi
    try { resp = await fetch('/api/questions'); }
    catch(e2){
      document.getElementById('quiz').innerHTML = '<p>Không tải được câu hỏi. <button type="button" onclick="location.reload()">Thử lại</button></p>';
      return;
    }
  }
  state.all = await resp.json();
  // Prune stale qids that no longer exist
  const validIds = new Set(state.all.map(q => q.id));
  let pruned = 0;
  for (const k of Object.keys(state.answers)){
    if (!validIds.has(k)){ delete state.answers[k]; delete state.results[k]; pruned++; }
  }
  if (pruned > 0) save();
  // Backfill: user cũ có answers nhưng chưa có results (trước khi đổi sang chấm
  // server-side) — re-grade qua /api/check để khôi phục điểm + feedback.
  const toGrade = Object.keys(state.answers).filter(id => state.results[id] == null);
  if (toGrade.length) { await gradeBatch(toGrade); save(); }
  populateFilters();
  applyFilters();
  render();
  attachEvents();
}

function populateFilters() {
  const topics = [...new Set(state.all.map(q => q.topic))].sort();
  const diffs = ['easy','med','hard'];
  fillSelect('filter-topic', topics);
  fillSelect('filter-diff', diffs);
}
function fillSelect(id, opts) {
  const sel = $(id);
  if (!sel) return;
  for (const o of opts) {
    const op = document.createElement('option');
    op.value = o; op.textContent = o;
    sel.appendChild(op);
  }
}

function applyFilters() {
  const topicEl = $('filter-topic'); const diffEl = $('filter-diff');
  const topic = topicEl ? topicEl.value : '';
  const diff = diffEl ? diffEl.value : '';
  const mode = $('mode').value;
  let pool = state.all.filter(q =>
    (!topic || q.topic === topic) &&
    (!diff || q.difficulty === diff)
  );
  if (mode === 'review') {
    pool = pool.filter(q => state.answers[q.id] != null);
  } else if (mode === 'rand') {
    pool = [...pool].sort(() => Math.random() - 0.5);
  }
  state.filtered = pool;
  state.reviewMode = (mode === 'review');
  if (state.idx >= pool.length) state.idx = 0;
  $('filtered-count').textContent = pool.length;
}

function render() {
  const q = state.filtered[state.idx];
  const total = state.all.length;
  const answered = Object.keys(state.answers).length;
  const correct = Object.values(state.results).reduce((acc, r) => acc + (r && r.ok ? 1 : 0), 0);
  $('progress').textContent = `${answered} / ${total}`;
  $('score').textContent = `đúng ${correct}/${answered}`;
  if (!q) {
    $('question-card').innerHTML = '<p>Không có câu hỏi nào khớp với bộ lọc hiện tại.</p>';
    return;
  }
  $('q-lang').textContent = q.lang;
  $('q-topic').textContent = q.topic;
  $('q-diff').textContent = q.difficulty;
  $('q-idx').textContent = `#${state.idx+1} / ${state.filtered.length}`;
  const codeEl = $('q-code');
  codeEl.textContent = q.code;
  codeEl.className = 'language-' + (q.lang === 'javascript' ? 'js' : q.lang);
  if (window.Prism && Prism.highlightElement) Prism.highlightElement(codeEl);
  $('q-question').textContent = q.question;
  const form = $('q-options');
  form.innerHTML = '';
  q.options.forEach((opt, i) => {
    const label = document.createElement('label');
    label.dataset.idx = i;
    const r = document.createElement('input');
    r.type = 'radio'; r.name = 'opt'; r.value = i;
    if (state.answers[q.id] === i) r.checked = true;
    label.appendChild(r);
    const span = document.createElement('span');
    span.textContent = `${i+1}. ${opt}`;
    label.appendChild(span);
    form.appendChild(label);
  });
  const fb = $('feedback');
  fb.classList.add('hidden'); fb.className = 'hidden';
  if (state.answers[q.id] != null) showFeedback(q);
  // pager
  $('page-info').textContent = `Trang ${Math.floor(state.idx / PAGE_SIZE) + 1} / ${Math.max(1, Math.ceil(state.filtered.length / PAGE_SIZE))}`;
}

function showFeedback(q) {
  const res = state.results[q.id];
  const fb = $('feedback');
  if (!res) { fb.classList.add('hidden'); fb.className = 'hidden'; return; }
  const ok = res.ok;
  const ci = res.correct_idx;
  fb.className = (ok === true) ? 'ok' : (ok === false ? 'bad' : '');
  fb.classList.remove('hidden');
  const status = (ok === true) ? '✓ Đúng'
    : (ok === false && ci != null) ? `✗ Sai (đáp án: ${ci+1}. ${q.options[ci]})`
    : '⚠ Chưa chấm được (mất kết nối)';
  const sources = (res.sources && res.sources.length) ? `Nguồn: ${res.sources.join(', ')}` : '';
  fb.innerHTML = `<strong>${status}</strong><div class="explain">${escapeHtml(res.explain || '')}</div>${sources ? `<div class="sources">${escapeHtml(sources)}</div>` : ''}`;
  // color the options
  document.querySelectorAll('#q-options label').forEach(l => {
    l.classList.add('disabled');
    const i = +l.dataset.idx;
    if (ci != null && i === ci) l.classList.add('correct');
    else if (i === res.choice) l.classList.add('wrong');
  });
}

async function submit() {
  const q = state.filtered[state.idx];
  if (!q) return;
  if (state.submitting) return;                  // chống double-submit (Enter/double-click)
  const sel = document.querySelector('input[name=opt]:checked');
  if (!sel) return;
  state.submitting = true;
  const btn = $('submit-btn'); if (btn) btn.disabled = true;
  const choice = +sel.value;
  const firstTime = (state.answers[q.id] == null);
  state.answers[q.id] = choice;
  save();
  await gradeOne(q.id);                           // chấm server-side
  save();
  render();
  if (window.Analytics) Analytics.track('quiz_submit', { qid: q.id, ok: state.results[q.id].ok, topic: q.topic, difficulty: q.difficulty });
  // Mừng hoàn thành CHỈ đúng lần chuyển sang đủ hết câu (không lặp mỗi lần nộp)
  if (firstTime && state.all.length > 0 && Object.keys(state.answers).length === state.all.length) {
    if (window.Analytics) Analytics.track('quiz_complete_all', { total: state.all.length });
    setTimeout(() => alert('🎉 Hoàn thành tất cả ' + state.all.length + ' câu!'), 100);
  }
  state.submitting = false;
  if (btn) btn.disabled = false;
}
function nextQ() {
  if (state.idx < state.filtered.length - 1) { state.idx++; save(); render(); }
}
function prevQ() {
  if (state.idx > 0) { state.idx--; save(); render(); }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function attachEvents() {
  $('submit-btn').onclick = submit;
  $('next-btn').onclick = nextQ;
  $('back-btn').onclick = prevQ;
  $('reset').onclick = () => {
    if (!confirm('Reset toàn bộ câu trả lời?')) return;
    state.answers = {}; state.results = {}; state.idx = 0; save(); applyFilters(); render();
  };
  $('theme-toggle').onclick = () => setTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  $('copy-code').onclick = () => navigator.clipboard.writeText($('q-code').textContent || '');
  for (const id of ['mode','filter-topic','filter-diff']) {
    const el = $(id); if (el) el.onchange = () => { applyFilters(); render(); };
  }
  document.querySelectorAll('.page-btn').forEach(b => {
    b.onclick = () => {
      const dir = parseInt(b.dataset.dir, 10);
      state.idx = Math.max(0, Math.min(state.filtered.length - 1, state.idx + dir * PAGE_SIZE));
      save(); render();
    };
  });

  document.addEventListener('keydown', e => {
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'select' || tag === 'textarea' || tag === 'button') return;
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key >= '1' && e.key <= '4') {
      const r = document.querySelector(`#q-options input[value="${+e.key - 1}"]`);
      if (r) r.checked = true;
    } else if (e.key === 'Enter') {
      submit();
    } else if (e.key === 'ArrowRight') {
      nextQ();
    } else if (e.key.toLowerCase() === 'b') {
      prevQ();
    } else if (e.key.toLowerCase() === 'r') {
      $('mode').value = 'rand'; applyFilters(); state.idx = 0; save(); render();
    }
  });
}

init();
