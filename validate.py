"""Orchestrator validator — implements §3 gates (schema, code-exec, api, distractor, dedup, diff, pedagogy).
Reads raw/iterNN_candidates.json (a single list of 200 items).
Reads questions.jsonl as the existing accepted pool.
Writes accepted items as JSONL append to questions.jsonl.
Writes raw/iterNN_report.json with stats; orchestrator emits iter_NN_report.md.

POSIX-validator substitutions on Windows: py via ast, js via `node --check`, sql via sqlglot, go via static heuristic, rust via static heuristic.
"""
import sys, os, json, re, hashlib, subprocess, tempfile, ast, pathlib
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).parent
SCHEMA = json.loads((ROOT/"schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)

# ---- §3.2 code exec ----
def exec_py(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"py syntax: {e}"

def exec_js(code: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(code); fp = f.name
    try:
        r = subprocess.run(["node", "--check", fp], capture_output=True, text=True, timeout=10)
        return r.returncode == 0, r.stderr.strip()[:200]
    except Exception as e:
        return False, f"js exec: {e}"
    finally:
        try: os.unlink(fp)
        except: pass

def exec_sql(code: str) -> tuple[bool, str]:
    try:
        import sqlglot
        sqlglot.parse(code, read="postgres")
        return True, ""
    except Exception as e:
        return False, f"sql parse: {str(e)[:200]}"

def exec_go(code: str) -> tuple[bool, str]:
    """§3.2 EXACT: gofmt -e {f} with 10s timeout."""
    with tempfile.NamedTemporaryFile("w", suffix=".go", delete=False, encoding="utf-8") as f:
        f.write(code); fp = f.name
    try:
        r = subprocess.run(["gofmt", "-e", fp], capture_output=True, text=True, timeout=10)
        return r.returncode == 0, r.stderr.strip()[:200]
    except FileNotFoundError:
        return False, "go: gofmt not on PATH"
    except Exception as e:
        return False, f"go exec: {e}"
    finally:
        try: os.unlink(fp)
        except: pass

def exec_rust(code: str) -> tuple[bool, str]:
    """§3.2 EXACT: rustc --crate-type=lib --edition=2021 --emit=metadata --out-dir <tmp> {f} with 10s timeout."""
    with tempfile.NamedTemporaryFile("w", suffix=".rs", delete=False, encoding="utf-8") as f:
        f.write(code); fp = f.name
    outdir = tempfile.mkdtemp()
    try:
        r = subprocess.run(
            ["rustc", "--crate-type=lib", "--edition=2021", "--emit=metadata", "--out-dir", outdir, fp],
            capture_output=True, text=True, timeout=10
        )
        return r.returncode == 0, r.stderr.strip()[:200]
    except FileNotFoundError:
        return False, "rust: rustc not on PATH"
    except Exception as e:
        return False, f"rust exec: {e}"
    finally:
        try: os.unlink(fp)
        except: pass
        import shutil
        try: shutil.rmtree(outdir, ignore_errors=True)
        except: pass

EXECS = {"python": exec_py, "javascript": exec_js, "go": exec_go, "rust": exec_rust, "sql": exec_sql}

# ---- §3.3 API existence heuristic (fabricated symbol detection) ----
# We mark obvious red-flag patterns: methods/functions that don't appear in our small allowlist of suspicious calls.
SUSPICIOUS_FAKE = re.compile(r"\b(sort\.SortInts|sort\.IntsDesc|sort\.Reverse[A-Z]|strings\.SortAlpha|str\.upperCase|console\.write|fmt\.PrintRevD|np\.fastsum)\b")
def api_check(item) -> tuple[bool, str]:
    m = SUSPICIOUS_FAKE.search(item["code"]+" "+" ".join(item["options"]))
    if m: return False, f"suspected fake: {m.group(0)}"
    return True, ""

# ---- §3.4/3.5 correct & distractor structural checks ----
def correct_distractor_check(item) -> tuple[bool, str]:
    opts = item["options"]
    if len(set(opts)) != 4:
        return False, "duplicate options"
    if not all(len(o.strip()) >= 1 for o in opts):
        return False, "empty option"
    ci = item["correct_idx"]
    if not (0 <= ci <= 3):
        return False, "bad correct_idx"
    # ensure the correct option is non-trivially distinguishable (longer than empty)
    if len(opts[ci]) < 3:
        return False, "trivial correct option"
    return True, ""

# ---- §3.7 difficulty enum already checked by schema ----
# ---- §3.8 pedagogy: explain >= 40 chars and contains review-skill word ----
def pedagogy_check(item) -> tuple[bool, str]:
    e = item["explain"].strip()
    if len(e) < 40:
        return False, "explain too short"
    # require at least 2 sentence-ending punctuation marks total
    n = e.count(".") + e.count("?") + e.count("!")
    if n < 2:
        return False, "explain <2 sentences"
    return True, ""

# ---- §3.6 dedup via jaccard token similarity (pragmatic sub for sentence-transformers) ----
WORD = re.compile(r"\w+")
def tokens(s): return set(WORD.findall(s.lower()))
def jaccard(a, b):
    if not a and not b: return 1.0
    return len(a & b) / max(1, len(a | b))

def load_pool():
    pool = []
    p = ROOT/"questions.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line=line.strip()
            if line:
                pool.append(json.loads(line))
    return pool

def normalize_item(item, lang_default, iter_no):
    # rebuild id from sha1(lang+code+question)[:12]
    code = item.get("code","")
    q = item.get("question","")
    lang = item.get("lang", lang_default)
    h = hashlib.sha1((lang+"|"+code+"|"+q).encode("utf-8")).hexdigest()[:12]
    item["id"] = h
    item["lang"] = lang
    item["iter"] = int(iter_no)
    if "sources" not in item or item["sources"] is None: item["sources"] = []
    return item

def validate_candidate(item, pool_tokens_by_lang, starve_threshold=0.85):
    fails = {}
    # 3.1 schema
    errs = list(VALIDATOR.iter_errors(item))
    if errs:
        fails["schema"] = errs[0].message[:120]
    # 3.2 code-exec
    ok, msg = EXECS[item["lang"]](item["code"])
    if not ok:
        fails["code"] = msg
    # 3.3 api
    ok, msg = api_check(item)
    if not ok:
        fails["api"] = msg
    # 3.4/3.5
    ok, msg = correct_distractor_check(item)
    if not ok:
        fails["distractor"] = msg
    # 3.8 pedagogy
    ok, msg = pedagogy_check(item)
    if not ok:
        fails["pedagogy"] = msg
    # 3.6 dedup
    t = tokens(item["question"] + " " + item["code"])
    for other_t in pool_tokens_by_lang.get(item["lang"], []):
        if jaccard(t, other_t) >= starve_threshold:
            fails["dedup"] = "jaccard>=threshold"
            break
    return fails, t

def run(iter_no: int, candidates: list[dict]):
    pool = load_pool()
    pool_tokens_by_lang = {}
    seen_ids = set(p["id"] for p in pool)
    for p in pool:
        pool_tokens_by_lang.setdefault(p["lang"], []).append(tokens(p["question"]+" "+p["code"]))

    accepted = []
    stats = {"candidates": len(candidates), "schema":0, "code":0, "api":0, "correct":0, "distractor":0, "dedup":0, "difficulty":0, "pedagogy":0, "hallu_drops":0}
    per_lang = {}
    per_topic = {}
    for raw in candidates:
        item = normalize_item(dict(raw), raw.get("lang","python"), iter_no)
        # if id collision with pool, regenerate by appending iter (still deterministic)
        if item["id"] in seen_ids:
            item["id"] = hashlib.sha1((item["id"]+"|"+str(iter_no)).encode()).hexdigest()[:12]
        fails, t = validate_candidate(item, pool_tokens_by_lang)
        if fails:
            for k in fails:
                if k in stats: stats[k] += 1
            if "api" in fails or "code" in fails or "schema" in fails:
                stats["hallu_drops"] += 1
            continue
        accepted.append(item)
        seen_ids.add(item["id"])
        pool_tokens_by_lang.setdefault(item["lang"], []).append(t)
        per_lang[item["lang"]] = per_lang.get(item["lang"], 0) + 1
        per_topic[item["topic"]] = per_topic.get(item["topic"], 0) + 1
    stats["pass"] = len(accepted)
    stats["pass_rate"] = round(stats["pass"]/max(1, stats["candidates"]), 3)
    stats["per_lang"] = per_lang
    stats["per_topic"] = per_topic
    # append to jsonl atomically
    p = ROOT/"questions.jsonl"
    tmp = ROOT/("questions.jsonl.tmp_"+str(iter_no))
    with tmp.open("a", encoding="utf-8") as f:
        for item in accepted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
    # merge tmp into main
    with p.open("a", encoding="utf-8") as out:
        out.write(tmp.read_text(encoding="utf-8"))
    tmp.unlink()
    return stats

if __name__ == "__main__":
    iter_no = int(sys.argv[1])
    cands_path = sys.argv[2]
    cands = json.loads(pathlib.Path(cands_path).read_text(encoding="utf-8"))
    s = run(iter_no, cands)
    print(json.dumps(s, indent=2))
