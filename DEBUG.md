# Debug & Health — Quiz Review Code

Comprehensive debugging guide cho app hiện tại và tương lai.

## Quick health check (1.7s)

```powershell
python health_check.py            # human-readable
python health_check.py --json     # machine-readable for CI
python health_check.py --quick    # bỏ qua bandit + JS lint
```

Exit code 0 nếu all PASS / WARN; exit 1 nếu có FAIL.

Kiểm tra 10 mục:
1. **data_integrity** — Q schema, stage assignment, KC valid, options=4, correct_idx in [0,3], lang=python only
2. **dag_acyclic** — Per-lang prereq graph không có cycle
3. **schema_validation** — jsonschema Draft 2020-12 trên base fields
4. **templates** — 11/11 templates present
5. **static_files** — 22/22 static JS files present
6. **flask_routes** — 35/35 routes return expected status (200/302/404)
7. **html_rendering** — Mọi page có `lang="vi"`, `<main>`, `skip-link`, không có unrendered Jinja
8. **git_clean** — Working tree clean (WARN nếu có uncommitted)
9. **js_syntax** — `node --check` mọi file `static/*.js`
10. **bandit_security** — Medium+ severity scan trên app.py + templates + static (0 issues required)

## Runtime debug routes

| Route | Visibility | Mục đích |
|---|---|---|
| `GET /debug/health` | **Always** | Quick probe: Q count, stages, git SHA, env flag. 60s cache. |
| `GET /debug/state-inspector` | `FLASK_ENV=development` only | Full data dump: distributions by topic/difficulty/stage/lang, file sizes |
| `GET /debug/bugs` | `FLASK_ENV=development` only | `bug_registry.json` raw |
| `GET /debug/coverage` | `FLASK_ENV=development` only | Explorer coverage from sim_explorer runs |
| `GET /debug/changelog` | `FLASK_ENV=development` only | `fix_log.json` raw |
| `POST /api/client_errors` | Always | JS error reporter sends here; rate-limited 10/session |

Bật dev mode:
```powershell
$env:FLASK_ENV = "development"; python app.py
```

## Logs

- Path: `logs/app.log` (rotating, 2MB × 3 backups)
- Format: JSON-line, một dòng = một event
- Fields: `ts` (UTC ISO), `lvl`, `logger`, `msg`, `req_id`, `path`, `method`, `status`, `ms`, `client_err`, `exc`
- Mọi response có header `X-Req-Id` để cross-reference với log

Filter examples:
```powershell
# All 5xx errors
Get-Content logs/app.log | Where-Object { $_ -match '"status":5' }

# Slow requests (>500ms)
Get-Content logs/app.log | Where-Object { $_ -match '"ms":[5-9]\d{2,}' }

# Client JS errors
Get-Content logs/app.log | Where-Object { $_ -match 'client_error' }

# By req_id (correlate one request across multiple log lines)
Get-Content logs/app.log | Where-Object { $_ -match '"req_id":"e5fc32abd9aa"' }
```

## JS client errors

`error_reporter.js` (load đầu tiên trong mọi template) bắt:
- `window.error` — runtime errors, SyntaxError, ReferenceError, TypeError…
- `unhandledrejection` — Promise rejection không có .catch

Payload POST tới `/api/client_errors`:
```json
{"msg":"...","src":"...","line":N,"col":N,"url":"...","ua":"..."}
```

Rate limit: 10 errors/page session để tránh loop nếu reporter chính bị lỗi.

Sample log entry sẽ là:
```json
{"ts":"...","lvl":"WARNING","logger":"quizapp","msg":"client_error","req_id":"...","client_err":"{...}"}
```

## Common debug paths

### 1. App không start / lỗi import
```powershell
python -c "from app import app; print(app)"
# Nếu lỗi ImportError → kiểm tra requirements: flask>=3
```

### 2. Một route trả 500
1. Lấy `X-Req-Id` từ browser DevTools Network tab
2. `Select-String "req_id\":\"<id>" logs/app.log` để xem stack trace
3. Hoặc check `logs/app.log` cho line `"lvl":"ERROR"` mới nhất

### 3. Câu hỏi không hiện
- `python health_check.py --quick` → xem `data_integrity`
- `curl http://127.0.0.1:5000/api/lang/python/stage/<stage_id>` xem trả về có `questions: [...]` không
- Nếu stage rỗng → chạy `python rebalance_py_stages.py` để rebalance

### 4. Cộng đồng bug ở browser
- Mở DevTools Console
- Reproduce
- Vào `logs/app.log` filter `client_error` để xem server đã nhận chưa
- Nếu chưa nhận → có thể CSP block hoặc fetch fail; xem Network tab

### 5. localStorage corruption / quota
- `error_reporter.js` sẽ log nếu `QuotaExceededError`
- Banner sẽ hiện trên trang ('Bộ nhớ trình duyệt đã đầy. Vào Mức độ thành thạo để xoá dữ liệu cũ.')
- Recovery: corrupt blob được lưu vào `state_corrupt_<timestamp>` trước khi clobber
- User có thể clear: `localStorage.clear()` từ DevTools Console

### 6. Theme not respecting OS preference
- Check `localStorage.getItem('theme')` — nếu set thì user đã chọn thủ công, override OS pref
- Clear: `localStorage.removeItem('theme')` để revert về OS pref
- `state_migrate.js` lắng nghe `matchMedia('(prefers-color-scheme: dark)').addEventListener('change', ...)` chỉ khi user chưa chọn thủ công

