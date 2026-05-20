/* progress.js — cohort vs personal chart on /progress. Vanilla canvas, no libs. */
(function(){
function applyTheme(t){ document.documentElement.setAttribute('data-theme', t); }
applyTheme(localStorage.getItem('theme') || 'light');
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('theme-toggle');
  btn && btn.addEventListener('click', () => {
    const n = (document.documentElement.getAttribute('data-theme')==='dark')?'light':'dark';
    applyTheme(n); localStorage.setItem('theme', n);
  });
});

function getPersonal(){
  try {
    const s = JSON.parse(localStorage.getItem('state') || 'null');
    if (!s || !s.per_lang) return null;
    const out = {};
    for (const lang of Object.keys(s.per_lang)){
      const ls = s.per_lang[lang];
      let allAttempts = [];
      for (const sid of Object.keys(ls.stage_attempts || {})){
        allAttempts = allAttempts.concat(ls.stage_attempts[sid]);
      }
      const recent = allAttempts.slice(-50);
      if (recent.length){
        out[lang] = recent.filter(a => a.correct).length / recent.length;
      }
    }
    return out;
  } catch(e){ return null; }
}

function drawChart(canvas, byIter){
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0,0,W,H);
  const padL = 50, padR = 20, padT = 20, padB = 40;
  const innerW = W - padL - padR, innerH = H - padT - padB;
  // axes
  const fg = getComputedStyle(document.body).getPropertyValue('color') || '#333';
  const muted = '#888';
  ctx.strokeStyle = muted; ctx.fillStyle = muted; ctx.font = '11px sans-serif';
  ctx.beginPath(); ctx.moveTo(padL, padT); ctx.lineTo(padL, H-padB); ctx.lineTo(W-padR, H-padB); ctx.stroke();
  for (let y=0; y<=10; y++){
    const py = padT + innerH - (y/10) * innerH;
    ctx.strokeStyle = '#22222220'; ctx.beginPath(); ctx.moveTo(padL, py); ctx.lineTo(W-padR, py); ctx.stroke();
    ctx.fillStyle = muted; ctx.fillText(`${y*10}%`, 8, py+4);
  }
  const iters = Object.keys(byIter).map(Number).filter(k=>k>0).sort((a,b)=>a-b);
  if (!iters.length) return;
  const xFor = (it) => padL + ((it-iters[0]) / Math.max(1, iters[iters.length-1]-iters[0])) * innerW;
  iters.forEach(it => {
    const x = xFor(it);
    ctx.fillStyle = muted; ctx.fillText(`iter ${it}`, x-15, H-padB+18);
  });
  // diag line
  ctx.strokeStyle = '#94a3b8'; ctx.lineWidth = 2; ctx.beginPath();
  iters.forEach((it,i) => {
    const v = byIter[String(it)].diag;
    const x = xFor(it), y = padT + innerH - v * innerH;
    if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.stroke();
  // post line
  ctx.strokeStyle = '#2563eb'; ctx.lineWidth = 2.5; ctx.beginPath();
  iters.forEach((it,i) => {
    const v = byIter[String(it)].post;
    const x = xFor(it), y = padT + innerH - v * innerH;
    if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.stroke();
  // legend
  ctx.fillStyle = '#94a3b8'; ctx.fillRect(padL, padT-12, 12, 2); ctx.fillText('cohort trước (diag)', padL+18, padT-6);
  ctx.fillStyle = '#2563eb'; ctx.fillRect(padL+140, padT-12, 12, 2); ctx.fillText('cohort sau (post)', padL+158, padT-6);
}

function renderTable(byIter){
  const tbody = document.querySelector('#cohort-table tbody');
  tbody.innerHTML = '';
  const iters = Object.keys(byIter).map(Number).filter(k=>k>0).sort((a,b)=>a-b);
  iters.forEach(it => {
    const v = byIter[String(it)];
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${it}</td><td>${(v.diag*100).toFixed(1)}%</td><td>${(v.post*100).toFixed(1)}%</td>
                    <td>${v.gain_pp>=0?'+':''}${v.gain_pp.toFixed(2)}</td><td>${v.active_learners}</td><td>${v.cum_distinct_learners}</td>`;
    tbody.appendChild(tr);
  });
}

function renderPerLang(personal, byIter){
  const grid = document.getElementById('per-lang-grid');
  const iters = Object.keys(byIter).map(Number).filter(k=>k>0).sort((a,b)=>a-b);
  const lastPost = iters.length ? byIter[String(iters[iters.length-1])].post : 0;
  grid.innerHTML = '';
  for (const lang of ['python']){
    const me = personal && personal[lang];
    const delta = me!=null ? Math.round((me - lastPost) * 1000)/10 : null;
    const card = document.createElement('div');
    card.className = 'kpi-card';
    card.innerHTML = `
      <div class="kpi-label">${lang}</div>
      <div class="kpi-val">${me==null?'—':Math.round(me*100)+'%'}</div>
      <div class="kpi-label">${delta==null?'chưa có dữ liệu':((delta>=0?'+':'')+delta+'pp so với cohort')}</div>
      <a href="/lang/${lang}" class="cta">Mở →</a>`;
    grid.appendChild(card);
  }
}

async function render(){
  const cohort = await fetch('/api/cohort_progress').then(r=>r.json());
  drawChart(document.getElementById('cohort-chart'), cohort.by_iter);
  renderTable(cohort.by_iter);
  renderPerLang(getPersonal(), cohort.by_iter);
}
render();
})();
