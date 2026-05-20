/* lang_switcher.js — Alt+1..5 to switch lang; navigates to matching route on current page-type */
(function(){
const LANGS = ['python','javascript','go','rust','sql'];
function pageType(){
  const p = location.pathname;
  if (p.startsWith('/lang/')){
    const parts = p.split('/');
    // /lang/<lang>/<rest...>
    return { kind: parts.slice(3).join('/') || '', curLang: parts[2] };
  }
  return { kind: null, curLang: null };
}
document.addEventListener('keydown', (e) => {
  if (!e.altKey) return;
  if (document.activeElement && /input|textarea|select/i.test(document.activeElement.tagName)) return;
  const k = e.key;
  if (k < '1' || k > '5') return;
  const idx = parseInt(k) - 1;
  const lang = LANGS[idx];
  const pt = pageType();
  let target;
  if (pt.kind === null){
    target = `/lang/${lang}`;
  } else if (pt.kind === ''){
    target = `/lang/${lang}`;
  } else {
    target = `/lang/${lang}/${pt.kind}`;
  }
  // For lesson, can't carry stage_id across langs (different IDs); fall back to roadmap.
  if (pt.kind && pt.kind.startsWith('lesson/')){
    target = `/lang/${lang}/roadmap`;
  }
  e.preventDefault();
  location.href = target;
});
})();
