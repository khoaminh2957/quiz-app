/* improvements.js — render improvement_log.json + research_refs.json on /improvements. */
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

function drawGain(canvas, byIter){
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0,0,W,H);
  const padL = 50, padR = 20, padT = 20, padB = 40;
  const innerW = W - padL - padR, innerH = H - padT - padB;
  const iters = Object.keys(byIter).map(Number).filter(k=>k>0).sort((a,b)=>a-b);
  if (!iters.length) return;
  const gains = iters.map(it => byIter[String(it)].gain_pp);
  const maxG = Math.max(8, Math.max(...gains));
  ctx.strokeStyle = '#888'; ctx.beginPath(); ctx.moveTo(padL, padT); ctx.lineTo(padL, H-padB); ctx.lineTo(W-padR, H-padB); ctx.stroke();
  const bw = innerW / iters.length;
  ctx.font = '11px sans-serif'; ctx.fillStyle = '#888';
  iters.forEach((it, i) => {
    const g = byIter[String(it)].gain_pp;
    const h = (g / maxG) * innerH;
    const x = padL + i * bw + bw*0.2;
    const y = padT + innerH - h;
    ctx.fillStyle = g >= 1 ? '#2563eb' : '#dc2626';
    ctx.fillRect(x, y, bw*0.6, h);
    ctx.fillStyle = '#888';
    ctx.fillText(`${g.toFixed(1)}`, x, y-4);
    ctx.fillText(`i${it}`, x, H-padB+16);
  });
  ctx.fillStyle = '#888';
  ctx.fillText('cohort gain (pp)', padL, padT-6);
}

async function render(){
  const [imp, refs, cohort] = await Promise.all([
    fetch('/api/improvements').then(r=>r.json()),
    fetch('/api/research_refs').then(r=>r.json()),
    fetch('/api/cohort_progress').then(r=>r.json()),
  ]);
  drawGain(document.getElementById('gain-curve'), cohort.by_iter);

  const tl = document.getElementById('iter-timeline');
  tl.innerHTML = '';
  const byIter = {};
  for (const x of imp.improvements){
    (byIter[x.iter] = byIter[x.iter] || []).push(x);
  }
  for (let it = 1; it <= 10; it++){
    const its = byIter[it] || [];
    const g = cohort.by_iter[String(it)] || {};
    const div = document.createElement('div');
    div.className = 'iter-row';
    div.innerHTML = `<div class="iter-num">iter ${String(it).padStart(2,'0')}</div>
      <div class="iter-summary">
        <strong>${its.length} improvements</strong> · gain ${g.gain_pp!=null?(g.gain_pp>=0?'+':'')+g.gain_pp.toFixed(2)+'pp':'—'} ·
        active learners ${g.active_learners||0} · cum ${g.cum_distinct_learners||0}
        <div class="iter-cats">${Array.from(new Set(its.map(x=>x.category))).map(c => `<span class="badge cat-${c}">${c}</span>`).join(' ')}</div>
      </div>`;
    tl.appendChild(div);
  }

  const list = document.getElementById('imp-list');
  list.innerHTML = '';
  for (const x of imp.improvements){
    const li = document.createElement('div');
    li.className = 'imp-card';
    const srcs = (x.source_refs || []).map(rid => {
      const ref = (refs.refs||{})[rid];
      if (!ref) return rid;
      return `<a href="${ref.url}" target="_blank" rel="noopener">${ref.author||rid} ${ref.year||''}</a>`;
    }).join(' · ');
    li.innerHTML = `<div class="imp-head">
        <span class="badge cat-${x.category}">${x.category}</span>
        <span class="badge lang-${x.lang}">${x.lang}</span>
        <span>iter ${x.iter}</span>
        <code>${x.file}:${x.line_range}</code>
        <span class="muted">expected +${x.expected_delta_pp}pp</span>
      </div>
      <p>${x.rationale}</p>
      <div class="muted">sources: ${srcs} · pre_sha <code>${(x.pre_sha||'').slice(0,8)}</code></div>`;
    list.appendChild(li);
  }

  const refList = document.getElementById('ref-list');
  refList.innerHTML = '';
  for (const [id, ref] of Object.entries(refs.refs || {})){
    const div = document.createElement('div');
    div.className = 'ref-card';
    div.innerHTML = `<span class="badge cls-${ref.class}">${ref.class}</span>
      <strong>${ref.author || id}</strong> (${ref.year || ''})
      <em>${ref.title || ''}</em>
      <a href="${ref.url}" target="_blank" rel="noopener">${ref.venue || 'link'}</a>`;
    refList.appendChild(div);
  }
}
render();
})();
