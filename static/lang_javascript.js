/* lang_javascript.js — JS-specific hints (Sorva 2013 notional machine; fCC; awesome-javascript). */
(function(){
const HINTS = {
  "event_loop_microtask":  "JS microtasks (Promises, queueMicrotask) drain BEFORE macrotasks (setTimeout, setImmediate) on each tick. Surprising order: Promise.then runs before setTimeout(0). (fCC, Sorva 2013)",
  "this_binding":          "`this` in JS depends on CALL site: method call → object, free call → undefined (strict) or global. Arrow functions inherit `this` from enclosing scope. (awesome-javascript)",
  "truthy_coercion":       "`==` triggers ToPrimitive + ToNumber coercion; e.g. `[] == false` is true. Prefer `===` unless you actively want coercion. (r/learnprogramming)",
  "array_holes":           "`new Array(5)` creates a SPARSE array with 5 holes; `.map()` SKIPS holes, `.fill()` does not. (fCC)",
  "promise_unhandled":     "An unhandled Promise rejection silently surfaces as a console warning, NOT an exception. Always attach .catch or use try/catch + await. (awesome-javascript)",
};
const PATTERN_HINTS = [
  [/setTimeout|setImmediate|process\.nextTick|queueMicrotask|Promise\./, "event_loop_microtask"],
  [/\bthis\b.*function\s*\(|\bfunction\s*\([^)]*\)\s*{[^}]*this/, "this_binding"],
  [/==\s*(true|false|null|undefined|0|''|"")|(true|false|null|undefined|0|''|"")\s*==/, "truthy_coercion"],
  [/new Array\(\d+\)|Array\(\d+\)\.fill|\.map\(/, "array_holes"],
  [/\.then\(|new Promise|async\s+function/, "promise_unhandled"],
];
function fire(hintIds){
  const ul = document.getElementById('lang-hint-active');
  if (!ul) return;
  if (!hintIds.length){ ul.innerHTML = '<li class="hint">No JS-specific hint for this question.</li>'; return; }
  ul.innerHTML = hintIds.map(id => `<li><strong>${id}</strong>: ${HINTS[id] || ''}</li>`).join('');
}
window.LANG_HINTS_JAVASCRIPT = function(q){
  if (q.lang !== 'javascript') return;
  const ids = new Set();
  if (HINTS[q.kc_tag]) ids.add(q.kc_tag);
  for (const [pat, id] of PATTERN_HINTS){
    if (pat.test(q.code)) ids.add(id);
  }
  fire(Array.from(ids));
};
})();
