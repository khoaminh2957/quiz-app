/* lang_switcher.js — Web đã thu hẹp về Python; giữ Alt+1 làm phím tắt về dashboard Python. */
(function(){
document.addEventListener('keydown', (e) => {
  if (!e.altKey) return;
  if (document.activeElement && /input|textarea|select/i.test(document.activeElement.tagName)) return;
  if (e.key !== '1') return;
  e.preventDefault();
  location.href = '/lang/python';
});
})();
