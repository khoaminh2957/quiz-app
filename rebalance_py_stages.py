"""Rebalance Python stages so every stage has >=5 questions.

Issue: py_f1 (literal trace) and py_f2 (runtime errors) had 0 Qs because the
original stage-assignment heuristic in design_roadmap.py funneled easy Python Qs
to f3/f5. Now that we're Python-only, those empty stages show "Hoàn thành" with
0 questions on first click.

Strategy: re-assign some Qs from over-populated stages (f3=37, f5=37, i4=39, i5=46)
to f1/f2/a3 so every stage has >=5 Qs while preserving topic/diff_band match.
Updates: questions.json (stage_id field) + roadmap_perlang.json (question_ids).
"""
import json, pathlib, os, tempfile, re
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).parent

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

qs = json.loads((ROOT/"questions.json").read_text(encoding="utf-8"))
rp = json.loads((ROOT/"roadmap_perlang.json").read_text(encoding="utf-8"))
py_stages = rp["per_lang_stages"]["python"]

# Stage spec criteria (matches design_roadmap.py)
STAGE_RULES = {
    "py_f1": {"global": "f1", "topics": ["style","edge"],     "diff_max": -0.5},
    "py_f2": {"global": "f2", "topics": ["bug","edge"],       "diff_max": -0.3},
    "py_f3": {"global": "f3", "topics": ["style"],            "diff_max": 0.0},
    "py_f4": {"global": "f4", "topics": ["edge","bug"],       "diff_max": 0.3},
    "py_f5": {"global": "f5", "topics": ["bug","edge","style"],"diff_max": 0.5},
    "py_a3": {"global": "a3", "topics": ["security"],         "diff_min": 0.5},
}
TARGET_MIN = 5

# Build maps
by_id = {q["id"]: q for q in qs}
by_stage = defaultdict(list)
for q in qs:
    # questions.json stores stage_id as global (e.g., "f1") OR per-lang (e.g., "py_f1")?
    # Check: prior /goal said the global field is q["stage_id"] and per-lang derives from roadmap_perlang
    by_stage[q["stage_id"]].append(q)

print("Current Python distribution (by global stage_id):")
for s_id in sorted(by_stage):
    print(f"  {s_id}: {len(by_stage[s_id])}")

# Target empty stages: f1, f2 ; under-populated: a3 (1)
needs_more = {"f1": TARGET_MIN, "f2": TARGET_MIN}
# a3 already has 1 from prior rebalance — leave alone or boost? Boost to >=5 for consistency.
if len(by_stage.get("a3", [])) < TARGET_MIN:
    needs_more["a3"] = TARGET_MIN - len(by_stage.get("a3", []))

# Donor candidates: stages with >20 Qs
donors = sorted(by_stage.items(), key=lambda kv: -len(kv[1]))[:6]

moves = []

def pick_donors_for(target_sid, n_needed):
    """Find n questions that fit target stage's rules without breaking donor."""
    target_rule = STAGE_RULES[f"py_{target_sid}"]
    target_topics = set(target_rule["topics"])
    picked = []
    for donor_sid, donor_qs in donors:
        if donor_sid == target_sid: continue
        if len(by_stage[donor_sid]) - len([m for m in moves if m["from"] == donor_sid]) <= 15: continue
        # Sort donor Qs by best-fit (topic match + diff band)
        candidates = []
        for q in donor_qs:
            if q["topic"] not in target_topics: continue
            est = q["est_difficulty"]
            if "diff_max" in target_rule and est > target_rule["diff_max"]: continue
            if "diff_min" in target_rule and est < target_rule["diff_min"]: continue
            candidates.append(q)
        # Sort by est_difficulty closeness to band midpoint
        def mid():
            r = target_rule
            if "diff_min" in r and "diff_max" in r: return (r["diff_min"]+r["diff_max"])/2
            if "diff_max" in r: return r["diff_max"] - 1.0
            if "diff_min" in r: return r["diff_min"] + 1.0
            return 0.0
        m = mid()
        candidates.sort(key=lambda q: abs(q["est_difficulty"] - m))
        for q in candidates:
            if any(mv["qid"] == q["id"] for mv in moves): continue
            picked.append({"qid": q["id"], "from": donor_sid, "to": target_sid})
            if len(picked) >= n_needed: return picked
    return picked

for target_sid, n in needs_more.items():
    picks = pick_donors_for(target_sid, n)
    moves.extend(picks)
    print(f"  -> {target_sid}: need {n}, picked {len(picks)} from {Counter(p['from'] for p in picks)}")

# Apply moves: update q['stage_id'] in questions.json AND question_ids in roadmap_perlang.json
moved_set = {m["qid"]: m["to"] for m in moves}
new_qs = []
for q in qs:
    if q["id"] in moved_set:
        q = dict(q)
        q["stage_id"] = moved_set[q["id"]]
    new_qs.append(q)
atomic_write(str(ROOT/"questions.json"), json.dumps(new_qs, ensure_ascii=False))
with open(ROOT/"questions.jsonl", "w", encoding="utf-8") as f:
    for q in new_qs:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")

# Update roadmap_perlang.json question_ids per stage by re-deriving from new_qs
by_global_stage = defaultdict(list)
for q in new_qs:
    by_global_stage[q["stage_id"]].append(q["id"])

for s in rp["per_lang_stages"]["python"]:
    # per-lang id is e.g. "py_f1"; global stage_id is the suffix
    global_id = s["id"].split("_", 1)[1]
    s["question_ids"] = by_global_stage.get(global_id, [])
atomic_write(str(ROOT/"roadmap_perlang.json"), json.dumps(rp, ensure_ascii=False, indent=2))

print("\nFinal Python distribution:")
for s in rp["per_lang_stages"]["python"]:
    print(f"  {s['id']:8s} order={s['order']:2d} qids={len(s['question_ids']):4d}")
