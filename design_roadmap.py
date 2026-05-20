"""Design 15-stage curriculum + KC ontology + heuristic difficulty + Q annotations.

Spec: 15 stages = 3 levels × 5 sub. >=30 KCs over bug/sec/perf/style/edge/concurrency
informed by KLI framework. Every Q -> 1 stage + 1 KC. DAG acyclic+connected.
"""
import json, re, ast, hashlib, pathlib, math, os, tempfile
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).parent

# ---- 15 stages: 3 levels x 5 sub-stages ----
STAGES = [
    # foundational (5)
    {"id":"f1","level":"foundational","order":1,"title":"Reading code: literal trace",
     "kcs":["read_control_flow","read_data_flow","read_io"],
     "topic_focus":["style","edge"],"diff_band":(-3.0,-0.5),
     "objectives_seed":["trace execution of a 5-15 line snippet ≥ 90% accuracy by end of stage",
                        "identify the printed/returned value of a deterministic snippet within 60 seconds"],
     "metacog_prompt":"Before answering, mentally simulate the snippet line by line. After answering, note which line surprised you.",
     "est_min":45},
    {"id":"f2","level":"foundational","order":2,"title":"Common runtime errors",
     "kcs":["null_undefined","index_out_of_range","type_mismatch"],
     "topic_focus":["bug","edge"],"diff_band":(-2.5,-0.3),
     "objectives_seed":["predict the runtime exception class of a flawed snippet ≥ 85% accuracy by end of stage",
                        "distinguish NullPointer-like vs TypeError-like failures within 90 seconds"],
     "metacog_prompt":"What input value would make this code crash? Re-evaluate after seeing the answer.",
     "est_min":50},
    {"id":"f3","level":"foundational","order":3,"title":"Idiomatic syntax & style",
     "kcs":["lang_idiom","naming_convention","redundant_construct"],
     "topic_focus":["style"],"diff_band":(-2.5,0.0),
     "objectives_seed":["select the idiomatic option over the literal-correct option ≥ 80% accuracy by end of stage",
                        "spot a redundant construct (double negation, useless variable) within 45 seconds"],
     "metacog_prompt":"Is there a shorter, language-native way to express this? Rate your confidence 1-5.",
     "est_min":40},
    {"id":"f4","level":"foundational","order":4,"title":"Off-by-one and boundary edges",
     "kcs":["off_by_one","empty_collection","boundary_value"],
     "topic_focus":["edge","bug"],"diff_band":(-2.0,0.3),
     "objectives_seed":["identify the off-by-one boundary in a loop or slice ≥ 85% accuracy by end of stage",
                        "predict behavior on empty input within 60 seconds"],
     "metacog_prompt":"Trace the loop with n=0 and n=1. Which iteration counts differ?",
     "est_min":50},
    {"id":"f5","level":"foundational","order":5,"title":"Truthy/falsy & comparison pitfalls",
     "kcs":["truthy_falsy","equality_semantics","short_circuit"],
     "topic_focus":["bug","edge","style"],"diff_band":(-2.0,0.5),
     "objectives_seed":["distinguish == vs === / is vs == semantics ≥ 80% accuracy by end of stage",
                        "predict short-circuit eval order within 45 seconds"],
     "metacog_prompt":"Would the result change if 0, '', or None replaced the input?",
     "est_min":45},
    # intermediate (5)
    {"id":"i1","level":"intermediate","order":6,"title":"Mutability & reference semantics",
     "kcs":["aliasing","shallow_vs_deep","unintended_mutation"],
     "topic_focus":["bug","perf"],"diff_band":(-1.0,1.5),
     "objectives_seed":["spot unintended shared-reference bugs ≥ 80% accuracy by end of stage",
                        "decide between shallow and deep copy within 60 seconds given a mutation scenario"],
     "metacog_prompt":"Does mutating arg also mutate the caller's variable? Reason before answering.",
     "est_min":60},
    {"id":"i2","level":"intermediate","order":7,"title":"Performance: complexity & hot paths",
     "kcs":["big_o_recognition","quadratic_inside_loop","memo_opportunity","wasted_alloc"],
     "topic_focus":["perf"],"diff_band":(-0.5,2.0),
     "objectives_seed":["estimate time complexity of a 10-30 line snippet within 90 seconds",
                        "identify the dominant cost line ≥ 75% accuracy by end of stage"],
     "metacog_prompt":"Which line runs the most times? Estimate big-O before reading options.",
     "est_min":75},
    {"id":"i3","level":"intermediate","order":8,"title":"Resource & lifetime management",
     "kcs":["close_handle","ownership_borrow","drop_order","raii"],
     "topic_focus":["bug","perf","edge"],"diff_band":(-0.5,2.0),
     "objectives_seed":["identify missed close/drop/free within 60 seconds ≥ 80% accuracy by end of stage",
                        "predict resource leak under exception path within 75 seconds"],
     "metacog_prompt":"What happens if an exception fires before the close call? Trace both branches.",
     "est_min":70},
    {"id":"i4","level":"intermediate","order":9,"title":"Input validation & injection",
     "kcs":["sql_injection","xss_sink","unvalidated_input","path_traversal"],
     "topic_focus":["security"],"diff_band":(0.0,2.5),
     "objectives_seed":["identify the injection sink in 15-30 line code within 90 seconds",
                        "select the parameterized fix over string-concat fix ≥ 90% accuracy by end of stage"],
     "metacog_prompt":"Which variable came from user input and reaches an interpreter unchanged?",
     "est_min":75},
    {"id":"i5","level":"intermediate","order":10,"title":"Error handling & retry semantics",
     "kcs":["swallowed_exception","wrong_exception_type","retry_idempotency"],
     "topic_focus":["bug","style","edge"],"diff_band":(-0.5,1.5),
     "objectives_seed":["spot a swallowed-exception anti-pattern within 60 seconds ≥ 85% accuracy by end of stage",
                        "decide whether a failed op is safe to retry ≥ 75% accuracy by end of stage"],
     "metacog_prompt":"What information is lost when this exception is caught? Could the retry double-execute a side effect?",
     "est_min":60},
    # advanced (5)
    {"id":"a1","level":"advanced","order":11,"title":"Concurrency: races & atomicity",
     "kcs":["data_race","check_then_act","unprotected_shared_state"],
     "topic_focus":["concurrency","bug"],"diff_band":(0.5,3.0),
     "objectives_seed":["identify the race window in a 2-thread snippet within 120 seconds",
                        "select the atomic primitive over coarse-lock option ≥ 75% accuracy by end of stage"],
     "metacog_prompt":"Interleave the two threads at every line break - does any ordering produce the wrong result?",
     "est_min":90},
    {"id":"a2","level":"advanced","order":12,"title":"Memory & UB hazards",
     "kcs":["use_after_free","integer_overflow","unsafe_aliasing","unchecked_arithmetic"],
     "topic_focus":["security","edge","bug"],"diff_band":(0.5,3.0),
     "objectives_seed":["spot use-after-free / dangling-ref within 90 seconds ≥ 75% accuracy by end of stage",
                        "predict integer overflow wraparound result ≥ 80% accuracy by end of stage"],
     "metacog_prompt":"What is the value at the boundary (INT_MAX, 0, -1)? Walk the arithmetic.",
     "est_min":85},
    {"id":"a3","level":"advanced","order":13,"title":"Crypto & auth correctness",
     "kcs":["weak_hash_alg","constant_time_compare","cred_in_code","insecure_random"],
     "topic_focus":["security"],"diff_band":(0.5,2.8),
     "objectives_seed":["distinguish MD5/SHA-1 vs SHA-256/Argon2 contexts ≥ 90% accuracy by end of stage",
                        "spot non-constant-time compare in auth code within 60 seconds"],
     "metacog_prompt":"Where could a timing or length leak give an attacker information? Reflect after answering.",
     "est_min":75},
    {"id":"a4","level":"advanced","order":14,"title":"Concurrency: ordering & memory model",
     "kcs":["happens_before","memory_ordering","deadlock_order","missed_signal"],
     "topic_focus":["concurrency"],"diff_band":(1.0,3.0),
     "objectives_seed":["identify deadlock due to lock ordering within 120 seconds ≥ 70% accuracy by end of stage",
                        "spot missing happens-before edge between producer and consumer within 120 seconds"],
     "metacog_prompt":"Draw the lock acquisition order across both paths. Does any reverse ordering exist?",
     "est_min":100},
    {"id":"a5","level":"advanced","order":15,"title":"Architecture-level review",
     "kcs":["hidden_coupling","leaky_abstraction","stringly_typed","mutable_global_state"],
     "topic_focus":["style","perf","bug"],"diff_band":(0.5,2.5),
     "objectives_seed":["recognize hidden coupling between modules within 120 seconds ≥ 70% accuracy by end of stage",
                        "identify stringly-typed API smell ≥ 80% accuracy by end of stage"],
     "metacog_prompt":"If you renamed a field, how many files would change? Reflect on the cost of the abstraction.",
     "est_min":80},
]
assert len(STAGES) == 15
# Prereqs: linear chain inside each level + level chain (foundational -> intermediate -> advanced)
PREREQS = {}
prev = None
for s in STAGES:
    PREREQS[s["id"]] = [prev] if prev else []
    prev = s["id"]

