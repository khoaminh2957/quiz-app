/* roadmap.js — render 15-stage tree, lock badges from localStorage.roadmap_state */
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
    if (!s || s.schema_v !== SCHEMA_V) return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, schema_v:SCHEMA_V};
    return s;
  } catch(e){ return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, schema_v:SCHEMA_V}; }
}
function saveState(s){ s.schema_v=SCHEMA_V; localStorage.setItem(STORE_KEY, JSON.stringify(s)); }

function stageAccuracy(state, stage){
  const attempts = state.stage_attempts[stage.id] || [];
  if (attempts.length === 0) return null;
  const recent = attempts.slice(-20);
  const correct = recent.filter(a => a.correct).length;
  return correct / recent.length;
}

function isLocked(state, stage, stages){
  if (!stage.prereqs || stage.prereqs.length === 0) return false;
  for (const pid of stage.prereqs){
    const prev = stages.find(s => s.id === pid);
    if (!prev) continue;
    const acc = stageAccuracy(state, prev);
    if (acc === null || acc < prev.mastery_gate) return true;
  }
  return false;
}

async function render(){
  const r = await fetch('/api/roadmap').then(r=>r.json());
  const stages = r.stages || [];
  const state = loadState();

  // header position
  const completed = stages.filter(s => {
    const acc = stageAccuracy(state, s);
    return acc !== null && acc >= s.mastery_gate;
  }).length;
  const pos = document.getElementById('stage-pos');
  if (pos) pos.textContent = `stage ${completed}/${stages.length}`;
  const fill = document.getElementById('mastery-fill');
  if (fill) fill.style.width = `${(completed/Math.max(1,stages.length))*100}%`;

  const tree = document.getElementById('roadmap-tree');
  if (!tree) return;
  const byLevel = {foundational:[], intermediate:[], advanced:[]};
  stages.forEach(s => byLevel[s.level] && byLevel[s.level].push(s));
  Object.keys(byLevel).forEach(level => byLevel[level].sort((a,b)=>a.order-b.order));

  tree.innerHTML = '';
  const levelTitles = {foundational:'Foundational', intermediate:'Intermediate', advanced:'Advanced'};
  for (const level of ['foundational','intermediate','advanced']){
    const section = document.createElement('section');
    section.className = `level level-${level}`;
    const h = document.createElement('h2');
    h.textContent = levelTitles[level];
    section.appendChild(h);
    const row = document.createElement('div');
    row.className = 'stage-row';
    for (const s of byLevel[level]){
      const locked = isLocked(state, s, stages);
      const acc = stageAccuracy(state, s);
      const passed = acc !== null && acc >= s.mastery_gate;
      const card = document.createElement('a');
      card.href = locked ? '#' : `/lesson/${s.id}`;
      card.className = `stage-card ${locked?'locked':''} ${passed?'passed':''}`;
      if (locked) card.addEventListener('click', e => {e.preventDefault(); alert('Locked: complete the prerequisite stage to mastery first.');});
      card.innerHTML = `
        <div class="stage-head">
          <span class="stage-order">${s.order}</span>
          <span class="stage-badge">${locked?'🔒':passed?'✓':'•'}</span>
        </div>
        <div class="stage-title">${s.title}</div>
        <div class="stage-meta">
          <span>${s.question_ids.length} Qs</span>
          <span>gate ${Math.round(s.mastery_gate*100)}%</span>
          <span>${s.est_min} min</span>
        </div>
        ${acc!==null ? `<div class="stage-acc"><span class="bar"><span style="width:${Math.round(acc*100)}%"></span></span> ${Math.round(acc*100)}%</div>` : ''}
      `;
      row.appendChild(card);
    }
    section.appendChild(row);
    tree.appendChild(section);
  }
}
render();
})();
