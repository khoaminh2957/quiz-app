// Quiz client - vanilla JS only
const PAGE_SIZE = 50;
const state = {
  all: [],
  filtered: [],
  idx: 0,
  answers: {}, // id -> chosen index
  page: 0,
  reviewMode: false,
};

function $(id) { return document.getElementById(id); }
function save() {
  try { localStorage.setItem('quiz_progress', JSON.stringify({ idx: state.idx, answers: state.answers })); } catch(e){}
}
function load() {
  try {
    const raw = localStorage.getItem('quiz_progress');
    if (!raw) return;
    const p = JSON.parse(raw);
    if (p && typeof p === 'object') { state.idx = p.idx|0; state.answers = p.answers || {}; }
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
  const resp = await fetch('/api/questions');
  state.all = await resp.json();
  populateFilters();
  applyFilters();
  render();
  attachEvents();
}

function populateFilters() {
  const langs = [...new Set(state.all.map(q => q.lang))].sort();
  const topics = [...new Set(state.all.map(q => q.topic))].sort();
  const diffs = ['easy','med','hard'];
  fillSelect('filter-lang', langs);
  fillSelect('filter-topic', topics);
  fillSelect('filter-diff', diffs);
}
function fillSelect(id, opts) {
  const sel = $(id);
  for (const o of opts) {
    const op = document.createElement('option');
    op.value = o; op.textContent = o;
    sel.appendChild(op);
  }
}

function applyFilters() {
  const lang = $('filter-lang').value;
  const topic = $('filter-topic').value;
  const diff = $('filter-diff').value;
  const mode = $('mode').value;
  let pool = state.all.filter(q =>
    (!lang || q.lang === lang) &&
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
  const correct = Object.entries(state.answers).reduce((acc, [id, choice]) => {
    const qq = state.all.find(x => x.id === id);
    return acc + (qq && qq.correct_idx === choice ? 1 : 0);
  }, 0);
  $('progress').textContent = `${answered} / ${total}`;
  $('score').textContent = `correct ${correct}/${answered}`;
  if (!q) {
    $('question-card').innerHTML = '<p>No questions match the current filters.</p>';
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
  if (state.answers[q.id] != null) showFeedback(q, state.answers[q.id]);
  // pager
  $('page-info').textContent = `Page ${Math.floor(state.idx / PAGE_SIZE) + 1} of ${Math.max(1, Math.ceil(state.filtered.length / PAGE_SIZE))}`;
}

function showFeedback(q, choice) {
  const fb = $('feedback');
  const ok = (choice === q.correct_idx);
  fb.className = ok ? 'ok' : 'bad';
  fb.classList.remove('hidden');
  const status = ok ? '✓ Correct' : `✗ Wrong (answer: ${q.correct_idx+1}. ${q.options[q.correct_idx]})`;
  const sources = (q.sources && q.sources.length) ? `Sources: ${q.sources.join(', ')}` : '';
  fb.innerHTML = `<strong>${status}</strong><div class="explain">${escapeHtml(q.explain)}</div>${sources ? `<div class="sources">${escapeHtml(sources)}</div>` : ''}`;
  // color the options
  document.querySelectorAll('#q-options label').forEach(l => {
    l.classList.add('disabled');
    const i = +l.dataset.idx;
    if (i === q.correct_idx) l.classList.add('correct');
    else if (i === choice) l.classList.add('wrong');
  });
}

function submit() {
  const q = state.filtered[state.idx];
  if (!q) return;
  const sel = document.querySelector('input[name=opt]:checked');
  if (!sel) return;
  const choice = +sel.value;
  state.answers[q.id] = choice;
  save();
  render();
  if (state.all.length > 0 && Object.keys(state.answers).length >= state.all.length) {
    setTimeout(() => alert('🎉 Completed all ' + state.all.length + ' questions!'), 100);
  }
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
    if (!confirm('Reset all answers?')) return;
    state.answers = {}; state.idx = 0; save(); applyFilters(); render();
  };
  $('theme-toggle').onclick = () => setTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  $('copy-code').onclick = () => navigator.clipboard.writeText($('q-code').textContent || '');
  for (const id of ['mode','filter-lang','filter-topic','filter-diff']) {
    $(id).onchange = () => { applyFilters(); render(); };
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
    if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
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
      $('mode').value = 'rand'; applyFilters(); state.idx = 0; render();
    }
  });
}

init();
