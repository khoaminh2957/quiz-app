/* lesson.js — single-stage practice with metacog pre/post + misconception feedback */
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
    if (!s.q_box) s.q_box = {};
    if (!s.stage_attempts) s.stage_attempts = {};
    return s;
  } catch(e){ return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, q_box:{}, schema_v:SCHEMA_V}; }
}
function saveState(s){ s.schema_v=SCHEMA_V; localStorage.setItem(STORE_KEY, JSON.stringify(s)); }

const startBtn = document.getElementById('start-practice');
const stageId = startBtn ? startBtn.dataset.stageId : null;
let stageData = null;
let qs = [];
let cur = 0;

async function loadStage(){
  const r = await fetch(`/api/stage/${stageId}`).then(r=>r.json());
  stageData = r.stage;
  qs = r.questions || [];
}

function renderQ(){
  if (cur >= qs.length){
    document.getElementById('lesson-practice').innerHTML = `<h2>Lesson complete</h2>
      <p>You answered ${qs.length} questions in this stage. <a href="/mastery">View mastery →</a></p>`;
    return;
  }
  const q = qs[cur];
  document.getElementById('q-lang').textContent = q.lang;
  document.getElementById('q-topic').textContent = q.topic;
  document.getElementById('q-diff').textContent = `est ${q.est_difficulty>=0?'+':''}${q.est_difficulty.toFixed(2)}`;
  document.getElementById('q-kc').textContent = q.kc_tag;
  document.getElementById('q-idx').textContent = `Q ${cur+1}/${qs.length}`;
  document.getElementById('q-code').textContent = q.code;
  document.getElementById('q-question').textContent = q.question;
  document.getElementById('metacog-pre-text').textContent = q.metacog_pre;
  const form = document.getElementById('q-options');
  form.innerHTML = '';
  q.options.forEach((opt, i) => {
    const lbl = document.createElement('label');
    lbl.innerHTML = `<input type="radio" name="opt" value="${i}"> <span class="opt-text"></span>`;
    lbl.querySelector('.opt-text').textContent = `${i+1}. ${opt}`;
    form.appendChild(lbl);
  });
  document.getElementById('feedback').classList.add('hidden');
  document.getElementById('feedback').innerHTML = '';
  document.getElementById('metacog-post').classList.add('hidden');
  document.getElementById('reflection').value = '';
  document.getElementById('confidence-pre').value = 3;
}

function leitnerNextBox(curBox, correct){
  if (correct) return Math.min(curBox+1, 5);
  return 1;
}
const LEITNER_DAYS = [1,3,7,16,35];

function recordAttempt(q, chosen, correct){
  const state = loadState();
  state.stage_attempts[stageId] = state.stage_attempts[stageId] || [];
  state.stage_attempts[stageId].push({qid:q.id, chosen, correct, ts:Date.now()});
  state.kc_mastery[q.kc_tag] = state.kc_mastery[q.kc_tag] || [];
  state.kc_mastery[q.kc_tag].push({qid:q.id, correct, ts:Date.now()});
  if (state.kc_mastery[q.kc_tag].length > 50) state.kc_mastery[q.kc_tag] = state.kc_mastery[q.kc_tag].slice(-50);
  const curBox = state.q_box[q.id] || 1;
  const nextBox = leitnerNextBox(curBox, correct);
  state.q_box[q.id] = nextBox;
  state.last_review[q.id] = {ts:Date.now(), next_due_days: LEITNER_DAYS[nextBox-1]};
  saveState(state);
}

function submit(){
  const sel = document.querySelector('input[name=opt]:checked');
  if (!sel) return;
  const chosen = parseInt(sel.value);
  const q = qs[cur];
  const correct = chosen === q.correct_idx;
  const fb = document.getElementById('feedback');
  fb.classList.remove('hidden');
  let html = `<div class="${correct?'correct':'wrong'}"><strong>${correct?'Correct':'Incorrect'}</strong></div>`;
  html += `<p>${q.explain}</p>`;
  if (!correct && q.misconception_map && q.misconception_map[String(chosen)]){
    html += `<div class="misconception"><strong>Why option ${chosen+1} is wrong:</strong> ${q.misconception_map[String(chosen)]}</div>`;
  }
  if (q.sources && q.sources.length){
    html += `<div class="sources">Sources: ${q.sources.join(' · ')}</div>`;
  }
  fb.innerHTML = html;
  document.getElementById('metacog-post').classList.remove('hidden');
  document.getElementById('metacog-post-text').textContent = q.metacog_post;
  recordAttempt(q, chosen, correct);
  // mastery status
  const state = loadState();
  const attempts = state.stage_attempts[stageId] || [];
  const recent = attempts.slice(-20);
  const accNum = recent.filter(a=>a.correct).length;
  const accPct = recent.length ? (accNum/recent.length) : 0;
  const ms = document.getElementById('mastery-status');
  ms.innerHTML = `<div class="mastery-row">Rolling 20-Q accuracy: <strong>${Math.round(accPct*100)}%</strong> · gate <strong>${Math.round(stageData.mastery_gate*100)}%</strong> ${accPct>=stageData.mastery_gate?'<span class="passed">✓ gate met</span>':''}</div>`;
}

function next(){
  cur++;
  renderQ();
  window.scrollTo({top: 0, behavior: 'smooth'});
}

document.getElementById('start-practice').addEventListener('click', async () => {
  await loadStage();
  document.querySelector('.lesson-intro').classList.add('hidden');
  document.getElementById('lesson-practice').classList.remove('hidden');
  cur = 0;
  renderQ();
});
document.getElementById('submit-btn').addEventListener('click', submit);
document.getElementById('next-btn').addEventListener('click', next);
document.getElementById('copy-code').addEventListener('click', () => {
  navigator.clipboard.writeText(document.getElementById('q-code').textContent);
});
document.addEventListener('keydown', (e) => {
  if (document.activeElement && /input|textarea|select/i.test(document.activeElement.tagName)) return;
  if (e.key >= '1' && e.key <= '4'){
    const r = document.querySelectorAll('input[name=opt]')[parseInt(e.key)-1];
    if (r) r.checked = true;
  } else if (e.key === 'Enter'){ submit(); }
  else if (e.key === 'ArrowRight'){ next(); }
});
})();
