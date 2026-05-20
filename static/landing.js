/* landing.js — Alt+1..5 to pick a lang from landing page */
(function(){
const LANGS = ['python','javascript','go','rust','sql'];
function applyTheme(t){ document.documentElement.setAttribute('data-theme', t); }
applyTheme(localStorage.getItem('theme') || 'light');
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('theme-toggle');
  btn && btn.addEventListener('click', () => {
    const n = (document.documentElement.getAttribute('data-theme')==='dark')?'light':'dark';
    applyTheme(n); localStorage.setItem('theme', n);
  });
});
document.addEventListener('keydown', (e) => {
  if (!e.altKey) return;
  const k = e.key;
  if (k < '1' || k > '5') return;
  const idx = parseInt(k) - 1;
  e.preventDefault();
  location.href = `/lang/${LANGS[idx]}`;
});
})();
