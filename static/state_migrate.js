/* state_migrate.js — one-time forward migration of legacy roadmap_state into state.per_lang[lang] */
(function(){
const SCHEMA_V = 2; // bumped from 1 (flat global) to 2 (per-lang partition)
function readJSON(k){ try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch(e){ return null; } }
function writeJSON(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }

function emptyLangState(){
  return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, q_box:{}};
}

function migrate(){
  let s = readJSON('state');
  if (s && s.schema_v === SCHEMA_V) return s;
  // Forward migration from legacy `roadmap_state` (schema_v 1).
  const legacy = readJSON('roadmap_state');
  s = { schema_v: SCHEMA_V, current_lang: 'python', per_lang: {} };
  for (const L of ['python','javascript','go','rust','sql']){
    s.per_lang[L] = emptyLangState();
  }
  if (legacy && (legacy.kc_mastery || legacy.stage_attempts || legacy.last_review || legacy.q_box)){
    // The legacy state was lang-agnostic; preserve it under "python" track as the default,
    // tagged with a migrate-marker so users know it's a one-time forward bucket.
    Object.assign(s.per_lang.python, {
      kc_mastery: legacy.kc_mastery || {},
      last_review: legacy.last_review || {},
      stage_attempts: legacy.stage_attempts || {},
      q_box: legacy.q_box || {},
      _migrated_from_v1: true,
    });
  }
  writeJSON('state', s);
  return s;
}

window.STATE = migrate();
window.QUIZ_STATE_API = {
  get: function(lang){ return window.STATE.per_lang[lang] || emptyLangState(); },
  save: function(){ writeJSON('state', window.STATE); },
  setCurrentLang: function(lang){ window.STATE.current_lang = lang; this.save(); },
  recordAttempt: function(lang, q, chosen, correct){
    const ls = this.get(lang);
    ls.stage_attempts[q.stage_id] = ls.stage_attempts[q.stage_id] || [];
    ls.stage_attempts[q.stage_id].push({qid:q.id, chosen, correct, ts:Date.now()});
    ls.kc_mastery[q.kc_tag] = ls.kc_mastery[q.kc_tag] || [];
    ls.kc_mastery[q.kc_tag].push({qid:q.id, correct, ts:Date.now()});
    if (ls.kc_mastery[q.kc_tag].length > 50) ls.kc_mastery[q.kc_tag] = ls.kc_mastery[q.kc_tag].slice(-50);
    const LEITNER_DAYS = [1,3,7,16,35];
    const curBox = ls.q_box[q.id] || 1;
    const nextBox = correct ? Math.min(curBox+1, 5) : 1;
    ls.q_box[q.id] = nextBox;
    ls.last_review[q.id] = {ts:Date.now(), next_due_days: LEITNER_DAYS[nextBox-1]};
    this.save();
  },
};
// Theme toggle global wiring
function applyTheme(t){ document.documentElement.setAttribute('data-theme', t); }
applyTheme(localStorage.getItem('theme') || 'light');
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('theme-toggle');
  btn && btn.addEventListener('click', () => {
    const n = (document.documentElement.getAttribute('data-theme')==='dark')?'light':'dark';
    applyTheme(n); localStorage.setItem('theme', n);
  });
});
})();
