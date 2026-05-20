/* error_reporter.js — capture JS runtime errors + unhandled promise rejections and POST
 * to /api/client_errors. Server-side decides whether to log (always logs in current setup).
 * Best-effort; ignores its own failures to avoid cascading.
 */
(function(){
let sent = 0;
const MAX_PER_SESSION = 10;
function send(payload){
  if (sent >= MAX_PER_SESSION) return;
  sent++;
  try {
    fetch('/api/client_errors', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(()=>{});
  } catch(_){}
}
window.addEventListener('error', (e) => {
  send({
    msg: e.message || 'error',
    src: e.filename || '',
    line: e.lineno || 0,
    col: e.colno || 0,
    url: location.href,
    ua: navigator.userAgent,
  });
});
window.addEventListener('unhandledrejection', (e) => {
  const reason = e.reason;
  const msg = reason && (reason.message || String(reason)) || 'unhandled-rejection';
  send({
    msg: 'UnhandledRejection: ' + msg,
    src: '',
    url: location.href,
    ua: navigator.userAgent,
  });
});
})();
