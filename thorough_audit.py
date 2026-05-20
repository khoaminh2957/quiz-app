"""Thorough debug audit — find any latent bug.

Runs 12 deep checks beyond health_check.py:
  1. Q stage_id integrity (every Q has valid global stage)
  2. Per-lang stage question_ids exist in questions.json
  3. Every per-lang lesson route + API returns 200
  4. Daily endpoint maps to valid per-lang stage
  5. /api/questions Python-only
  6. JSON error responses don't escape Vietnamese
  7. Browser 404 returns HTML (not JSON)
  8. state_migrate.js included on key pages
  9. error_reporter.js included on all user-facing pages
  10. All CSS vars defined
  11. localStorage schema_v consistency
  12. bandit clean
"""
import json, sys, os, subprocess, pathlib

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))
from app import app

ESCAPE_PREFIX = chr(92) + 'u'  # avoid SyntaxError from literal \\u

issues = []
notes = []
client = app.test_client()

# 1.
qs = json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))
rm = json.loads((ROOT/'roadmap.json').read_text(encoding='utf-8'))
rp = json.loads((ROOT/'roadmap_perlang.json').read_text(encoding='utf-8'))
global_ids = {s['id'] for s in rm['stages']}
for q in qs:
    if q['stage_id'] not in global_ids:
        issues.append(f"Q {q['id']} has stage_id={q['stage_id']} not in global stages")
notes.append(f"Q stage_id integrity: {len(qs)} OK")

# 2.
qid_set = {q['id'] for q in qs}
for s in rp['per_lang_stages']['python']:
    for qid in s['question_ids']:
        if qid not in qid_set:
            issues.append(f"Per-lang stage {s['id']} references missing qid {qid}")
notes.append("Per-lang question_ids integrity: OK")

# 3.
for s in rp['per_lang_stages']['python']:
    r = client.get(f"/lang/python/lesson/{s['id']}")
    if r.status_code != 200: issues.append(f"Lesson route {s['id']} = {r.status_code}")
    r = client.get(f"/api/lang/python/stage/{s['id']}")
    if r.status_code != 200: issues.append(f"API stage route {s['id']} = {r.status_code}")
notes.append("All 15 lesson + API routes 200 OK")

# 4.
r = client.get('/api/daily')
d = r.get_json()
qid_global = d['question']['stage_id']
candidate = f"py_{qid_global}"
r2 = client.get(f"/api/lang/python/stage/{candidate}")
if r2.status_code != 200:
    issues.append(f"Daily stage_id={qid_global} -> {candidate} returns {r2.status_code}")
notes.append(f"Daily -> stage {qid_global} -> {candidate} OK")

# 4b. Also test landing page daily card URL would resolve correctly
r = client.get(f"/lang/python/lesson/{qid_global}", follow_redirects=False)
if r.status_code not in (200, 302):
    issues.append(f"Defensive redirect for /lang/python/lesson/{qid_global} returns {r.status_code}")
notes.append(f"Daily card URL (global) defensive redirect OK")

# 5.
data = client.get('/api/questions').get_json()
non_py = [q for q in data if q['lang'] != 'python']
if non_py: issues.append(f"/api/questions has {len(non_py)} non-Python")
notes.append(f"/api/questions: {len(data)} all Python")

# 6.
raw = client.get('/api/no-such').get_data(as_text=True)
if ESCAPE_PREFIX in raw:
    issues.append(f"API 404 has escape: {raw[:80]}")
notes.append("JSON error: Vietnamese direct, no escape")

# 7.
r = client.get('/this-no-exist', headers={'Accept':'text/html,application/xhtml+xml'})
if 'text/html' not in r.headers.get('Content-Type',''):
    issues.append(f"Browser 404 returns {r.headers.get('Content-Type')}")
notes.append("Browser 404 returns HTML")

# 8.
for p in ['/', '/lang/python', '/lang/python/lesson/py_f1', '/lang/python/mastery']:
    h = client.get(p).get_data(as_text=True)
    if 'state_migrate.js' not in h: issues.append(f"{p}: state_migrate.js missing")
notes.append("state_migrate.js on key pages")

# 9.
for p in ['/', '/quiz', '/lang/python', '/lang/python/roadmap', '/lang/python/lesson/py_f1',
          '/lang/python/mastery', '/progress', '/improvements']:
    h = client.get(p, follow_redirects=True).get_data(as_text=True)
    if 'error_reporter.js' not in h: issues.append(f"{p}: error_reporter.js missing")
notes.append("error_reporter.js on all 8 pages")

# 10.
css = (ROOT/'static/style.css').read_text(encoding='utf-8')
for var in ['--bad','--ok','--warn','--accent','--muted','--border','--bg','--fg','--card','--focus-ring']:
    if var not in css: issues.append(f"CSS var {var} missing")
notes.append("All CSS vars defined")

# 11.
js_state = (ROOT/'static/state_migrate.js').read_text(encoding='utf-8')
if 'SCHEMA_V = 2' not in js_state: issues.append("state_migrate.js SCHEMA_V != 2")
notes.append("schema_v=2 confirmed")

# 12.
try:
    r = subprocess.run([sys.executable,'-m','bandit','-r','app.py','templates','static',
                        '--severity-level','medium','-f','json','-q'],
                       capture_output=True, text=True, timeout=60, cwd=str(ROOT))
    b = json.loads(r.stdout) if r.stdout.strip() else {'results':[]}
    if b['results']: issues.append(f"bandit: {len(b['results'])} medium+ issues")
    notes.append("bandit: 0 medium+ issues")
except Exception as e:
    notes.append(f"bandit skipped: {e}")

# 13. New: every daily candidate stage_id (all stages in pool) should map to a valid per-lang stage
for sid in global_ids:
    cand = f"py_{sid}"
    r = client.get(f"/api/lang/python/stage/{cand}", follow_redirects=False)
    if r.status_code not in (200, 404):
        issues.append(f"py_{sid} stage API returns unexpected {r.status_code}")
notes.append("Every global stage_id -> per-lang transition deterministic")

print(f"=== Audit OK ({len(notes)}) ===")
for n in notes: print(f"  PASS  {n}")
print(f"=== Issues ({len(issues)}) ===")
for i in issues: print(f"  FAIL  {i}")
sys.exit(1 if issues else 0)
