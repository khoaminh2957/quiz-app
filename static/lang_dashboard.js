/* lang_dashboard.js — per-lang dashboard KPIs + next-stage recommendation. */
(function(){
const lang = window.QUIZ_LANG;
async function render(){
  const [r, cohort] = await Promise.all([
    fetch(`/api/lang/${lang}/roadmap`).then(r=>r.json()),
    fetch('/api/cohort_progress').then(r=>r.json()),
  ]);
  const stages = r.stages || [];
  const langKcs = r.lang_specific_kcs || [];
  const state = window.QUIZ_STATE_API ? window.QUIZ_STATE_API.get(lang) : {stage_attempts:{}, kc_mastery:{}};

  // Stages complete
  let completed = 0;
  let totalAttempts = 0;
  let recentCorrect = 0, recentTotal = 0;
  let lowest = null;
  for (const s of stages){
    const attempts = (state.stage_attempts || {})[s.id] || [];
    totalAttempts += attempts.length;
    const recent = attempts.slice(-20);
    const acc = recent.length ? recent.filter(a=>a.correct).length/recent.length : null;
    if (acc !== null && acc >= s.mastery_gate) completed++;
    if (recent.length){
      recentCorrect += recent.filter(a=>a.correct).length;
      recentTotal += recent.length;
    }
    if (acc === null || acc < s.mastery_gate){
      if (lowest === null || (acc !== null && (lowest.acc === null || acc < lowest.acc))){
        lowest = {stage: s, acc};
      }
    }
  }
  document.getElementById('kpi-stages').textContent = `${completed}/${stages.length}`;
  document.getElementById('kpi-questions').textContent = `${totalAttempts}/${stages.reduce((a,s)=>a+s.question_ids.length,0)}`;
  document.getElementById('kpi-accuracy').textContent = recentTotal ? `${Math.round(recentCorrect/recentTotal*100)}%` : '—';
  // vs cohort: compare against last cohort iter pass rate
  const iterKeys = Object.keys(cohort.by_iter).map(Number).filter(k=>k>0).sort((a,b)=>b-a);
  const last = iterKeys.length ? cohort.by_iter[String(iterKeys[0])] : null;
  if (last && recentTotal){
    const me = recentCorrect/recentTotal;
    const delta = Math.round((me - last.post) * 1000)/10;
    document.getElementById('kpi-vs-cohort').textContent = `${delta>=0?'+':''}${delta}pp`;
  }
  // Stage pos in header
  const pos = document.getElementById('stage-pos');
  if (pos) pos.textContent = `stage ${completed}/${stages.length}`;
  const fill = document.getElementById('mastery-fill');
  if (fill) fill.style.width = `${(completed/Math.max(1,stages.length))*100}%`;

  // Next recommended
  const next = document.getElementById('next-card');
  if (lowest){
    next.classList.remove('hint');
    next.innerHTML = `<div class="kpi-label">Tiếp theo: stage ${lowest.stage.order}</div>
      <div class="kpi-val">${lowest.stage.title}</div>
      <p>${lowest.stage.question_ids.length} câu ${lang} · gate ${Math.round(lowest.stage.mastery_gate*100)}% · ${lowest.acc===null?'chưa có dữ liệu':Math.round(lowest.acc*100)+'% hiện tại'}</p>
      <a href="/lang/${lang}/lesson/${lowest.stage.id}" class="cta">Mở bài học →</a>`;
  } else {
    next.innerHTML = `<p>Tất cả stage đã đạt gate. <a href="/lang/${lang}/mastery">Xem mức độ thành thạo →</a></p>`;
  }

  // Lang hints panel
  const ul = document.getElementById('lang-hint-list');
  ul.classList.remove('hint');
  ul.innerHTML = langKcs.map(kc => `<li><code>${kc}</code></li>`).join('');
}
render();
})();