### 7. Daily question không đổi mỗi ngày
- Endpoint: `/api/daily` tính theo ICT (UTC+7), hash SHA1(date) mod pool size
- Nếu thay đổi vào lúc 7:00 UTC = 14:00 ICT → kiểm tra server timezone
- Manual test: `curl http://127.0.0.1:5000/api/daily` xem field `date`

### 8. Streak counter sai
- `state_migrate.js` `recordAttempt()` tính theo ICT
- Logic: nếu `last_active_date == today` → no change; `diff == 1` → +1; `diff > 1` → reset to 1
- Check `localStorage.getItem('state')` → `gamification.streak.history` để xem dates đã active

### 9. Stage progress ring không hiện
- Yêu cầu: stage phải có ≥1 attempt trong `stage_attempts`
- Nếu chưa có attempt → fallback hiện emoji `🔒` / `✓` / `•`
- Check: `JSON.parse(localStorage.state).per_lang.python.stage_attempts`

### 10. Celebration modal spam
- Dedup theo `stage_id|today_ICT` trong `state.gamification.last_celebration`
- Một stage chỉ celebrate 1 lần / ngày
- Clear: `delete STATE.gamification.last_celebration['py_f1|2026-05-20']; QUIZ_STATE_API.save()`

## File-level audit map

```
quiz_app/
├── app.py                  # Flask routes + JSON logging + req_id middleware
├── questions.json          # 286 Python MCQs (Q-annotation immutable)
├── roadmap.json            # 15 cross-lang stages (legacy view)
├── roadmap_perlang.json    # Per-lang Python 15 stage instances
├── pedagogy_refs.json      # 24 pedagogy refs (Bloom, Sweller, ...)
├── improvement_log.json    # 44 improvements across 10 iters
├── learner_registry.json   # 25 simulated learners + cohort metrics
├── research_refs.json      # 32 research refs (MDN, SO, GitHub, edu)
├── bug_registry.json       # 25 bugs found + fixed (debug pipeline output)
├── fix_log.json            # 10-iter fix history
├── health_check.py         # ★ Run this first when something seems off
├── rebalance_py_stages.py  # Run if stage Q distribution is uneven
├── migrate_vi_python.py    # One-shot: filter to Python + translate to VN
├── design_roadmap.py       # Source of truth for 15-stage spec
├── sim_explorer.py         # Flask test_client based bug probe
├── debug_orchestrator.py   # 10-iter explore→fix→verify pipeline
├── logs/
│   └── app.log            # ★ Live request log (JSON-line, rotating)
├── templates/             # 11 Jinja2 templates (all <html lang="vi">)
└── static/                # 22 JS files + style.css + prism.js
    └── error_reporter.js  # ★ Captures runtime errors, POSTs to /api/client_errors
```

## CI invocation (future)

```yaml
# .github/workflows/health.yml stub
- name: Health check
  run: |
    pip install flask jsonschema sentence-transformers sqlglot bandit
    python health_check.py --quick --json > health.json
    cat health.json | python -c "import sys,json; r=json.load(sys.stdin); sys.exit(0 if r['summary']['fail']==0 else 1)"
```

## Operational gotchas (đã gặp trong session)

| Symptom | Root cause | Fix |
|---|---|---|
| `UnicodeEncodeError: cp1252` khi print Vietnamese trong Windows console | Default stdout encoding cp1252 không có char Vietnamese | `python -X utf8 script.py` hoặc `$env:PYTHONIOENCODING="utf-8"` |
| Stage `py_f1`/`py_f2` 0 câu sau Python-only filter | Heuristic gán stage dồn vào f3/f5 | `python rebalance_py_stages.py` |
| "Background command failed exit 127" | Flask process bị `Stop-Process -Force` kill (intentional) | Bình thường, không phải bug |
| Auto-mode classifier block khi push GitHub public / vercel deploy | Protective behavior khi action có blast radius | Yêu cầu user authorize tường minh trong text |
| Live curl /lang/python trả 404 nhưng test_client trả 200 | Cũ Flask server vẫn bind cổng 5000, cần kill và restart | `Stop-Process python -Force; python app.py` |

## Schema versioning (localStorage)

- v1 (legacy): `localStorage.roadmap_state` flat object
- v2 (current): `localStorage.state` = `{schema_v:2, current_lang, per_lang:{...}, gamification:{...}}`
- Migration: v1 → v2 chạy 1 lần trong `state_migrate.js`, copy legacy data vào `per_lang.python`, mark `_migrated_from_v1: true`
- Corruption recovery: nếu parse fail, copy raw vào `state_corrupt_<ts>` trước khi reinit

## Re-running the full debug pipeline

```powershell
# 1. Quick smoke
python health_check.py --quick

# 2. Deep bug probe (sim-explorers via Flask test_client)
python sim_explorer.py     # generates bug_registry.json + transcripts

# 3. Full 10-iter explore-fix-verify
python debug_orchestrator.py     # generates iter_NN_debug_report.md + patch.diff

# 4. Re-balance Python stages if needed
python rebalance_py_stages.py

# 5. After fixes, re-run health check
python health_check.py
```
