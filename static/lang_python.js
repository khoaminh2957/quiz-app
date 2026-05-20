/* lang_python.js — Hints riêng cho Python. Gợi ý kích hoạt khi q.kc_tag khớp hoặc pattern phát hiện trong code.
 * Nguồn: Hermans 2021 (cognitive priming), MIT 6.0001, r/Python, awesome-python.
 */
(function(){
const HINTS = {
  "late_binding_closure":  "Closure trong Python bind biến THEO TÊN, không phải theo giá trị. Bẫy điển hình: `[lambda i: i for i in range(3)]` vs `[lambda i=i: i for i in range(3)]`. (r/Python, MIT 6.0001)",
  "list_default_mutable":  "Default argument được đánh giá MỘT LẦN khi def. `def f(x=[])` sẽ giữ state qua các lần gọi. Dùng `x=None` + `if x is None: x = []`. (Hermans 2021)",
  "f_string_quoting":      "Trước Python 3.12, f-string không cho dùng cùng dấu nháy với delimiter. 3.12+ nới lỏng (PEP-701). (awesome-python, MIT 6.0001)",
  "walrus_scope":          "Walrus `:=` tạo tên ở scope BAO QUANH. Bên trong comprehension, tên rò ra function chứa nó. (r/Python)",
  "gil_threading_limits":  "GIL của CPython serialize bytecode Python qua các thread. Dùng multiprocessing cho CPU-bound; asyncio/threads cho I/O-bound. (MIT 6.0001, awesome-python)",
};
const PATTERN_HINTS = [
  [/def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|dict\(\)|list\(\))/, "list_default_mutable"],
  [/\[lambda.*for\s+\w+\s+in/,                            "late_binding_closure"],
  [/[\(\[][^)\]]*:=[^)\]]*[\)\]]/,                        "walrus_scope"],
  [/threading\.Thread|concurrent\.futures\.ThreadPoolExecutor|asyncio/, "gil_threading_limits"],
];
function fire(hintIds){
  const ul = document.getElementById('lang-hint-active');
  if (!ul) return;
  if (!hintIds.length){ ul.innerHTML = '<li class="hint">Không có gợi ý Python riêng cho câu này.</li>'; return; }
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
