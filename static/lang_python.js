/* lang_python.js — Python-specific hint sidebar trigger.
 * Hints fire when q.kc_tag matches a Python-specific KC or pattern is detected.
 * Sources: Hermans 2021 (cognitive priming), MIT 6.0001, r/Python, awesome-python.
 */
(function(){
const HINTS = {
  "late_binding_closure":  "Python closures bind variables LATE — they capture the name, not the value. The classic [lambda i: i for i in range(3)] vs [lambda i=i: i for i in range(3)] gotcha. (r/Python, MIT 6.0001)",
  "list_default_mutable":  "Default arguments are evaluated ONCE at def-time. `def f(x=[])` keeps state across calls. Use `x=None` + `if x is None: x = []`. (Hermans 2021)",
  "f_string_quoting":      "f-string quoting before Python 3.12 cannot reuse the same quote char as the f-string delimiter. 3.12+ relaxed this (PEP-701). (awesome-python, MIT 6.0001)",
  "walrus_scope":          "Walrus `:=` creates a name in the ENCLOSING scope. Inside a comprehension, the name leaks to the enclosing function. (r/Python)",
  "gil_threading_limits":  "CPython GIL serializes Python bytecode across threads. Use multiprocessing for CPU-bound, asyncio/threads for I/O-bound. (MIT 6.0001, awesome-python)",
};
const PATTERN_HINTS = [
  // pattern → hint id
  [/def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|dict\(\)|list\(\))/, "list_default_mutable"],
  [/\[lambda.*for\s+\w+\s+in/,                            "late_binding_closure"],
  [/[\(\[][^)\]]*:=[^)\]]*[\)\]]/,                        "walrus_scope"],
  [/threading\.Thread|concurrent\.futures\.ThreadPoolExecutor|asyncio/, "gil_threading_limits"],
];
function fire(hintIds){
  const ul = document.getElementById('lang-hint-active');
  if (!ul) return;
  if (!hintIds.length){ ul.innerHTML = '<li class="hint">No Python-specific hint for this question.</li>'; return; }
  ul.innerHTML = hintIds.map(id => `<li><strong>${id}</strong>: ${HINTS[id] || ''}</li>`).join('');
}
window.LANG_HINTS_PYTHON = function(q){
  if (q.lang !== 'python') return;
  const ids = new Set();
  if (HINTS[q.kc_tag]) ids.add(q.kc_tag);
  for (const [pat, id] of PATTERN_HINTS){
    if (pat.test(q.code)) ids.add(id);
  }
  fire(Array.from(ids));
};
})();
