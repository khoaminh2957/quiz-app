/* mastery_perlang.js — per-lang KC + stage + Leitner due queue. */
(function(){
const lang = window.QUIZ_LANG;
const DAY_MS = 86400000;
async function render(){
  const r = await fetch(`/api/lang/${lang}/roadmap`).then(r=>r.json());
  const stages = r.stages || [];
  const kcs = r.kcs || [];
  const state = window.QUIZ_STATE_API ? window.QUIZ_STATE_API.get(lang) : {kc_mastery:{},stage_attempts:{},last_review:{},q_box:{}};
  const now = Date.now();

  const grid = document.getElementById('kc-grid');
  grid.innerHTML = '';
  kcs.forEach(kc => {
    const arr = (state.kc_mastery || {})[kc] || [];
    const recent = arr.slice(-20);
    const acc = recent.length ? recent.filter(a=>a.correct).length / recent.length : null;
    const card = document.createElement('div');
    card.className = 'kc-card';
    card.innerHTML = `
      <div class="kc-name">${kc}</div>
      <div class="kc-stat">${recent.length}/20 lượt</div>
      <div class="bar"><span style="width:${acc===null?0:Math.round(acc*100)}%"></span></div>
      <div class="kc-acc">${acc===null?'chưa có dữ liệu':Math.round(acc*100)+'%'}</div>`;
    grid.appendChild(card);
  });

  const sg = document.getElementById('stage-grid');
  sg.innerHTML = '';
  stages.forEach(s => {
    const attempts = (state.stage_attempts || {})[s.id] || [];
    const recent = attempts.slice(-20);
    const acc = recent.length ? recent.filter(a=>a.correct).length / recent.length : null;
    const passed = acc !== null && acc >= s.mastery_gate;
    const card = document.createElement('div');
    card.className = `stage-bar ${passed?'passed':''}`;
    card.innerHTML = `
      <a href="/lang/${lang}/lesson/${s.id}">${s.order}. ${s.title}</a>
      <div class="bar"><span style="width:${acc===null?0:Math.round(acc*100)}%"></span></div>
      <div class="stage-acc">${acc===null?'chưa có dữ liệu':Math.round(acc*100)+'%'} / gate ${Math.round(s.mastery_gate*100)}% ${passed?'✓':''}</div>`;
    sg.appendChild(card);
  });

  const due = [];
  for (const [qid, info] of Object.entries(state.last_review || {})){
    const dueAt = info.ts + info.next_due_days * DAY_MS;
    if (dueAt <= now){
      due.push({qid, overdue_days: Math.floor((now - dueAt)/DAY_MS), box: (state.q_box||{})[qid] || 1});
    }
  }
  due.sort((a,b)=> b.overdue_days - a.overdue_days);
  const dl = document.getElementById('due-list');
  if (due.length === 0){
    dl.innerHTML = '<li class="hint">Không có câu nào đến hạn — luyện tiếp.</li>';
  } else {
    dl.innerHTML = due.slice(0,20).map(d =>
      `<li>Câu <code>${d.qid}</code> — box ${d.box}, quá hạn ${d.overdue_days} ngày</li>`
    ).join('');
  }
}
render();
})();
