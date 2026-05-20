"""Build per-lang roadmap views (75 stage instances = 15 stages × 5 langs).
Reuses existing stage structure; filters question_ids per lang.
Adds 5 lang-specific KCs for the per-lang KC ontology.
Preserves the global roadmap.json (immutable per spec §7).
"""
import json, pathlib, os, tempfile, hashlib

ROOT = pathlib.Path(__file__).parent
qs = json.loads((ROOT/"questions.json").read_text(encoding="utf-8"))
gm = json.loads((ROOT/"roadmap.json").read_text(encoding="utf-8"))

LANGS = ["python","javascript","go","rust","sql"]

# Per-lang specific KCs (sit alongside the 52 global KCs - additive, non-mutating)
LANG_KCS = {
    "python":     ["gil_threading_limits","list_default_mutable","late_binding_closure","f_string_quoting","walrus_scope"],
    "javascript": ["event_loop_microtask","this_binding","truthy_coercion","array_holes","promise_unhandled"],
    "go":         ["nil_interface_vs_value","goroutine_leak","slice_aliasing","range_loop_var","defer_in_loop"],
    "rust":       ["borrow_lifetime_elision","move_vs_borrow","sized_unsized","drop_order_field","unsafe_send_sync"],
    "sql":        ["index_planner_stat","null_three_valued_logic","windowed_aggregate","cte_materialization","row_estimate_skew"],
}

def stage_qids_for_lang(stage, lang):
    return [q["id"] for q in qs if q["lang"]==lang and q["stage_id"]==stage["id"]]

def build_lang_stages(lang):
    out = []
    for s in gm["stages"]:
        qids = stage_qids_for_lang(s, lang)
        out.append({
            "id": f"{lang[:2]}_{s['id']}",
            "lang": lang,
            "global_stage_id": s["id"],
            "level": s["level"],
            "order": s["order"],
            "title": s["title"],
            "objectives": s["objectives"],
            "prereqs": [f"{lang[:2]}_{p}" for p in s["prereqs"]],
            "kc_coverage": s["kc_coverage"] + LANG_KCS[lang],
            "question_ids": qids,
            "mastery_gate": s["mastery_gate"],
            "spaced_review": s["spaced_review"],
            "metacog_prompt": s["metacog_prompt"],
            "est_min": s["est_min"],
            "pedagogy_sources": s["pedagogy_sources"],
        })
    return out

per_lang = {}
for lang in LANGS:
    per_lang[lang] = build_lang_stages(lang)

# Per-lang KC ontology = global 52 + 5 lang-specific per lang
per_lang_kcs = {lang: gm["kcs"] + LANG_KCS[lang] for lang in LANGS}

# Per-lang prereq DAG
def dag_ok(stages):
    ids = {s["id"] for s in stages}
    indeg = {s["id"]: 0 for s in stages}
    for s in stages:
        for p in s["prereqs"]:
            if p in ids: indeg[s["id"]] += 1
    order = [k for k,d in indeg.items() if d==0]
    seen = set()
    while order:
        n = order.pop()
        if n in seen: return False
        seen.add(n)
        for s in stages:
            if n in s["prereqs"]:
                indeg[s["id"]] -= 1
                if indeg[s["id"]] == 0: order.append(s["id"])
    return len(seen) == len(stages)

dag_results = {lang: dag_ok(per_lang[lang]) for lang in LANGS}

# Summary stats
total_stages = sum(len(v) for v in per_lang.values())
total_qs_covered = sum(len(s["question_ids"]) for v in per_lang.values() for s in v)
per_lang_q_total = {lang: sum(len(s["question_ids"]) for s in per_lang[lang]) for lang in LANGS}

out = {
    "version": 1,
    "langs": LANGS,
    "per_lang_stages": per_lang,
    "per_lang_kcs": per_lang_kcs,
    "lang_specific_kcs": LANG_KCS,
    "stats": {
        "total_stage_instances": total_stages,
        "stages_per_lang": {lang: len(per_lang[lang]) for lang in LANGS},
        "questions_per_lang": per_lang_q_total,
        "dag_valid_per_lang": dag_results,
    }
}
print(f"Per-lang stage instances: {total_stages} (target 75)")
print(f"Questions covered (sum): {total_qs_covered} / {len(qs)} (some land in different lang's stage map)")
print(f"Per-lang Q totals: {per_lang_q_total}")
print(f"DAG valid: {dag_results}")
assert total_stages == 75
assert all(dag_results.values())

def atomic_write(path, content):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try: os.unlink(tmp)
            except: pass

atomic_write(str(ROOT/"roadmap_perlang.json"), json.dumps(out, ensure_ascii=False, indent=2))
print("wrote roadmap_perlang.json")
