/* lang_rust.js — Rust-specific hints (Rust Book, r/rust, Exercism Rust, awesome-rust). */
(function(){
const HINTS = {
  "borrow_lifetime_elision": "Lifetime elision rules: 1 input lifetime → output gets it; &self method → output gets &self lifetime. When 0 inputs OR multiple, explicit annotation required. (Rust Book ch 10)",
  "move_vs_borrow":          "Assignment/passing of a non-Copy type MOVES ownership. Use & to borrow, &mut for exclusive borrow. After move, original binding is invalid. (r/rust)",
  "sized_unsized":           "?Sized opt-out lets generic types accept unsized types (str, [T], dyn Trait). Default trait bound is Sized. (Rust Book)",
  "drop_order_field":        "Struct fields drop in DECLARATION order; tuple in left-to-right; locals in REVERSE of binding. Drop interleavings can matter for handles. (Exercism Rust)",
  "unsafe_send_sync":        "Send/Sync are auto-traits — implemented automatically if all fields are. Manual impl in unsafe block is your assertion you've upheld the invariant. (Rust Book, r/rust)",
};
const PATTERN_HINTS = [
  [/<\s*'\w+\s*>|fn\s+\w+\s*<\s*'\w+/, "borrow_lifetime_elision"],
  [/let\s+\w+\s*=\s*\w+\s*;?\s*$|fn\s+\w+\s*\([^)]*\w+:\s*\w+(?!&)/, "move_vs_borrow"],
  [/\?Sized|dyn\s+\w+/, "sized_unsized"],
  [/struct\s+\w+/, "drop_order_field"],
  [/unsafe\s+impl\s+(Send|Sync)/, "unsafe_send_sync"],
];
function fire(hintIds){
  const ul = document.getElementById('lang-hint-active');
  if (!ul) return;
  if (!hintIds.length){ ul.innerHTML = '<li class="hint">No Rust-specific hint for this question.</li>'; return; }
  ul.innerHTML = hintIds.map(id => `<li><strong>${id}</strong>: ${HINTS[id] || ''}</li>`).join('');
}
window.LANG_HINTS_RUST = function(q){
  if (q.lang !== 'rust') return;
  const ids = new Set();
  if (HINTS[q.kc_tag]) ids.add(q.kc_tag);
  for (const [pat, id] of PATTERN_HINTS){
    if (pat.test(q.code)) ids.add(id);
  }
  fire(Array.from(ids));
};
})();