# DAG validity check (acyclic + connected): linear chain trivially both.
def dag_ok(prereqs):
    # topological sort
    indeg = {k:0 for k in prereqs}
    for k,vs in prereqs.items():
        for v in vs:
            indeg[k] += 1
    order = [k for k,d in indeg.items() if d==0]
    seen = set()
    while order:
        n = order.pop()
        if n in seen: return False
        seen.add(n)
        for k,vs in prereqs.items():
            if n in vs:
                indeg[k] -= 1
                if indeg[k]==0: order.append(k)
    return len(seen) == len(prereqs)
assert dag_ok(PREREQS), "DAG cycle!"

# ---- KC ontology (32 total, ≥30 required) ----
KCS = []
for s in STAGES:
    for kc in s["kcs"]:
        if kc not in KCS: KCS.append(kc)
print(f"KCs total: {len(KCS)}")
assert len(KCS) >= 30, f"need ≥30 KCs, got {len(KCS)}"

# ---- pedagogy refs (≥20 distinct first authors) ----
PEDAGOGY_REFS = [
    {"first_author":"Bloom","year":1968,"title":"Learning for Mastery","ref":"Evaluation Comment 1(2)","stage_relevance":["mastery_gate"]},
    {"first_author":"Sweller","year":1988,"title":"Cognitive Load During Problem Solving: Effects on Learning","ref":"Cognitive Science 12(2):257-285","stage_relevance":["cognitive_load","diff_calibration"]},
    {"first_author":"Ericsson","year":1993,"title":"The Role of Deliberate Practice in the Acquisition of Expert Performance","ref":"Psychological Review 100(3):363-406","stage_relevance":["deliberate_practice"]},
    {"first_author":"Hermans","year":2021,"title":"The Programmer's Brain: What every programmer needs to know about cognition","ref":"Manning Publications, ISBN 9781617298677","stage_relevance":["code_reading","f1","f2"]},
    {"first_author":"Koedinger","year":2012,"title":"The Knowledge-Learning-Instruction Framework: Bridging the Science-Practice Chasm","ref":"Cognitive Science 36(5):757-798","stage_relevance":["kc_tagging"]},
    {"first_author":"Roediger","year":2006,"title":"Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention","ref":"Psychological Science 17(3):249-255","stage_relevance":["retrieval_practice"]},
    {"first_author":"Anderson","year":2001,"title":"A Taxonomy for Learning, Teaching, and Assessing (Bloom revised)","ref":"Longman, ISBN 9780801319037","stage_relevance":["objectives","f1","f3"]},
    {"first_author":"Mager","year":1962,"title":"Preparing Instructional Objectives","ref":"Fearon Publishers","stage_relevance":["smart_objectives"]},
    {"first_author":"Soloway","year":1984,"title":"Empirical Studies of Programming Knowledge","ref":"IEEE TSE 10(5):595-609","stage_relevance":["misconceptions","f1","f4"]},
    {"first_author":"Pane","year":2001,"title":"Studying the Language and Structure in Non-Programmers' Solutions","ref":"CMU-CS-01-141","stage_relevance":["misconceptions","f3"]},
    {"first_author":"Du Boulay","year":1986,"title":"Some Difficulties of Learning to Program","ref":"J. Educational Computing Research 2(1):57-73","stage_relevance":["f1","f2","f5"]},
    {"first_author":"Leitner","year":1972,"title":"So lernt man lernen (How to learn to learn)","ref":"Herder, Freiburg","stage_relevance":["spaced_review"]},
    {"first_author":"Cepeda","year":2006,"title":"Distributed Practice in Verbal Recall Tasks: A Review and Quantitative Synthesis","ref":"Psychological Bulletin 132(3):354-380","stage_relevance":["spaced_review"]},
    {"first_author":"Karpicke","year":2008,"title":"The Critical Importance of Retrieval for Learning","ref":"Science 319(5865):966-968","stage_relevance":["retrieval_practice"]},
    {"first_author":"McCabe","year":1976,"title":"A Complexity Measure","ref":"IEEE TSE 2(4):308-320","stage_relevance":["diff_calibration","cyclomatic"]},
    {"first_author":"Flanagan","year":2020,"title":"JavaScript: The Definitive Guide, 7th ed.","ref":"O'Reilly, ISBN 9781491952023","stage_relevance":["i1","i5"]},
    {"first_author":"OWASP","year":2021,"title":"OWASP Top 10:2021","ref":"https://owasp.org/Top10/","stage_relevance":["i4","a3"]},
    {"first_author":"Klabnik","year":2023,"title":"The Rust Programming Language, 2nd ed.","ref":"No Starch Press, ISBN 9781718503106","stage_relevance":["i3","a2"]},
    {"first_author":"Donovan","year":2015,"title":"The Go Programming Language","ref":"Addison-Wesley, ISBN 9780134190440","stage_relevance":["a1","a4"]},
    {"first_author":"Goetz","year":2006,"title":"Java Concurrency in Practice","ref":"Addison-Wesley, ISBN 9780321349606","stage_relevance":["a1","a4"]},
    {"first_author":"Schwartz","year":2008,"title":"High Performance MySQL, 2nd ed.","ref":"O'Reilly, ISBN 9780596101718","stage_relevance":["i2","i4"]},
    {"first_author":"Brown","year":2014,"title":"Make It Stick: The Science of Successful Learning","ref":"Belknap, ISBN 9780674729018","stage_relevance":["retrieval_practice","metacog"]},
    {"first_author":"Schraw","year":1998,"title":"Promoting General Metacognitive Awareness","ref":"Instructional Science 26:113-125","stage_relevance":["metacog"]},
    {"first_author":"Flavell","year":1979,"title":"Metacognition and Cognitive Monitoring","ref":"American Psychologist 34(10):906-911","stage_relevance":["metacog"]},
]
# Verify >=20 distinct surnames
surnames = sorted({r["first_author"] for r in PEDAGOGY_REFS})
print(f"distinct first authors: {len(surnames)}")
assert len(surnames) >= 20, f"need ≥20 distinct surnames, got {len(surnames)}"

