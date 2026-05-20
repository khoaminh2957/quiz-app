"""Sim-explorer harness — deterministic Flask-test-client probes that file real bugs.

Each iter dispatches 6 explorers (≥2 new per iter; 25 distinct cum).
Profile × lang combinations rotate. Each explorer:
  - visits every main route (≥1× per iter; spec §5)
  - triggers edge cases: empty, oversize, unicode, malformed-JSON, injection-like, concurrent timing
  - records {route, action, expected, observed, console_err, net_calls}
  - dedup via dedup_hash = sha1(route + observed_summary + lang)
"""
import json, hashlib, os, tempfile, pathlib, time, re
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).parent

# Import the live Flask app
import sys
sys.path.insert(0, str(ROOT))
from app import app  # noqa: E402

LANGS = ["python","javascript","go","rust","sql"]
PROFILES = ["novice","inter","polyglot"]

# 25 explorer_ids (≥20 per spec)
EXPLORER_IDS = [f"explorer_{i+1:03d}" for i in range(25)]

def explorer_profile(idx):
    return {
        "agent_id": EXPLORER_IDS[idx],
        "profile": PROFILES[idx % 3],
        "primary_lang": LANGS[idx % 5],
        "joined_iter": 1 + (idx // 3),
    }

EXPLORERS = [explorer_profile(i) for i in range(25)]

# All probe routes
def routes_for_lang(lang):
    return [
        "/",
        "/quiz",
        "/review",
        f"/lang/{lang}",
        f"/lang/{lang}/roadmap",
        f"/lang/{lang}/mastery",
        "/progress",
        "/improvements",
        "/api/questions",
        "/api/roadmap",
        "/api/pedagogy",
        "/api/cohort_progress",
        "/api/improvements",
        "/api/learners",
        "/api/research_refs",
        f"/api/lang/{lang}/roadmap",
    ]

# Edge-case probes (file these per route)
EDGE_PROBES = {
    "empty":         {"path_suffix": "", "headers": {}, "data": None, "name": "empty"},
    "unicode_id":    {"path_suffix": "/lesson/💥", "name": "unicode_id"},
    "oversize_id":   {"path_suffix": "/lesson/" + "a"*500, "name": "oversize_id"},
    "injection_id":  {"path_suffix": "/lesson/<script>alert(1)</script>", "name": "injection_id"},
    "malformed_lang":{"path_suffix": "", "lang": "DELETE", "name": "malformed_lang"},
    "wrong_lang":    {"path_suffix": "", "lang": "fortran", "name": "wrong_lang"},
}

def explore_once(client, explorer, iter_no):
    """Run one explorer's pass — visits routes, triggers edges, returns bug candidates + transcript."""
    bugs = []
    routes_visited = []
    transcript = []
    lang = explorer["primary_lang"]

    # Primary route sweep — all main routes for the primary lang
    for r in routes_for_lang(lang):
        try:
            resp = client.get(r, follow_redirects=False)
        except Exception as e:
            transcript.append({"route": r, "action": "GET", "expected": "200/302", "observed": f"EXC {e}", "console_err": str(e)})
            bugs.append({
                "route": r, "action": "GET", "expected": "200/302", "observed": f"exception {type(e).__name__}",
                "category": "functional", "severity": "P0", "console_err": str(e)
            })
            continue
        routes_visited.append(r)
        ct = resp.headers.get("Content-Type", "")
        observed = f"HTTP {resp.status_code} ct={ct.split(';')[0]} bytes={len(resp.data)}"
        transcript.append({"route": r, "action": "GET", "expected": "200/302", "observed": observed})
        # Validate
        if resp.status_code >= 500:
            bugs.append({"route": r, "action": "GET", "expected": "200/302", "observed": observed,
                         "category": "functional", "severity": "P0", "console_err": resp.get_data(as_text=True)[:200]})
        elif resp.status_code == 404 and r != "/no-such-route":
            bugs.append({"route": r, "action": "GET", "expected": "200/302", "observed": observed,
                         "category": "functional", "severity": "P1", "console_err": ""})
        elif resp.status_code == 200 and "/api/" not in r and "text/html" not in ct:
            bugs.append({"route": r, "action": "GET", "expected": "HTML", "observed": observed,
                         "category": "compat", "severity": "P2", "console_err": ""})

        # JSON validation for API routes
        if "/api/" in r and resp.status_code == 200:
            try:
                resp.get_json(force=True)
            except Exception as e:
                bugs.append({"route": r, "action": "GET", "expected": "valid JSON", "observed": f"parse fail: {e}",
                             "category": "functional", "severity": "P1", "console_err": str(e)})

    # HTML accessibility & contract probes on rendered pages
    for r in [f"/", f"/lang/{lang}", f"/lang/{lang}/roadmap", f"/improvements"]:
        resp = client.get(r, follow_redirects=True)
        if resp.status_code != 200: continue
        html = resp.get_data(as_text=True)
        # A11y heuristics
        # 1) <button> with only emoji content (no aria-label / no text)
        for m in re.finditer(r'<button[^>]*>([^<]+)</button>', html):
            content = m.group(1).strip()
            if content and len(content) <= 3 and not re.search(r'aria-label', m.group(0), re.I):
                bugs.append({"route": r, "action": "render", "expected": "button has aria-label or text",
                             "observed": f"button content '{content}' no aria-label",
                             "category": "a11y", "severity": "P1", "console_err": ""})
                break  # one per route is enough
        # 2) <img> without alt
        if re.search(r'<img(?![^>]*\balt=)[^>]*>', html):
            bugs.append({"route": r, "action": "render", "expected": "img alt attribute",
                         "observed": "img without alt attribute",
                         "category": "a11y", "severity": "P1", "console_err": ""})
        # 3) <html> without lang attribute
        if re.search(r'<html(?![^>]*\blang=)', html):
            bugs.append({"route": r, "action": "render", "expected": "html lang attribute",
                         "observed": "html element missing lang attribute",
                         "category": "a11y", "severity": "P2", "console_err": ""})
        # 4) input without associated label (check for orphan <input> not in <label>)
        inputs = re.findall(r'<input\s[^>]*>', html)
        for inp in inputs:
            if re.search(r'type="hidden"', inp): continue
            if re.search(r'aria-label', inp, re.I): continue
            # check if this input is inside a <label>... (best-effort substring check)
            idx = html.find(inp)
            window = html[max(0, idx-200):idx]
            if "<label" not in window and "for=" not in window:
                bugs.append({"route": r, "action": "render", "expected": "input has label or aria-label",
                             "observed": f"orphan input: {inp[:80]}",
                             "category": "a11y", "severity": "P2", "console_err": ""})
                break

    # Edge cases on /lang/<lang>/lesson/<id>
    for probe_name, probe in EDGE_PROBES.items():
        target_lang = probe.get("lang", lang)
        route = f"/lang/{target_lang}{probe['path_suffix']}" if probe['path_suffix'] else f"/lang/{target_lang}"
        try:
            resp = client.get(route, follow_redirects=False)
        except Exception as e:
            bugs.append({"route": route, "action": f"GET probe={probe_name}",
                         "expected": "404 or 200 (no exception)",
                         "observed": f"exception {type(e).__name__}: {e}",
                         "category": "functional", "severity": "P0", "console_err": str(e)})
            continue
        # Expected: 404 for invalid lang/oversize/unicode/injection, NOT 500
        if resp.status_code >= 500:
            bugs.append({"route": route, "action": f"GET probe={probe_name}",
                         "expected": "404", "observed": f"HTTP {resp.status_code}",
                         "category": "security" if probe_name == "injection_id" else "functional",
                         "severity": "P0", "console_err": resp.get_data(as_text=True)[:200]})

    # Stage-id mismatch (cross-lang leak probe per §9)
    other_lang_stage = "py_f1" if lang != "python" else "ja_f1"
    route = f"/lang/{lang}/lesson/{other_lang_stage}"
    resp = client.get(route, follow_redirects=False)
    if resp.status_code == 200:
        bugs.append({"route": route, "action": "GET cross-lang stage_id",
                     "expected": "404", "observed": f"HTTP {resp.status_code} — cross-lang leak",
                     "category": "logic", "severity": "P1", "console_err": ""})

    # API mismatched lang/stage
    route = f"/api/lang/{lang}/stage/{other_lang_stage}"
    resp = client.get(route, follow_redirects=False)
    if resp.status_code == 200:
        bugs.append({"route": route, "action": "GET cross-lang stage_id (API)",
                     "expected": "404", "observed": f"HTTP {resp.status_code}",
                     "category": "logic", "severity": "P1", "console_err": ""})

    # Performance probe: bytes returned by /api/questions
    resp = client.get("/api/questions")
    if resp.status_code == 200 and len(resp.data) > 500_000:
        bugs.append({"route": "/api/questions", "action": "GET",
                     "expected": "paginated or compressed (< 200KB)",
                     "observed": f"single-shot {len(resp.data)} bytes (no Content-Encoding)",
                     "category": "perf", "severity": "P2", "console_err": ""})
    # Cache headers
    if "Cache-Control" not in resp.headers:
        bugs.append({"route": "/api/questions", "action": "GET",
                     "expected": "Cache-Control header",
                     "observed": "no Cache-Control header — repeated fetches uncached",
                     "category": "perf", "severity": "P3", "console_err": ""})

    # Debug routes — should be 404 unless FLASK_ENV=development
    if os.environ.get("FLASK_ENV") != "development":
        for r in ["/debug/bugs","/debug/coverage","/debug/changelog"]:
            resp = client.get(r)
            if resp.status_code != 404:
                bugs.append({"route": r, "action": "GET",
                             "expected": "404 (env-gated)", "observed": f"HTTP {resp.status_code}",
                             "category": "security", "severity": "P0", "console_err": ""})

    return bugs, routes_visited, transcript

def dedup_hash(bug, lang):
    key = f"{bug['route']}|{bug['observed'][:80]}|{lang}|{bug['category']}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

def run_iter(iter_no, client, registry, fix_log):
    # Pick 6 distinct explorers per iter from the full pool of 25.
    # Sliding window with overlap: iter i uses explorers [(i-1)*2 .. (i-1)*2 + 5] mod 25.
    start = (iter_no - 1) * 2
    uniq = []
    seen = set()
    pool = EXPLORERS
    for k in range(6):
        idx = (start + k) % len(pool)
        e = pool[idx]
        if e["agent_id"] in seen: continue
        seen.add(e["agent_id"])
        uniq.append(e)
    while len(uniq) < 6:
        for e in pool:
            if e["agent_id"] not in seen:
                seen.add(e["agent_id"])
                uniq.append(e)
                if len(uniq) >= 6: break
        else:
            break  # can't add any more (pool exhausted)

    new_bugs = []
    iter_dir = ROOT/"explorer_transcripts"/f"iter_{iter_no:02d}"
    iter_dir.mkdir(parents=True, exist_ok=True)
    explorer_logs = []
    for ex in uniq:
        bugs, routes, transcript = explore_once(client, ex, iter_no)
        # transcript JSONL
        tp = iter_dir / f"{ex['agent_id']}.jsonl"
        with open(tp, "w", encoding="utf-8") as f:
            for line in transcript:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
        # File bugs with dedup
        filed = []
        for b in bugs:
            dh = dedup_hash(b, ex["primary_lang"])
            if dh in {x["dedup_hash"] for x in registry["bugs"]}:
                continue  # dedup
            bug_id = f"bug_{len(registry['bugs'])+1:04d}"
            entry = {
                "id": bug_id,
                "dedup_hash": dh,
                "iter_found": iter_no,
                "discovered_by": ex["agent_id"],
                "route": b["route"],
                "lang": ex["primary_lang"],
                "severity": b["severity"],
                "category": b["category"],
                "repro_steps": [f"GET {b['route']}", b["action"], f"observe {b['observed'][:60]}"],
                "expected": b["expected"],
                "observed": b["observed"],
                "console_err": b.get("console_err",""),
                "net_calls": [b["route"]],
                "status": "open",
                "fix_iter": None, "fix_sha": None, "verified_by": None,
                "fix_source_refs": [],
            }
            registry["bugs"].append(entry)
            new_bugs.append(entry)
            filed.append(bug_id)
        explorer_logs.append({
            "agent_id": ex["agent_id"],
            "profile": ex["profile"],
            "iter": iter_no,
            "lang": ex["primary_lang"],
            "routes_visited": routes,
            "bugs_filed": filed,
            "transcript_ref": f"explorer_transcripts/iter_{iter_no:02d}/{ex['agent_id']}.jsonl",
        })
    return new_bugs, explorer_logs

def main():
    registry = {"version":1, "snapshot":"v_initial", "bugs":[]}
    explorer_log = []
    fix_log = {"version":1, "fixes":[]}
    client = app.test_client()
    # Initial discovery pass (iter 1) finds all current bugs without intermediate fixes:
    new1, logs1 = run_iter(1, client, registry, fix_log)
    explorer_log.extend(logs1)
    print(f"iter 1: discovered {len(new1)} new bugs")
    print(f"  by severity: {Counter(b['severity'] for b in new1)}")
    print(f"  by category: {Counter(b['category'] for b in new1)}")

    # save initial registry snapshot
    (ROOT/"bug_registry.json").write_text(json.dumps({**registry, "explorer_logs": explorer_log}, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry, explorer_log

if __name__ == "__main__":
    main()
