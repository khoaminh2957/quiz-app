/* celebration.js — confetti + modal khi đạt mastery gate (Exercism-style milestone) */
(function(){
function todayICT(){
  const now = new Date();
  const ictMs = now.getTime() + (now.getTimezoneOffset()*60000) + (7*3600000);
  return new Date(ictMs).toISOString().slice(0,10);
}

const ENCOURAGEMENTS_FIRST = [
  "Bạn vừa thông thạo một KC quan trọng.",
  "Sẵn sàng review code Python ở mức này rồi đấy.",
  "Một nấc thang mới — tiếp tục đà nhé.",
];
const ENCOURAGEMENTS_REPEAT = [
  "Bạn đã củng cố lại stage này — kiến thức bền hơn rồi.",
  "Refresh tốt — Leitner sẽ giảm tần suất ôn câu này.",
];

function pickMsg(prev){
  const pool = prev ? ENCOURAGEMENTS_REPEAT : ENCOURAGEMENTS_FIRST;
  return pool[Math.floor(Math.random()*pool.length)];
}

function spawnConfetti(){
  const c = document.createElement('canvas');
  c.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9998;';
  c.width = window.innerWidth; c.height = window.innerHeight;
  document.body.appendChild(c);
  const ctx = c.getContext('2d');
  const colors = ['#1d4ed8','#15803d','#b45309','#b91c1c','#7c3aed'];
  const particles = [];
  for (let i=0;i<80;i++){
    particles.push({
      x: Math.random()*c.width, y: -20,
      vx: (Math.random()-0.5)*4, vy: Math.random()*4+2,
      size: Math.random()*6+4, color: colors[i%colors.length],
      rot: Math.random()*Math.PI, vrot: (Math.random()-0.5)*0.2,
    });
  }
  let frames = 0;
  function tick(){
    ctx.clearRect(0,0,c.width,c.height);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.rot += p.vrot;
      ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot); ctx.fillStyle = p.color;
      ctx.fillRect(-p.size/2, -p.size/2, p.size, p.size); ctx.restore();
    });
    frames++;
    if (frames < 180) requestAnimationFrame(tick);
    else c.remove();
  }
  tick();
}

window.SHOW_MASTERY_CELEBRATION = function(stage, accPct){
  if (!window.STATE || !window.STATE.gamification) return;
  const g = window.STATE.gamification;
  g.last_celebration = g.last_celebration || {};
  const today = todayICT();
  // Show once per stage per day to avoid spam
  const key = `${stage.id}|${today}`;
  if (g.last_celebration[key]) return;
  g.last_celebration[key] = true;
  if (window.QUIZ_STATE_API) window.QUIZ_STATE_API.save();

  const prev = Object.keys(g.last_celebration).some(k => k.startsWith(stage.id + '|') && k !== key);
  const msg = pickMsg(prev);
  const modal = document.createElement('div');
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'cel-h');
  modal.style.cssText = 'position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;padding:20px;';
  modal.innerHTML = `
    <div class="card" style="max-width:480px;padding:24px;text-align:center;">
      <h2 id="cel-h" style="margin:0 0 8px 0;color:var(--ok);"><span aria-hidden="true">🎉</span> Đạt gate mastery!</h2>
      <p style="margin:6px 0;font-size:15px;"><strong>${stage.title}</strong></p>
      <p class="muted">${Math.round(accPct*100)}% trên 20 câu gần nhất · gate ${Math.round(stage.mastery_gate*100)}%</p>
      <p style="margin:14px 0;">${msg}</p>
      <button type="button" id="cel-close" class="cta" style="margin-top:8px;">Tiếp tục</button>
    </div>
  `;
  document.body.appendChild(modal);
  spawnConfetti();
  const closeBtn = document.getElementById('cel-close');
  closeBtn.focus();
  function close(){ modal.remove(); }
  closeBtn.onclick = close;
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  document.addEventListener('keydown', function escClose(e){
    if (e.key === 'Escape'){ close(); document.removeEventListener('keydown', escClose); }
  });
};
})();
