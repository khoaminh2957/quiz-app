/* mastery.js — per-KC rolling-20 accuracy + Leitner spaced-review queue */
(function(){
const SCHEMA_V = 1;
const STORE_KEY = 'roadmap_state';
const themeBtn = document.getElementById('theme-toggle');
function applyTheme(t){ document.documentElement.setAttribute('data-theme', t); }
applyTheme(localStorage.getItem('theme')||'light');
themeBtn && themeBtn.addEventListener('click', () => {
  const n = (document.documentElement.getAttribute('data-theme')==='dark')?'light':'dark';
  applyTheme(n); localStorage.setItem('theme', n);
});

function loadState(){
  try {
    const s = JSON.parse(localStorage.getItem(STORE_KEY)||'null');
    if (!s || s.schema_v !== SCHEMA_V) return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, q_box:{}, schema_v:SCHEMA_V};
    return s;
  } catch(e){ return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, q_box:{}, schema_v:SCHEMA_V}; }
}

const DAY_MS = 86400000;
const LEITNER_DAYS = [1,3,7,16,35];

async function render(){
  const r = await fetch('/api/roadmap').then(r=>r.json());
  const stages = r.stages || [];
  const kcs = r.kcs || [];
  const state = loadState();
  const now = Date.now();

  // KC grid
  const grid = document.getElementById('kc-grid');
  grid.innerHTML = '';
  kcs.forEach(kc => {
    const arr = state.kc_mastery[kc] || [];
    const recent = arr.slice(-20);
    const acc = recent.length ? recent.filter(a=>a.correct).length / recent.length : null;
    const card = document.createElement('div');
    card.className = 'kc-card';
    card.innerHTML = `
      <div class="kc-name">${kc}</div>
      <div class="kc-stat">${recent.length}/20 attempts</div>
      <div class="bar"><span style="width:${acc===null?0:Math.round(acc*100)}%"></span></div>
      <div class="kc-acc">${acc===null?'no data':Math.round(acc*100)+'%'}</div>
    `;
    grid.appendChild(card);
  });

  // Stage grid
  const sg = document.getElementById('stage-grid');
  sg.innerHTML = '';
  stages.forEach(s => {
    const attempts = state.stage_attempts[s.id] || [];
    const recent = attempts.slice(-20);
    const acc = recent.length ? recent.filter(a=>a.correct).length / recent.length : null;
    const passed = acc !== null && acc >= s.mastery_gate;
    const card = document.createElement('div');
    card.className = `stage-bar ${passed?'passed':''}`;
    card.innerHTML = `
      <a href="/lesson/${s.id}">${s.order}. ${s.title}</a>
      <div class="bar"><span style="width:${acc===null?0:Math.round(acc*100)}%"></span></div>
      <div class="stage-acc">${acc===null?'no data':Math.round(acc*100)+'%'} / gate ${Math.round(s.mastery_gate*100)}% ${passed?'✓':''}</div>
    `;
    sg.appendChild(card);
  });

  // Due queue (Leitner)
  const due = [];
  for (const [qid, info] of Object.entries(state.last_review || {})){
    const dueAt = info.ts + info.next_due_days * DAY_MS;
    if (dueAt <= now){
      due.push({qid, overdue_days: Math.floor((now - dueAt)/DAY_MS), box: state.q_box[qid] || 1});
    }
  }
  due.sort((a,b)=> b.overdue_days - a.overdue_days);
  const dl = document.getElementById('due-list');
  if (due.length === 0){
    dl.innerHTML = '<li class="hint">Nothing due — keep working through stages.</li>';
  } else {
    dl.innerHTML = due.slice(0,20).map(d =>
      `<li>Q <code>${d.qid}</code> — box ${d.box}, overdue ${d.overdue_days}d</li>`
    ).join('');
  }
}
render();
})();
