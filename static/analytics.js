// Cookieless analytics + waitlist + CTA tracking — KHÔNG cookie, KHÔNG PII.
// Anonymous client-id lưu localStorage; gửi event qua /api/event (sendBeacon).
(function () {
  function rid() { return 'c_' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36); }
  function cid() {
    try {
      let c = localStorage.getItem('cid');
      if (!c) { c = rid(); localStorage.setItem('cid', c); }
      return c;
    } catch (e) { return 'c_anon'; }
  }
  function utm() {
    try {
      const p = new URLSearchParams(location.search), o = {};
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
        .forEach(k => { const v = p.get(k); if (v) o[k] = v.slice(0, 80); });
      if (Object.keys(o).length) { localStorage.setItem('utm', JSON.stringify(o)); return o; }
      const s = localStorage.getItem('utm'); return s ? JSON.parse(s) : {};
    } catch (e) { return {}; }
  }
  function track(name, props) {
    try {
      const body = JSON.stringify({
        name: name, cid: cid(), path: location.pathname,
        ref: document.referrer || '', utm: utm(), props: props || {}
      });
      if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/event', new Blob([body], { type: 'application/json' }));
      } else {
        fetch('/api/event', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: body, keepalive: true }).catch(() => {});
      }
    } catch (e) {}
  }
  async function joinWaitlist(email, source, persona) {
    const ctrl = ('AbortController' in window) ? new AbortController() : null;
    const t = ctrl ? setTimeout(() => ctrl.abort(), 8000) : null;
    try {
      const r = await fetch('/api/waitlist', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        signal: ctrl ? ctrl.signal : undefined,
        body: JSON.stringify({ email: email, source: source || '', persona: persona || '', ref: document.referrer || '', utm: utm() })
      });
      return r.json();
    } finally { if (t) clearTimeout(t); }
  }
  window.Analytics = { cid, track, utm, joinWaitlist };

  // ---- Auto-wiring ----
  function wire() {
    // page view
    track('page_view', { title: document.title });

    // any element with data-track="event_name" → track on click
    document.querySelectorAll('[data-track]').forEach(el => {
      el.addEventListener('click', () => {
        let props = {};
        try { props = el.dataset.trackProps ? JSON.parse(el.dataset.trackProps) : {}; } catch (e) {}
        track(el.dataset.track, props);
      });
    });

    // waitlist form (id=waitlist-form, input#wl-email, msg#wl-msg, optional data-source/data-persona)
    const f = document.getElementById('waitlist-form');
    if (f) {
      f.addEventListener('submit', async ev => {
        ev.preventDefault();
        const inp = document.getElementById('wl-email');
        const msg = document.getElementById('wl-msg');
        const email = (inp && inp.value || '').trim();
        if (!email) return;
        track('waitlist_submit', { source: f.dataset.source || '' });
        if (msg) msg.textContent = 'Đang gửi…';
        try {
          const res = await joinWaitlist(email, f.dataset.source || 'landing', f.dataset.persona || '');
          if (res && res.ok) {
            if (msg) msg.textContent = '✓ Đã ghi nhận! Bạn sẽ là người đầu tiên nhận bản Pro.';
            if (inp) inp.value = '';
            track('waitlist_ok', { source: f.dataset.source || '' });
          } else {
            if (msg) msg.textContent = (res && res.error) || 'Email không hợp lệ, thử lại nhé.';
          }
        } catch (e) {
          if (msg) msg.textContent = 'Lỗi mạng, thử lại sau.';
        }
      });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
