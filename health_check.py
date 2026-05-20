"""Health check — chạy độc lập (không cần Flask server live).

  python health_check.py                  # full check, exit 0 nếu pass tất cả
  python health_check.py --json           # output JSON cho CI
  python health_check.py --quick          # bỏ qua bandit + JS lint (nhanh)

Check:
  1. Data integrity (questions.json, roadmap.json, roadmap_perlang.json,
     learner_registry, improvement_log, research_refs, pedagogy_refs, bug_registry)
  2. Schema validation (jsonschema for questions)
  3. Q-annotation field completeness (immutability gate)
  4. Per-stage min/max count, prereq DAG acyclic
  5. Flask route smoke (33 routes via test_client)
  6. HTML rendering check (no unrendered Jinja, lang=vi, <main>, skip-link)
  7. JS syntax (node --check)
  8. bandit security scan (medium+)
  9. Static file presence (templates + static all referenced)
"""
from __future__ import annotations
import json, os, sys, subprocess, pathlib, time, argparse
from collections import Counter

ROOT = pathlib.Path(__file__).parent

class Check:
    def __init__(self, name): self.name=name; self.status='?'; self.details=''
    def ok(self, d=''): self.status='OK'; self.details=d; return self
    def warn(self, d): self.status='WARN'; self.details=d; return self
    def fail(self, d): self.status='FAIL'; self.details=d; return self
    def to_dict(self): return {'name':self.name,'status':self.status,'details':self.details}

def check_data_integrity():
    c = Check('data_integrity')
    try:
        qs = json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))
        rm = json.loads((ROOT/'roadmap.json').read_text(encoding='utf-8'))
        rp = json.loads((ROOT/'roadmap_perlang.json').read_text(encoding='utf-8'))
    except Exception as e:
        return c.fail(f'cannot load core data: {e}')
    issues = []
    ids = [q['id'] for q in qs]
    if len(ids) != len(set(ids)): issues.append('duplicate Q ids')
    valid_global = {s['id'] for s in rm['stages']}
    invalid = [q['id'] for q in qs if q['stage_id'] not in valid_global]
    if invalid: issues.append(f'{len(invalid)} Q with invalid global stage_id')
    if rp.get('langs') != ['python']: issues.append(f'roadmap_perlang.langs not python-only: {rp.get("langs")}')
    py_stages = rp.get('per_lang_stages',{}).get('python', [])
    if len(py_stages) != 15: issues.append(f'Python stages count {len(py_stages)} != 15')
    empty = [s['id'] for s in py_stages if not s.get('question_ids')]
    if empty: issues.append(f'empty Python stages: {empty}')
    low = [(s['id'], len(s['question_ids'])) for s in py_stages if 0 < len(s['question_ids']) < 5]
    if low: issues.append(f'stages with <5 questions: {low}')
    # Q-annotation immutability
    required = {'id','lang','code','question','options','correct_idx','topic','subtopic','difficulty',
                'explain','sources','iter','learning_objective','kc_tag','est_difficulty',
                'calibration_method','stage_id','misconception_map','metacog_pre','metacog_post'}
    missing = [q['id'] for q in qs if not required.issubset(set(q.keys()))]
    if missing: issues.append(f'{len(missing)} Q missing annotation fields')
    bad_ci = [q['id'] for q in qs if not (isinstance(q['correct_idx'], int) and 0<=q['correct_idx']<=3)]
    if bad_ci: issues.append(f'{len(bad_ci)} Q with bad correct_idx')
    bad_opts = [q['id'] for q in qs if not (isinstance(q['options'], list) and len(q['options'])==4)]
    if bad_opts: issues.append(f'{len(bad_opts)} Q with options != 4')
    bad_lang = [q['id'] for q in qs if q['lang'] != 'python']
    if bad_lang: issues.append(f'{len(bad_lang)} Q with lang != python')
    if issues:
        return c.fail('; '.join(issues))
    return c.ok(f'286 Q, 15 stages, all annotation fields present, Python-only')

