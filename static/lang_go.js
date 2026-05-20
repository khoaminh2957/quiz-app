/* lang_go.js — Go-specific hints (Go Proverbs, r/golang, awesome-go, Exercism Go). */
(function(){
const HINTS = {
  "nil_interface_vs_value": "An interface holding a typed nil is NOT == nil. `var p *T; var i I = p; i == nil` is FALSE because i has type *T. (Go Proverbs)",
  "goroutine_leak":         "Goroutines blocked on channels/locks leak silently. Wire ctx.Done() or close-channel signaling. (awesome-go, r/golang)",
  "slice_aliasing":         "Slices share underlying arrays; append CAN mutate the parent if cap > len. Make a fresh slice when handing to callers you don't trust. (Go Proverbs)",
  "range_loop_var":         "Pre-Go 1.22: loop variable is reused across iterations — a goroutine capturing it sees the last value. Fixed in 1.22 with per-iter scoping. (r/golang)",
  "defer_in_loop":          "defer runs at FUNCTION exit, not block exit; defer inside a loop accumulates calls. Wrap the body in a func or call explicitly. (Exercism Go)",
};
const PATTERN_HINTS = [
  [/interface\{?\}?|var\s+\w+\s+\w+\s*=\s*\(\*?\w+\)\(nil\)/, "nil_interface_vs_value"],
  [/go\s+func|chan\s+\w+|<-/, "goroutine_leak"],
  [/append\(|\bslice\b/, "slice_aliasing"],
  [/for\s+\w+,?\s*\w+\s*:=\s*range\s+/, "range_loop_var"],
  [/for\s+.*\{[\s\S]*defer\s+/, "defer_in_loop"],
];
function fire(hintIds){
  const ul = document.getElementById('lang-hint-active');
  if (!ul) return;
  if (!hintIds.length){ ul.innerHTML = '<li class="hint">No Go-specific hint for this question.</li>'; return; }
  ul.innerHTML = hintIds.map(id => `<li><strong>${id}</strong>: ${HINTS[id] || ''}</li>`).join('');
}
window.LANG_HINTS_GO = function(q){
  if (q.lang !== 'go') return;
  const ids = new Set();
  if (HINTS[q.kc_tag]) ids.add(q.kc_tag);
  for (const [pat, id] of PATTERN_HINTS){
    if (pat.test(q.code)) ids.add(id);
  }
  fire(Array.from(ids));
};
})();