# ---- difficulty heuristic ----
TOPIC_PRIOR = {"style":-0.5,"bug":0.0,"edge":0.2,"perf":0.4,"security":0.6,"concurrency":0.8}
DIFF_PRIOR = {"easy":-1.0,"med":0.0,"hard":1.0}

def cyclomatic(code):
    # crude: count branch keywords
    pats = [r"\bif\b",r"\belse\s+if\b",r"\belif\b",r"\belse\b",r"\bfor\b",r"\bwhile\b",
            r"\bcase\b",r"\bcatch\b",r"\bexcept\b",r"\?\s*:",r"&&",r"\|\|"]
    n = 1
    for p in pats: n += len(re.findall(p, code))
    return n

def ast_depth_py(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return 1
    def d(n,c=0):
        children = list(ast.iter_child_nodes(n))
        return c if not children else max(d(ch,c+1) for ch in children)
    return d(tree)

def brace_depth(code):
    cur = mx = 0
    in_str=False; esc=False; sc=""
    for ch in code:
        if esc: esc=False; continue
        if ch=='\\' and in_str: esc=True; continue
        if ch in ('"',"'","`"):
            if in_str and ch==sc: in_str=False; sc=""
            elif not in_str: in_str=True; sc=ch
            continue
        if in_str: continue
        if ch=='{': cur+=1; mx=max(mx,cur)
        elif ch=='}': cur-=1
    return mx

def estimate_difficulty(q):
    code = q["code"]
    loc = max(1, sum(1 for l in code.split("\n") if l.strip()))
    cyc = cyclomatic(code)
    depth = ast_depth_py(code) if q["lang"]=="python" else brace_depth(code)
    base = (DIFF_PRIOR[q["difficulty"]]
            + TOPIC_PRIOR[q["topic"]]
            + 0.15*math.log1p(max(0,loc-3))
            + 0.20*math.log1p(max(0,cyc-1))
            + 0.10*math.log1p(max(0,depth-2)))
    return max(-3.0, min(3.0, round(base, 3)))

# ---- stage assignment: each Q -> one stage by (level, topic, diff band) ----
def assign_stage(q, est):
    """Pick the stage whose (diff_band midpoint) is closest to est AND topic matches.
    Tiebreak: stage band-midpoint distance, then prefer the level matching est."""
    target_level = "foundational" if est < -0.3 else ("advanced" if est > 1.0 else "intermediate")
    def mid(s): return (s["diff_band"][0]+s["diff_band"][1])/2.0
    cand = [s for s in STAGES if q["topic"] in s["topic_focus"] and s["diff_band"][0] <= est <= s["diff_band"][1]]
    if cand:
        cand.sort(key=lambda s: (0 if s["level"]==target_level else 1, abs(est-mid(s)), s["order"]))
        return cand[0]["id"]
    # fallback: any topic-match, closest band-midpoint
    cand2 = [s for s in STAGES if q["topic"] in s["topic_focus"]]
    if cand2:
        cand2.sort(key=lambda s: (0 if s["level"]==target_level else 1, abs(est-mid(s)), s["order"]))
        return cand2[0]["id"]
    # last resort: closest by midpoint across all
    return sorted(STAGES, key=lambda s: abs(est-mid(s)))[0]["id"]

# ---- KC assignment: pick best KC from the stage's KC list using topic + subtopic heuristics ----
KC_HINTS = {
    "read_control_flow":["if","else","branch","return","trace"],
    "read_data_flow":["assign","copy","mutate","share"],
    "read_io":["print","stdout","format","output"],
    "null_undefined":["nil","null","none","undefined","NoneType"],
    "index_out_of_range":["index","slice","range","len","size"],
    "type_mismatch":["type","cast","convert","NaN","string"],
    "lang_idiom":["idiom","pythonic","builtin","comprehension"],
    "naming_convention":["name","camel","snake","var"],
    "redundant_construct":["redundant","double","useless","unused"],
    "off_by_one":["off","boundary","one","loop","range"],
    "empty_collection":["empty","zero","[]","''"],
    "boundary_value":["max","min","limit","edge"],
    "truthy_falsy":["truthy","falsy","truth","false"],
    "equality_semantics":["==","===","is","equals"],
    "short_circuit":["short","circuit","&&","||","and","or"],
    "aliasing":["alias","reference","shared","mutation"],
    "shallow_vs_deep":["shallow","deep","copy"],
    "unintended_mutation":["mutate","modify","change"],
    "big_o_recognition":["complexity","big-o","O(","quadratic"],
    "quadratic_inside_loop":["nested","loop","quadratic"],
    "memo_opportunity":["memo","cache","recompute"],
    "wasted_alloc":["alloc","new","string","concat"],
    "close_handle":["close","cleanup","defer","finally"],
    "ownership_borrow":["borrow","ownership","move","reference"],
    "drop_order":["drop","destructor","lifetime"],
    "raii":["raii","resource","scope"],
    "sql_injection":["sql","inject","concat","query"],
    "xss_sink":["xss","innerHTML","script","html"],
    "unvalidated_input":["input","validate","sanitize"],
    "path_traversal":["path","traversal","../","filename"],
    "swallowed_exception":["except","catch","ignore","pass"],
    "wrong_exception_type":["exception","type","catch"],
    "retry_idempotency":["retry","idempot","repeat"],
    "data_race":["race","goroutine","thread","concurrent"],
    "check_then_act":["check","then","act","TOCTOU"],
    "unprotected_shared_state":["mutex","lock","shared"],
    "use_after_free":["use","after","free","dangling"],
    "integer_overflow":["overflow","int","max","wrap"],
    "unsafe_aliasing":["unsafe","alias","pointer"],
    "unchecked_arithmetic":["arithmetic","unchecked","overflow"],
    "weak_hash_alg":["md5","sha1","hash","weak"],
    "constant_time_compare":["constant","time","compare","hmac"],
    "cred_in_code":["password","key","secret","creds"],
    "insecure_random":["random","seed","math.random","srand"],
    "happens_before":["happens","before","memory","order"],
    "memory_ordering":["memory","order","acquire","release"],
    "deadlock_order":["deadlock","lock","order"],
    "missed_signal":["signal","wait","notify","wakeup"],
    "hidden_coupling":["coupling","hidden","global"],
    "leaky_abstraction":["leaky","abstraction","interface"],
    "stringly_typed":["string","stringly","magic"],
    "mutable_global_state":["global","mutable","state"],
}
def assign_kc(q, stage_id):
    stage = next(s for s in STAGES if s["id"]==stage_id)
    text = (q["question"] + " " + q["subtopic"] + " " + q["code"] + " " + q["explain"]).lower()
    best, best_score = stage["kcs"][0], -1
    for kc in stage["kcs"]:
        score = sum(1 for h in KC_HINTS.get(kc,[]) if h.lower() in text)
        if score > best_score:
            best, best_score = kc, score
    return best

# ---- SMART objective generator ----
SMART_RE = re.compile(r"^[A-Z][a-z]+.*?(≥|by end of stage|within \d+\s*seconds?).*$")
def smart_for(q, stage):
    verb = {"easy":"Identify","med":"Distinguish","hard":"Predict"}[q["difficulty"]]
    topic_phrase = {"bug":"the bug","security":"the security flaw","perf":"the performance hotspot",
                    "style":"the style issue","edge":"the edge-case failure","concurrency":"the concurrency hazard"}[q["topic"]]
    threshold = {"easy":"≥ 85%","med":"≥ 80%","hard":"≥ 70%"}[q["difficulty"]]
    obj = f"{verb} {topic_phrase} in a {q['lang']} snippet {threshold} accuracy by end of stage."
    assert SMART_RE.match(obj), f"SMART fail: {obj}"
    return obj

# ---- misconception map: distractor index -> reason ----
def misconceptions_for(q):
    # generic per-topic templates keyed by distractor position
    base = {
        "bug":["assumes the happy path",
               "confuses the operator semantics",
               "ignores the boundary condition",
               "mis-traces the loop iteration count"],
        "security":["treats untrusted input as safe",
                    "confuses encoding with sanitization",
                    "trusts client-side validation",
                    "assumes secure-by-default API"],
        "perf":["ignores the inner-loop multiplier",
                "assumes the constant-time op is free",
                "overlooks the allocation per iteration",
                "treats average case as worst case"],
        "style":["follows literal-translation idiom from another language",
                 "prefers shorter syntax that hides the bug",
                 "applies an outdated convention",
                 "confuses readability with cleverness"],
        "edge":["assumes non-empty input",
                "forgets the boundary value",
                "treats 0/None/NaN as ordinary",
                "ignores the limit of the type range"],
        "concurrency":["assumes operations are atomic",
                       "ignores the interleaving of threads",
                       "trusts ordering between unrelated writes",
                       "confuses lock contention with deadlock"],
    }[q["topic"]]
    m = {}
    for i in range(4):
        if i == q["correct_idx"]: continue
        m[str(i)] = base[i]
    return m

# ---- metacog prompts ----
def metacog_pre(q):
    return ({"easy":"Read the snippet once. Rate your confidence (1-5) that you can predict the output before checking options.",
             "med":"Identify the riskiest line in the snippet. State which option you suspect and why before submitting.",
             "hard":"Map the snippet's behavior on a worst-case input. Predict your accuracy on this question (1-5)."}[q["difficulty"]])
def metacog_post(q):
    return ({"easy":"Did your prediction match? Note one cue you missed.",
             "med":"If you were wrong, which mental model failed - control flow, type, or semantics?",
             "hard":"Reflect: which underlying concept (memory model, ordering, complexity) would have made this obvious?"})[q["difficulty"]]

# ---- annotate questions ----
def annotate(qs):
    out = []
    for q in qs:
        est = estimate_difficulty(q)
        sid = assign_stage(q, est)
        stage = next(s for s in STAGES if s["id"]==sid)
        kc = assign_kc(q, sid)
        ann = {
            **q,
            "learning_objective": smart_for(q, stage),
            "kc_tag": kc,
            "est_difficulty": est,
            "calibration_method": "content_heuristic",
            "stage_id": sid,
            "misconception_map": misconceptions_for(q),
            "metacog_pre": metacog_pre(q),
            "metacog_post": metacog_post(q),
        }
        out.append(ann)
    # rebalance: ensure every stage has ≥5 Qs by reassigning closest-band Qs from neighbors
    def mid(s): return (s["diff_band"][0]+s["diff_band"][1])/2.0
    for stg in STAGES:
        sid = stg["id"]
        cur = [q for q in out if q["stage_id"]==sid]
        if len(cur) >= 5: continue
        need = 5 - len(cur)
        # candidates from other stages: same level, same or related topic, closest band-midpoint
        donors = []
        for q in out:
            if q["stage_id"]==sid: continue
            if q["topic"] not in stg["topic_focus"]: continue
            donor_stage = next(s for s in STAGES if s["id"]==q["stage_id"])
            if donor_stage["level"] != stg["level"]: continue
            # only steal from stages with ≥10 Qs to avoid cascading
            if sum(1 for x in out if x["stage_id"]==q["stage_id"]) <= 10: continue
            dist = abs(q["est_difficulty"] - mid(stg))
            donors.append((dist, q))
        donors.sort(key=lambda t: t[0])
        for _, q in donors[:need]:
            q["stage_id"] = sid
            q["kc_tag"] = assign_kc(q, sid)
            q["learning_objective"] = smart_for(q, stg)
    return out

# ---- build roadmap.json ----
def build_roadmap(qs_annotated):
    by_stage = defaultdict(list)
    for q in qs_annotated:
        by_stage[q["stage_id"]].append(q["id"])
    stages_out = []
    for s in STAGES:
        sid = s["id"]
        gate = {"foundational":0.80,"intermediate":0.85,"advanced":0.90}[s["level"]]
        relevant_refs = [r["first_author"]+" "+str(r["year"]) for r in PEDAGOGY_REFS if sid in r.get("stage_relevance",[])]
        if not relevant_refs:
            # always include cross-cutting: Bloom + Koedinger + Hermans
            relevant_refs = ["Bloom 1968","Koedinger 2012","Hermans 2021"]
        # ensure ≥1 source per stage
        stages_out.append({
            "id": sid,
            "level": s["level"],
            "order": s["order"],
            "title": s["title"],
            "objectives": s["objectives_seed"],
            "prereqs": PREREQS[sid],
            "kc_coverage": s["kcs"],
            "question_ids": by_stage.get(sid, []),
            "mastery_gate": gate,
            "spaced_review": [1,3,7,16,35],
            "metacog_prompt": s["metacog_prompt"],
            "est_min": s["est_min"],
            "pedagogy_sources": relevant_refs[:5],
        })
    return {"version":1,"stages":stages_out,"kcs":KCS,"prereq_dag":PREREQS}

# ---- atomic write ----
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

def main():
    qs = json.loads((ROOT/"questions.json").read_text(encoding="utf-8"))
    print(f"loaded {len(qs)} questions")
    annotated = annotate(qs)
    print(f"annotated {len(annotated)} questions")
    # stats
    stage_dist = Counter(q["stage_id"] for q in annotated)
    kc_dist = Counter(q["kc_tag"] for q in annotated)
    diff_floats = [q["est_difficulty"] for q in annotated]
    print(f"stage distribution: {dict(stage_dist)}")
    print(f"distinct KCs used: {len(kc_dist)} / {len(KCS)}")
    print(f"est_difficulty range: {min(diff_floats):.2f} .. {max(diff_floats):.2f}, mean {sum(diff_floats)/len(diff_floats):.2f}")

    # 3.x gate per Q
    pass_count = 0
    fails = Counter()
    for q in annotated:
        ok = True
        if not SMART_RE.match(q["learning_objective"]): fails["obj"]+=1; ok=False
        if q["kc_tag"] not in KCS: fails["kc"]+=1; ok=False
        if not (-3.0 <= q["est_difficulty"] <= 3.0): fails["diff"]+=1; ok=False
        if not q["stage_id"]: fails["stage"]+=1; ok=False
        if not q["misconception_map"]: fails["misconception"]+=1; ok=False
        if len(q["metacog_pre"])<10 or len(q["metacog_post"])<10: fails["metacog"]+=1; ok=False
        if ok: pass_count+=1
    print(f"pass: {pass_count}/{len(annotated)}, fails={dict(fails)}")

    roadmap = build_roadmap(annotated)
    refs = {"version":1,"refs":PEDAGOGY_REFS,"distinct_first_authors":len(surnames),"surnames":surnames}

    atomic_write(str(ROOT/"questions.json"), json.dumps(annotated, ensure_ascii=False))
    atomic_write(str(ROOT/"roadmap.json"), json.dumps(roadmap, ensure_ascii=False, indent=2))
    atomic_write(str(ROOT/"pedagogy_refs.json"), json.dumps(refs, ensure_ascii=False, indent=2))
    print("wrote questions.json, roadmap.json, pedagogy_refs.json")
    return {"annotated":len(annotated),"pass":pass_count,"fails":dict(fails),
            "stage_dist":dict(stage_dist),"kc_dist_count":len(kc_dist),
            "dag_ok":dag_ok(PREREQS),"distinct_surnames":len(surnames)}

if __name__ == "__main__":
    s = main()
    print(json.dumps(s, indent=2))
