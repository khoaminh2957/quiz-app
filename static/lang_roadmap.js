/* lang_roadmap.js — render per-lang 15-stage tree with lock badges. */
(function(){
const lang = window.QUIZ_LANG;
function stageAccuracy(state, stage){
  const attempts = (state.stage_attempts || {})[stage.id] || [];
  if (attempts.length === 0) return null;
  const recent = attempts.slice(-20);
  return recent.filter(a => a.correct).length / recent.length;
}
function isLocked(state, stage, stages){
  if (!stage.prereqs || !stage.prereqs.length) return false;
  for (const pid of stage.prereqs){
    const prev = stages.find(s => s.id === pid);
    if (!prev) continue;
    const acc = stageAccuracy(state, prev);
    if (acc === null || acc < prev.mastery_gate) return true;
  }
  return false;
}
let currentTopicFilter = '';
let cachedStages = [];
let cachedAllQs = null;

async function render(){
  const r = await fetch(`/api/lang/${lang}/roadmap`).then(r=>r.json());
  const allStages = r.stages || [];
  cachedStages = allStages;
  // Topic filter: fetch all questions once, group by stage_id, count which stages contain that topic
  if (currentTopicFilter && !cachedAllQs){
    try { cachedAllQs = await fetch('/api/questions').then(r=>r.json()); } catch(_){}
  }
  let stages = allStages;
  if (currentTopicFilter && cachedAllQs){
    const stagesWithTopic = new Set(
      cachedAllQs.filter(q => q.topic === currentTopicFilter).map(q => `${lang.slice(0,2)}_${q.stage_id}`)
    );
    stages = allStages.filter(s => stagesWithTopic.has(s.id));
  }
  const state = window.QUIZ_STATE_API ? window.QUIZ_STATE_API.get(lang) : {stage_attempts:{}};
  const completed = stages.filter(s => {
    const acc = stageAccuracy(state, s);
    return acc !== null && acc >= s.mastery_gate;
  }).length;
  const pos = document.getElementById('stage-pos');
  if (pos) pos.textContent = `stage ${completed}/${stages.length}`;
  const fill = document.getElementById('mastery-fill');
  if (fill) fill.style.width = `${(completed/Math.max(1,stages.length))*100}%`;

  const tree = document.getElementById('roadmap-tree');
  tree.innerHTML = '';
  const byLevel = {foundational:[], intermediate:[], advanced:[]};
  stages.forEach(s => byLevel[s.level] && byLevel[s.level].push(s));
  Object.keys(byLevel).forEach(level => byLevel[level].sort((a,b)=>a.order-b.order));

  const titles = {foundational:'Foundational', intermediate:'Intermediate', advanced:'Advanced'};
  for (const level of ['foundational','intermediate','advanced']){
    const section = document.createElement('section');
    section.className = `level level-${level}`;
    section.innerHTML = `<h2>${titles[level]}</h2>`;
    const row = document.createElement('div');
    row.className = 'stage-row';
    for (const s of byLevel[level]){
      const locked = isLocked(state, s, stages);
      const acc = stageAccuracy(state, s);
      const passed = acc !== null && acc >= s.mastery_gate;
      const card = document.createElement('a');
      card.href = locked ? '#' : `/lang/${lang}/lesson/${s.id}`;
      card.className = `stage-card ${locked?'locked':''} ${passed?'passed':''}`;
      if (locked){
        card.setAttribute('aria-disabled', 'true');
        card.setAttribute('aria-describedby', `lock-reason-${s.id}`);
        card.addEventListener('click', e => {
          e.preventDefault();
          const status = document.getElementById('roadmap-status');
          if (status) status.textContent = `Đã khoá: hoàn thành stage ${s.order - 1} để mở stage này.`;
        });
      }
      // Preview: list 2-3 KCs as chips
      const kcChips = (s.kc_coverage || []).slice(0, 3).map(kc => `<span class="kc-chip">${kc}</span>`).join('');
      // Progress ring (SVG)
      const ringPct = acc !== null ? Math.round(acc * 100) : 0;
      const circumference = 2 * Math.PI * 18;
      const dashOffset = circumference * (1 - ringPct/100);
      const ringSvg = acc !== null ? `<svg class="prog-ring" width="44" height="44" viewBox="0 0 44 44" aria-hidden="true">
        <circle cx="22" cy="22" r="18" fill="none" stroke="var(--code-bg)" stroke-width="3"/>
        <circle cx="22" cy="22" r="18" fill="none" stroke="${ringPct >= s.mastery_gate*100 ? 'var(--ok)' : 'var(--accent)'}"
                stroke-width="3" stroke-linecap="round" stroke-dasharray="${circumference}" stroke-dashoffset="${dashOffset}"
                transform="rotate(-90 22 22)"/>
        <text x="22" y="26" text-anchor="middle" font-size="11" fill="var(--fg)">${ringPct}%</text>
      </svg>` : '';
      card.innerHTML = `
        <div class="stage-head">
          <span class="stage-order">${s.order}</span>
          ${ringSvg || `<span class="stage-badge" aria-hidden="true">${locked?'🔒':passed?'✓':'•'}</span>`}
        </div>
        <div class="stage-title">${s.title}</div>
        <div class="kc-chips">${kcChips}</div>
        <div class="stage-meta"><span>${s.question_ids.length} câu</span><span>gate ${Math.round(s.mastery_gate*100)}%</span><span>${s.est_min} phút</span></div>
        ${acc!==null && !ringSvg ? `<div class="stage-acc"><span class="bar"><span style="width:${ringPct}%"></span></span> ${ringPct}%</div>` : ''}
      `;
      row.appendChild(card);
    }
    section.appendChild(row);
    tree.appendChild(section);
  }
}
// Topic filter handlers
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.chip-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.chip-filter').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTopicFilter = btn.dataset.topic || '';
      render();
    });
  });
});
render();
})();
