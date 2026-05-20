/* gamification.js — daily question + streak heatmap + XP + weekly goal on landing.
 * Features synthesized from LeetCode (daily challenge), Duolingo (streak), Khan/SoloLearn (XP),
 * Codecademy (weekly goal). All client-side, vanilla JS, no DB.
 */
(function(){
function $(id){ return document.getElementById(id); }

function todayICT(){
  const now = new Date();
  const ictMs = now.getTime() + (now.getTimezoneOffset()*60000) + (7*3600000);
  return new Date(ictMs).toISOString().slice(0,10);
}

function renderDaily(daily, completed){
  const card = $('daily-card');
  if (!card) return;
  if (!daily || !daily.question){
    card.innerHTML = '<p class="hint">Không tải được câu hỏi hôm nay.</p>';
    return;
  }
  const q = daily.question;
  const doneClass = completed ? ' daily-done' : '';
  // q.stage_id is the GLOBAL stage id (e.g. "i5"). Per-lang route expects "py_i5".
  const perLangStageId = q.stage_id && q.stage_id.startsWith('py_') ? q.stage_id : `py_${q.stage_id}`;
  card.innerHTML = `
    <div class="daily-head">
      <h3>Câu hỏi hôm nay${completed ? ' <span class="passed">✓ đã làm</span>' : ''}</h3>
      <span class="muted">${daily.date}</span>
    </div>
    <p class="daily-q">${q.question || 'Code review'}</p>
    <div class="daily-meta">
      <span class="badge cat-method">${q.topic}</span>
      <span class="badge">${q.difficulty}</span>
      <span class="badge cat-idea">stage ${q.stage_id}</span>
    </div>
    <a href="/lang/python/lesson/${perLangStageId}" class="cta daily-cta${doneClass}">${completed ? 'Làm lại stage' : 'Mở bài học'}</a>
  `;
}

function renderStreak(g){
  const card = $('streak-card');
  if (!card) return;
  const cur = g.streak.current || 0;
  const longest = g.streak.longest || 0;
  // 53-week heatmap: 7×53 grid, last 371 days
  const today = new Date(todayICT() + 'T00:00:00Z');
  const days = [];
  const set = new Set(g.streak.history || []);
  for (let i = 370; i >= 0; i--){
    const d = new Date(today.getTime() - i*86400000);
    const key = d.toISOString().slice(0,10);
    days.push({date: key, active: set.has(key)});
  }
  // Group by columns of 7 (week)
  const cellSize = 11;
  const gap = 2;
  const cols = Math.ceil(days.length / 7);
  let svg = `<svg viewBox="0 0 ${cols*(cellSize+gap)} ${7*(cellSize+gap)}" width="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Bản đồ nhiệt streak 53 tuần">`;
  days.forEach((d, idx) => {
    const c = Math.floor(idx / 7);
    const r = idx % 7;
    const x = c * (cellSize + gap);
    const y = r * (cellSize + gap);
    const fill = d.active ? 'var(--accent)' : 'var(--code-bg)';
    svg += `<rect x="${x}" y="${y}" width="${cellSize}" height="${cellSize}" rx="2" fill="${fill}"><title>${d.date}${d.active?' · ✓':''}</title></rect>`;
  });
  svg += '</svg>';
  card.innerHTML = `
    <div class="streak-head">
      <h3><span aria-hidden="true">🔥</span> Streak ${cur} ngày</h3>
      <span class="muted">Kỷ lục: ${longest} ngày</span>
    </div>
    ${svg}
    ${cur === 0 ? '<p class="hint">Trả lời ít nhất 1 câu hôm nay để bắt đầu streak.</p>' : ''}
  `;
}

function renderXP(g){
  const card = $('xp-card');
  if (!card) return;
  const xp = g.xp_total || 0;
  const weekly = g.weekly || {earned:0, goal:200};
  const pct = Math.min(100, Math.round((weekly.earned / Math.max(1,weekly.goal)) * 100));
  card.innerHTML = `
    <div class="xp-head">
      <h3>XP tuần này</h3>
      <span class="muted">Tổng cộng: ${xp} XP</span>
    </div>
    <div class="xp-bar"><span style="width:${pct}%"></span></div>
    <div class="xp-meta">
      <strong>${weekly.earned}</strong> / ${weekly.goal} XP
      <span class="muted">(${pct}%)</span>
    </div>
    <label for="weekly-goal" class="sr-only">Mục tiêu tuần</label>
    <select id="weekly-goal" aria-label="Mục tiêu tuần">
      <option value="100">Nhẹ nhàng (100 XP)</option>
      <option value="200">Đều đặn (200 XP)</option>
      <option value="500">Nghiêm túc (500 XP)</option>
      <option value="1000">Cường độ cao (1000 XP)</option>
    </select>
  `;
  const sel = $('weekly-goal');
  if (sel){
    sel.value = String(weekly.goal);
    sel.addEventListener('change', () => {
      if (window.QUIZ_STATE_API) window.QUIZ_STATE_API.setWeeklyGoal(parseInt(sel.value,10));
      renderXP(window.STATE.gamification);
    });
  }
}

async function init(){
  if (!$('daily-card') && !$('streak-card') && !$('xp-card')) return;  // page doesn't host these widgets
  const g = (window.STATE && window.STATE.gamification) || {streak:{current:0,longest:0,history:[]},weekly:{earned:0,goal:200},xp_total:0,daily_completed:{}};
  let daily = null;
  try { daily = await fetch('/api/daily').then(r => r.json()); } catch(_){}
  renderDaily(daily, !!g.daily_completed[todayICT()]);
  renderStreak(g);
  renderXP(g);
}
document.addEventListener('DOMContentLoaded', init);
})();
