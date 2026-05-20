"""Re-run §3.2 EXACT validators (gofmt -e for go, rustc for rust) over the existing pool.
Items that no longer pass are removed from questions.jsonl. Tracks per-language acceptance.
"""
import json, pathlib, os
from validate import exec_py, exec_js, exec_go, exec_rust, exec_sql

ROOT = pathlib.Path(__file__).parent
JSONL = ROOT / 'questions.jsonl'

items = []
for line in JSONL.read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if line:
        items.append(json.loads(line))
print(f"loaded {len(items)} items")

EXEC = {"python": exec_py, "javascript": exec_js, "go": exec_go, "rust": exec_rust, "sql": exec_sql}

kept = []
rejected = []
per_lang_fail = {}
for it in items:
    fn = EXEC[it['lang']]
    ok, msg = fn(it['code'])
    if ok:
        kept.append(it)
    else:
        rejected.append((it['id'], it['lang'], msg))
        per_lang_fail[it['lang']] = per_lang_fail.get(it['lang'], 0) + 1

print(f"\nkept {len(kept)} / {len(items)} items")
print(f"rejected: {len(rejected)}")
print(f"per-lang failures: {per_lang_fail}")
if rejected[:10]:
    print("\nfirst 10 failures:")
    for r in rejected[:10]:
        print(f"  {r[0]} [{r[1]}] {r[2][:80]}")

# atomically rewrite jsonl + json
tmp = ROOT / 'questions.jsonl.exact_tmp'
with tmp.open('w', encoding='utf-8') as f:
    for it in kept:
        f.write(json.dumps(it, ensure_ascii=False) + '\n')
        f.flush()
os.replace(tmp, JSONL)
(ROOT / 'questions.json').write_text(json.dumps(kept, ensure_ascii=False, indent=0), encoding='utf-8')
print(f"rewrote {JSONL.name} and questions.json")