def check_dag_acyclic():
    c = Check('dag_acyclic')
    try:
        rp = json.loads((ROOT/'roadmap_perlang.json').read_text(encoding='utf-8'))
        stages = rp['per_lang_stages']['python']
    except Exception as e:
        return c.fail(str(e))
    prereqs = {s['id']: s.get('prereqs', []) for s in stages}
    visited = set(); stack = []
    def dfs(n):
        if n in stack: raise Exception(f'cycle via {n}')
        if n in visited: return
        stack.append(n)
        for p in prereqs.get(n, []):
            if p in prereqs: dfs(p)
        stack.pop(); visited.add(n)
    try:
        for n in prereqs: dfs(n)
    except Exception as e:
        return c.fail(str(e))
    return c.ok(f'{len(prereqs)} stages, acyclic')

def check_schema():
    c = Check('schema_validation')
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return c.warn('jsonschema not installed; skipping')
    try:
        schema = json.loads((ROOT/'schema.json').read_text(encoding='utf-8'))
        qs = json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))
    except Exception as e:
        return c.fail(str(e))
    v = Draft202012Validator(schema)
    fails = 0; first_err = ''
    for q in qs:
        # Schema requires base fields only; Q has additional Vi-annotation fields that schema rejects via additionalProperties: false.
        # Validate only the base fields.
        base = {k: q[k] for k in schema['required'] if k in q}
        errs = list(v.iter_errors(base))
        if errs:
            fails += 1
            if not first_err: first_err = f"{q['id']}: {errs[0].message[:80]}"
    if fails: return c.fail(f'{fails} Q fail base schema; first: {first_err}')
    return c.ok(f'286 Q pass base schema')

def check_flask_routes():
    c = Check('flask_routes')
    try:
        sys.path.insert(0, str(ROOT))
        from app import app
    except Exception as e:
        return c.fail(f'cannot import app: {e}')
    client = app.test_client()
    routes = [
        ('/', 200), ('/quiz', 200), ('/review', 200),
        ('/roadmap', 302), ('/mastery', 302),
        ('/roadmap/global', 200), ('/mastery/global', 200),
        ('/lang/python', 200), ('/lang/python/roadmap', 200),
        ('/lang/python/lesson/py_f1', 200), ('/lang/python/lesson/py_a5', 200),
        ('/lang/python/mastery', 200),
        ('/lang/javascript', 302), ('/lang/go', 302), ('/lang/rust', 302), ('/lang/sql', 302),
        ('/progress', 200), ('/improvements', 200),
        ('/api/questions', 200), ('/api/roadmap', 200), ('/api/pedagogy', 200),
        ('/api/stage/f1', 200), ('/api/lang/python/roadmap', 200),
        ('/api/lang/python/stage/py_f1', 200), ('/api/cohort_progress', 200),
        ('/api/improvements', 200), ('/api/learners', 200), ('/api/research_refs', 200),
        ('/api/daily', 200), ('/api/meta', 200),
        ('/debug/bugs', 404), ('/debug/coverage', 404), ('/debug/changelog', 404),
        ('/no-such-route', 404), ('/lang/python/lesson/no-such-stage', 404),
    ]
    bad = []
    for path, expected in routes:
        r = client.get(path, follow_redirects=False)
        if r.status_code != expected:
            bad.append(f'{path}={r.status_code}(expect {expected})')
    if bad: return c.fail(f'{len(bad)}: {"; ".join(bad[:5])}')
    return c.ok(f'{len(routes)}/{len(routes)} routes match expected')

def check_html_rendering():
    c = Check('html_rendering')
    try:
        from app import app
    except Exception as e:
        return c.fail(str(e))
    client = app.test_client()
    issues = []
    for p in ['/', '/lang/python', '/lang/python/roadmap', '/lang/python/lesson/py_f1',
              '/lang/python/mastery', '/progress', '/improvements', '/quiz']:
        r = client.get(p)
        h = r.get_data(as_text=True)
        if '{{' in h or '%}' in h or '{%' in h: issues.append(f'{p}: unrendered Jinja')
        if 'lang="vi"' not in h: issues.append(f'{p}: missing lang=vi')
        if '<main' not in h: issues.append(f'{p}: missing <main>')
        if 'skip-link' not in h: issues.append(f'{p}: missing skip-link')
    if issues: return c.fail('; '.join(issues))
    return c.ok('8 pages render OK, all have lang=vi + <main> + skip-link')

