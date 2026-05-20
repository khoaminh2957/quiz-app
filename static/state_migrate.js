/* state_migrate.js — localStorage migration + safe API with quota + corruption recovery.
 * - Forward-migrates legacy `roadmap_state` (v1) to `state.per_lang[lang]` (v2).
 * - Caps stage_attempts to last 200 per stage (DOM-bug-hunter P0: unbounded growth).
 * - Detects parse failure & quota errors; surfaces banner instead of silent loss.
 * - Reads prefers-color-scheme when no theme stored (a11y agent: theme system pref).
 */
(function(){
const SCHEMA_V = 2;
const MAX_ATTEMPTS_PER_STAGE = 200;
const MAX_KC_HISTORY = 50;

function showBanner(msg, kind){
  if (document.getElementById('lc-banner')) return;
  const b = document.createElement('div');
  b.id = 'lc-banner';
  b.setAttribute('role', 'alert');
  b.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;padding:10px 16px;'
    + 'background:' + (kind==='error' ? '#b91c1c' : '#b45309') + ';color:white;font-size:14px;text-align:center;';
  b.innerHTML = msg + ' <button type="button" id="lc-banner-close" aria-label="Đóng cảnh báo" style="margin-left:12px;background:rgba(255,255,255,.2);border:0;color:white;padding:4px 8px;border-radius:4px;cursor:pointer;">✕</button>';
  document.body.appendChild(b);
  document.getElementById('lc-banner-close').onclick = () => b.remove();
}

function readJSON(k){
  let raw;
  try { raw = localStorage.getItem(k); }
  catch(e){ return {value:null, error:'storage-unavailable'}; }
  if (!raw) return {value:null};
  try { return {value: JSON.parse(raw)}; }
  catch(e){
    // Preserve corrupt blob for recovery instead of clobbering silently.
    try { localStorage.setItem(`${k}_corrupt_${Date.now()}`, raw); } catch(_){}
    return {value:null, error:'parse-error'};
  }
}
function writeJSON(k, v){
  try {
    localStorage.setItem(k, JSON.stringify(v));
    return true;
  } catch(e){
    if (e && e.name === 'QuotaExceededError') {
      showBanner('Bộ nhớ trình duyệt đã đầy. Vào Mức độ thành thạo để xoá dữ liệu cũ.', 'error');
    }
    return false;
  }
}

function emptyLangState(){
  return {cur:null, kc_mastery:{}, last_review:{}, stage_attempts:{}, q_box:{}};
}
function emptyGamification(){
  return {
    xp_total: 0,
    streak: {current: 0, longest: 0, last_active_date: null, history: []},
    weekly: {week_start: null, earned: 0, goal: 200, history: []},
    daily_completed: {},  // {date: bool}
    badges_earned: [],
    last_celebration: {},  // {stage_id: date} — show once per stage gate
  };
}

function migrate(){
  const cur = readJSON('state');
  if (cur.error === 'parse-error') {
    showBanner('Dữ liệu local bị lỗi. Đã sao lưu bản cũ; tạo lại state mới.', 'warn');
  }
  if (cur.value && cur.value.schema_v === SCHEMA_V) return cur.value;

  const legacy = readJSON('roadmap_state');
  const s = { schema_v: SCHEMA_V, current_lang: 'python', per_lang: {}, gamification: emptyGamification() };
  for (const L of ['python','javascript','go','rust','sql']){
    s.per_lang[L] = emptyLangState();
  }
  if (legacy.value && (legacy.value.kc_mastery || legacy.value.stage_attempts || legacy.value.last_review || legacy.value.q_box)){
    Object.assign(s.per_lang.python, {
      kc_mastery: legacy.value.kc_mastery || {},
      last_review: legacy.value.last_review || {},
      stage_attempts: legacy.value.stage_attempts || {},
      q_box: legacy.value.q_box || {},
      _migrated_from_v1: true,
    });
  }
  writeJSON('state', s);
  return s;
}

window.STATE = migrate();
// Backfill gamification for users on schema v2 who pre-date the gamification field
if (!window.STATE.gamification) { window.STATE.gamification = emptyGamification(); writeJSON('state', window.STATE); }

window.QUIZ_STATE_API = {
  get: function(lang){ return window.STATE.per_lang[lang] || emptyLangState(); },
  save: function(){ return writeJSON('state', window.STATE); },
  setCurrentLang: function(lang){ window.STATE.current_lang = lang; return this.save(); },
  recordAttempt: function(lang, q, chosen, correct){
    const ls = this.get(lang);
    const isFirstTry = !ls.stage_attempts[q.stage_id] || !ls.stage_attempts[q.stage_id].some(a => a.qid === q.id);
    ls.stage_attempts[q.stage_id] = ls.stage_attempts[q.stage_id] || [];
    ls.stage_attempts[q.stage_id].push({qid:q.id, chosen, correct, ts:Date.now()});
    if (ls.stage_attempts[q.stage_id].length > MAX_ATTEMPTS_PER_STAGE) {
      ls.stage_attempts[q.stage_id] = ls.stage_attempts[q.stage_id].slice(-MAX_ATTEMPTS_PER_STAGE);
    }
    ls.kc_mastery[q.kc_tag] = ls.kc_mastery[q.kc_tag] || [];
    ls.kc_mastery[q.kc_tag].push({qid:q.id, correct, ts:Date.now()});
    if (ls.kc_mastery[q.kc_tag].length > MAX_KC_HISTORY) {
      ls.kc_mastery[q.kc_tag] = ls.kc_mastery[q.kc_tag].slice(-MAX_KC_HISTORY);
    }
    const LEITNER_DAYS = [1,3,7,16,35];
    const curBox = ls.q_box[q.id] || 1;
    const nextBox = correct ? Math.min(curBox+1, 5) : 1;
    ls.q_box[q.id] = nextBox;
    ls.last_review[q.id] = {ts:Date.now(), next_due_days: LEITNER_DAYS[nextBox-1]};
    // Gamification updates
    const g = window.STATE.gamification;
    let xpGain = correct ? (isFirstTry ? 10 : 5) : 0;
    if (correct && q.difficulty === 'hard') xpGain += 5;
    g.xp_total += xpGain;
    // Streak: today in ICT (UTC+7)
    const now = new Date();
    const ictMs = now.getTime() + (now.getTimezoneOffset()*60000) + (7*3600000);
    const today = new Date(ictMs).toISOString().slice(0,10);
    const last = g.streak.last_active_date;
    if (last !== today){
      if (last){
        const lastD = new Date(last + 'T00:00:00Z').getTime();
        const diff = Math.round((new Date(today + 'T00:00:00Z').getTime() - lastD) / 86400000);
        if (diff === 1) g.streak.current += 1;
        else if (diff > 1) g.streak.current = 1;
      } else {
        g.streak.current = 1;
      }
      g.streak.last_active_date = today;
      g.streak.longest = Math.max(g.streak.longest, g.streak.current);
      if (!g.streak.history.includes(today)) g.streak.history.push(today);
      if (g.streak.history.length > 365) g.streak.history = g.streak.history.slice(-365);
    }
    // Weekly goal — week starts Monday
    const dnow = new Date(today + 'T00:00:00Z');
    const dow = dnow.getUTCDay() || 7;  // 1=Mon, 7=Sun
    const monday = new Date(dnow.getTime() - (dow-1)*86400000).toISOString().slice(0,10);
    if (g.weekly.week_start !== monday){
      if (g.weekly.week_start){
        g.weekly.history.push({week_start: g.weekly.week_start, earned: g.weekly.earned, goal: g.weekly.goal, hit: g.weekly.earned >= g.weekly.goal});
        if (g.weekly.history.length > 12) g.weekly.history = g.weekly.history.slice(-12);
      }
      g.weekly.week_start = monday;
      g.weekly.earned = 0;
    }
    g.weekly.earned += xpGain;
    return this.save();
  },
  setWeeklyGoal: function(goal){
    const g = Math.max(50, Math.min(2000, parseInt(goal,10) || 200));
    window.STATE.gamification.weekly.goal = g;
    return this.save();
  },
  markDailyCompleted: function(){
    const now = new Date();
    const ictMs = now.getTime() + (now.getTimezoneOffset()*60000) + (7*3600000);
    const today = new Date(ictMs).toISOString().slice(0,10);
    window.STATE.gamification.daily_completed[today] = true;
    return this.save();
  },
};

// Theme — respect OS preference when user hasn't chosen
function getPreferredTheme(){
  try {
    const stored = localStorage.getItem('theme');
    if (stored === 'dark' || stored === 'light') return stored;
  } catch(_){}
  try {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
  } catch(_){}
  return 'light';
}
function applyTheme(t){ document.documentElement.setAttribute('data-theme', t); }
applyTheme(getPreferredTheme());

// Listen for OS theme change when user hasn't explicitly chosen
try {
  if (window.matchMedia){
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener || mq.addListener).call(mq, 'change', (e) => {
      if (!localStorage.getItem('theme')) applyTheme(e.matches ? 'dark' : 'light');
    });
  }
} catch(_){}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = cur === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('theme', next); } catch(_){}
  });
});
})();
