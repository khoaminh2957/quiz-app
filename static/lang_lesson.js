/* lang_lesson.js — per-lang lesson runner with hint sidebar dispatch.
 * Bug fixes:
 * - Double-submit guard (answered flag)
 * - Race condition (loading flag on start-practice)
 * - Confidence-pre clamp [1,5] before record
 * - Stage-locked check via API + roadmap state -> redirect to roadmap
 * - Focus mgmt: completion replacement focuses new heading
 * - Clipboard feedback (visual confirmation + execCommand fallback)
 */
(function(){
const lang = window.QUIZ_LANG;
const stageId = window.STAGE_ID;
let stageData = null, qs = [], cur = 0;
let answered = false;
let loading = false;

function clampConfidence(){
  const el = document.getElementById('confidence-pre');
  if (!el) return 3;
  let v = parseInt(el.value, 10);
  if (!Number.isFinite(v)) v = 3;
  v = Math.max(1, Math.min(5, v));
  el.value = String(v);
  return v;
}

function fireHints(q){
  const fn = window[`LANG_HINTS_${lang.toUpperCase()}`];
  if (fn) fn(q);
}

async function checkLocked(){
  // Defense: even if user lands here via direct URL, redirect if prereqs unmet
  try {
    const r = await fetch(`/api/lang/${lang}/roadmap`).then(r=>r.json());
    const stages = r.stages || [];
    const s = stages.find(x => x.id === stageId);
    if (!s) return false;
    const state = window.QUIZ_STATE_API ? window.QUIZ_STATE_API.get(lang) : {stage_attempts:{}};
    function acc(stage){
      const att = (state.stage_attempts || {})[stage.id] || [];
      if (!att.length) return null;
      const recent = att.slice(-20);
      return recent.filter(a => a.correct).length / recent.length;
    }
    for (const pid of (s.prereqs || [])){
      const prev = stages.find(x => x.id === pid);
      if (!prev) continue;
      const a = acc(prev);
      if (a === null || a < prev.mastery_gate) return prev;
    }
  } catch(_){}
  return false;
}

async function load(){
  if (loading) return;
  loading = true;
  try {
    const blocker = await checkLocked();
    if (blocker){
      document.querySelector('.lesson-intro').innerHTML =
        `<h2>Stage này chưa mở khoá</h2>
         <p>Cần đạt gate mastery (${Math.round(blocker.mastery_gate*100)}%) ở <strong>${blocker.title}</strong> trước.
         <a href="/lang/${lang}/roadmap">Quay lại lộ trình →</a></p>`;
      return;
    }
    const r = await fetch(`/api/lang/${lang}/stage/${stageId}`).then(r=>r.json());
    stageData = r.stage;
    qs = r.questions || [];
  } catch(e){
    document.querySelector('.lesson-intro').innerHTML =
      `<h2>Không tải được dữ liệu</h2><p>Có lỗi mạng. <button type="button" onclick="location.reload()">Thử lại</button></p>`;
    throw e;
  } finally {
    loading = false;
  }
}

function focusHeading(){
  const h = document.querySelector('#lesson-practice h2');
  if (h){ h.setAttribute('tabindex', '-1'); h.focus(); }
}

function renderQ(){
  if (qs.length === 0){
    document.getElementById('lesson-practice').innerHTML = `<h2>Stage này chưa có câu hỏi</h2>
      <p>Stage <code>${stageId}</code> hiện không có câu Python phù hợp. <a href="/lang/${lang}/roadmap">Quay lại lộ trình →</a></p>`;
    focusHeading();
    return;
  }
  if (cur >= qs.length){
    document.getElementById('lesson-practice').innerHTML = `<h2>Hoàn thành bài học</h2>
      <p>Đã trả lời ${qs.length} câu Python. <a href="/lang/${lang}/mastery">Xem mức độ thành thạo →</a></p>`;
    focusHeading();
    return;
  }
  const q = qs[cur];
  answered = false;
  const submitBtn = document.getElementById('submit-btn');
  if (submitBtn) submitBtn.disabled = false;
  document.getElementById('q-lang').textContent = q.lang;
  document.getElementById('q-topic').textContent = q.topic;
  document.getElementById('q-diff').textContent = `est ${q.est_difficulty>=0?'+':''}${q.est_difficulty.toFixed(2)}`;
  document.getElementById('q-kc').textContent = q.kc_tag;
  document.getElementById('q-idx').textContent = `Câu ${cur+1}/${qs.length}`;
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
  fireHints(q);
}

function submit(){
  if (answered) return;  // P1 fix: double-submit guard
  if (!qs || !qs.length || cur >= qs.length) return;
  const sel = document.querySelector('input[name=opt]:checked');
  if (!sel) return;
  const chosen = parseInt(sel.value);
  const q = qs[cur];
  const correct = chosen === q.correct_idx;
  answered = true;
  const submitBtn = document.getElementById('submit-btn');
  if (submitBtn) submitBtn.disabled = true;
  clampConfidence();  // P2 fix: validate before recording
  const fb = document.getElementById('feedback');
  fb.classList.remove('hidden');
  let html = `<div class="${correct?'correct':'wrong'}"><strong>${correct?'Đúng':'Chưa đúng — cùng xem nhé'}</strong></div><p>${q.explain}</p>`;
  if (!correct && q.misconception_map && q.misconception_map[String(chosen)]){
    html += `<div class="misconception"><strong>Vì sao đáp án ${chosen+1} sai:</strong> ${q.misconception_map[String(chosen)]}</div>`;
  }
  if (q.sources && q.sources.length){
    html += `<div class="sources">Nguồn: ${q.sources.join(' · ')}</div>`;
  }
  fb.innerHTML = html;
  document.getElementById('metacog-post').classList.remove('hidden');
  document.getElementById('metacog-post-text').textContent = q.metacog_post;
  window.QUIZ_STATE_API && window.QUIZ_STATE_API.recordAttempt(lang, q, chosen, correct);
  const ls = window.QUIZ_STATE_API ? window.QUIZ_STATE_API.get(lang) : {stage_attempts:{}};
  const attempts = ls.stage_attempts[stageId] || [];
  const recent = attempts.slice(-20);
  const accPct = recent.length ? (recent.filter(a=>a.correct).length / recent.length) : 0;
  const ms = document.getElementById('mastery-status');
  ms.innerHTML = `<div class="mastery-row">Độ chính xác (20 câu gần nhất): <strong>${Math.round(accPct*100)}%</strong> · gate <strong>${Math.round(stageData.mastery_gate*100)}%</strong> ${accPct>=stageData.mastery_gate?'<span class="passed">✓ đã đạt gate</span>':''}</div>`;
  // Celebrate when gate first crossed (only when stage has >=10 attempts to avoid noise)
  if (accPct >= stageData.mastery_gate && attempts.length >= 10 && window.SHOW_MASTERY_CELEBRATION){
    window.SHOW_MASTERY_CELEBRATION(stageData, accPct);
  }
}
function next(){
  if (!qs || !qs.length) return;
  cur++;
  renderQ();
  window.scrollTo({top:0, behavior:'smooth'});
}

document.getElementById('start-practice').addEventListener('click', async (e) => {
  const btn = e.currentTarget;
  if (loading) return;
  btn.disabled = true;
  btn.setAttribute('aria-expanded', 'true');
  await load();
  document.querySelector('.lesson-intro').classList.add('hidden');
  document.getElementById('lesson-practice').classList.remove('hidden');
  cur = 0;
  renderQ();
  // Move focus into practice section for SR users
  const card = document.getElementById('question-card');
  if (card){ card.setAttribute('tabindex','-1'); card.focus(); }
});
document.getElementById('submit-btn').addEventListener('click', submit);
document.getElementById('next-btn').addEventListener('click', next);
document.getElementById('copy-code').addEventListener('click', async (e) => {
  const btn = e.currentTarget;
  const text = document.getElementById('q-code').textContent || '';
  let ok = false;
  try {
    await navigator.clipboard.writeText(text);
    ok = true;
  } catch(_){
    // Fallback for non-HTTPS / older browsers
    try {
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      ok = document.execCommand('copy');
      ta.remove();
    } catch(_2){}
  }
  const original = btn.innerHTML;
  btn.innerHTML = ok ? '✓' : '✗';
  btn.setAttribute('aria-label', ok ? 'Đã copy' : 'Copy thất bại');
  setTimeout(() => { btn.innerHTML = original; btn.setAttribute('aria-label', 'Copy đoạn code'); }, 1200);
});
// Confidence-pre clamp on input change
document.getElementById('confidence-pre').addEventListener('input', clampConfidence);
document.getElementById('confidence-pre').addEventListener('blur', clampConfidence);

document.addEventListener('keydown', (e) => {
  if (document.activeElement && /input|textarea|select/i.test(document.activeElement.tagName)) return;
  if (e.altKey) return;
  if (e.key >= '1' && e.key <= '4'){
    const r = document.querySelectorAll('input[name=opt]')[parseInt(e.key)-1];
    if (r) r.checked = true;
  } else if (e.key === 'Enter'){ submit(); }
  else if (e.key === 'ArrowRight'){ next(); }
});
})();