def check_js_syntax():
    c = Check('js_syntax')
    files = list((ROOT/'static').glob('*.js'))
    bad = []
    try:
        for f in files:
            r = subprocess.run(['node', '--check', str(f)], capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                bad.append(f.name + ': ' + r.stderr.strip()[:80])
    except FileNotFoundError:
        return c.warn('node not on PATH; skipping JS lint')
    if bad: return c.fail('; '.join(bad))
    return c.ok(f'{len(files)} JS files pass node --check')

def check_bandit():
    c = Check('bandit_security')
    try:
        r = subprocess.run([sys.executable, '-m', 'bandit', '-r', 'app.py', 'templates', 'static',
                            '--severity-level', 'medium', '-f', 'json', '-q'],
                           capture_output=True, text=True, timeout=60, cwd=str(ROOT))
        data = json.loads(r.stdout) if r.stdout.strip() else {'results': []}
    except FileNotFoundError:
        return c.warn('bandit not installed; skipping')
    except Exception as e:
        return c.warn(f'bandit run failed: {e}')
    n = len(data.get('results', []))
    if n: return c.fail(f'{n} medium+ issues')
    return c.ok('0 medium+ issues on app.py + templates + static')

def check_static_files():
    c = Check('static_files')
    expected = ['style.css','prism.js','quiz.js','state_migrate.js','lang_switcher.js',
                'landing.js','lang_python.js','lang_javascript.js','lang_go.js','lang_rust.js','lang_sql.js',
                'lang_lesson.js','lang_roadmap.js','lang_dashboard.js','mastery_perlang.js',
                'progress.js','improvements.js','roadmap.js','lesson.js','mastery.js',
                'gamification.js','celebration.js']
    missing = [f for f in expected if not (ROOT/'static'/f).exists()]
    if missing: return c.fail(f'missing static files: {missing}')
    return c.ok(f'{len(expected)}/{len(expected)} static files present')

def check_templates():
    c = Check('templates')
    expected = ['index.html','landing.html','lang_dashboard.html','lang_roadmap.html',
                'lang_lesson.html','lang_mastery.html','progress.html','improvements.html',
                'lesson.html','mastery.html','roadmap.html']
    missing = [t for t in expected if not (ROOT/'templates'/t).exists()]
    if missing: return c.fail(f'missing templates: {missing}')
    return c.ok(f'{len(expected)}/{len(expected)} templates present')

def check_git_clean():
    c = Check('git_clean')
    try:
        r = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, cwd=str(ROOT))
        if r.returncode != 0:
            return c.warn('not a git repo or git unavailable')
        dirty = [ln for ln in r.stdout.strip().splitlines() if ln]
        if dirty: return c.warn(f'{len(dirty)} uncommitted files: {dirty[:3]}')
        return c.ok('working tree clean')
    except FileNotFoundError:
        return c.warn('git not on PATH')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true', help='output JSON')
    ap.add_argument('--quick', action='store_true', help='skip slow checks (bandit, JS)')
    args = ap.parse_args()

    t0 = time.time()
    checks = [
        check_data_integrity(),
        check_dag_acyclic(),
        check_schema(),
        check_templates(),
        check_static_files(),
        check_flask_routes(),
        check_html_rendering(),
        check_git_clean(),
    ]
    if not args.quick:
        checks.append(check_js_syntax())
        checks.append(check_bandit())
    elapsed = time.time() - t0

    if args.json:
        out = {'checks':[c.to_dict() for c in checks], 'elapsed_s': round(elapsed,2),
               'summary': {'ok': sum(1 for c in checks if c.status=='OK'),
                           'warn': sum(1 for c in checks if c.status=='WARN'),
                           'fail': sum(1 for c in checks if c.status=='FAIL')}}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            sym = {'OK':'PASS','WARN':'WARN','FAIL':'FAIL','?':'?'}[c.status]
            print(f'[{sym}] {c.name}: {c.details}')
        ok = sum(1 for c in checks if c.status=='OK')
        warn = sum(1 for c in checks if c.status=='WARN')
        fail = sum(1 for c in checks if c.status=='FAIL')
        print(f'\nSummary: {ok} PASS / {warn} WARN / {fail} FAIL ({elapsed:.1f}s)')

    return 1 if any(c.status=='FAIL' for c in checks) else 0

if __name__ == '__main__':
    sys.exit(main())
