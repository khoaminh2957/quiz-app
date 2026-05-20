/* lang_lesson.js — per-lang lesson runner with hint sidebar dispatch. */
(function(){
const lang = window.QUIZ_LANG;
const stageId = window.STAGE_ID;
let stageData = null, qs = [], cur = 0;

async function load(){
  const r = await fetch(`/api/lang/${lang}/stage/${stageId}`).then(r=>r.json());
  stageData = r.stage;
  qs = r.questions || [];
}

function fireHints(q){
  const fn = window[`LANG_HINTS_${lang.toUpperCase()}`];
  if (fn) fn(q);
}

function renderQ(){
  if (cur >= qs.length){
    document.getElementById('lesson-practice').innerHTML = `<h2>Hoàn thành bài học</h2>
      <p>Đã trả lời ${qs.length} câu ${lang}. <a href="/lang/${lang}/mastery">Xem mức độ thành thạo →</a></p>`;
    return;
  }
  const q = qs[cur];
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
  const sel = document.querySelector('input[name=opt]:checked');
  if (!sel) return;
  const chosen = parseInt(sel.value);
  const q = qs[cur];
  const correct = chosen === q.correct_idx;
  const fb = document.getElementById('feedback');
  fb.classList.remove('hidden');
  let html = `<div class="${correct?'correct':'wrong'}"><strong>${correct?'Đúng':'Sai'}</strong></div><p>${q.explain}</p>`;
  if (!correct && q.misconception_map && q.misconception_map[String(chosen)]){
    html += `<div class="misconception"><strong>Vì sao đáp án ${chosen+1} sai:</strong> ${q.misconception_map[String(chosen)]}</div>`;
  }
  if (q.sources && q.sources.length){
    html += `<div class="sources">Nguồn: ${q.sources.join(' · ')}</div>`;
  }
  fb.innerHTML = html;
  document.getElementById('metacog-post').classList.remove('hidden');
  document.getElementById('metacog-post-text').textContent = q.metacog_post;
  // record via state API
  window.QUIZ_STATE_API && window.QUIZ_STATE_API.recordAttempt(lang, q, chosen, correct);
  // mastery status
  const ls = window.QUIZ_STATE_API ? window.QUIZ_STATE_API.get(lang) : {stage_attempts:{}};
  const attempts = ls.stage_attempts[stageId] || [];
  const recent = attempts.slice(-20);
  const accPct = recent.length ? (recent.filter(a=>a.correct).length / recent.length) : 0;
  const ms = document.getElementById('mastery-status');
  ms.innerHTML = `<div class="mastery-row">Độ chính xác (20 câu gần nhất): <strong>${Math.round(accPct*100)}%</strong> · gate <strong>${Math.round(stageData.mastery_gate*100)}%</strong> ${accPct>=stageData.mastery_gate?'<span class="passed">✓ đã đạt gate</span>':''}</div>`;
}
function next(){ cur++; renderQ(); window.scrollTo({top:0, behavior:'smooth'}); }

document.getElementById('start-practice').addEventListener('click', async () => {
  await load();
  document.querySelector('.lesson-intro').classList.add('hidden');
  document.getElementById('lesson-practice').classList.remove('hidden');
  cur = 0; renderQ();
});
document.getElementById('submit-btn').addEventListener('click', submit);
document.getElementById('next-btn').addEventListener('click', next);
document.getElementById('copy-code').addEventListener('click', () => {
  navigator.clipboard.writeText(document.getElementById('q-code').textContent);
});
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
