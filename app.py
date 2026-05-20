"""Quiz app — chỉ Python, giao diện tiếng Việt."""
from __future__ import annotations
import json, pathlib, os, hashlib
from flask import Flask, jsonify, render_template, send_from_directory, abort, redirect, url_for

ROOT = pathlib.Path(__file__).parent
QUESTIONS_JSON       = ROOT / "questions.json"
QUESTIONS_JSONL      = ROOT / "questions.jsonl"
ROADMAP_JSON         = ROOT / "roadmap.json"
ROADMAP_PERLANG_JSON = ROOT / "roadmap_perlang.json"
PEDAGOGY_REFS_JSON   = ROOT / "pedagogy_refs.json"
IMPROVEMENT_LOG      = ROOT / "improvement_log.json"
LEARNER_REGISTRY     = ROOT / "learner_registry.json"
RESEARCH_REFS        = ROOT / "research_refs.json"

# Python-only focus per latest /goal
PRIMARY_LANG = "python"
LANGS = [PRIMARY_LANG]

app = Flask(__name__, template_folder=str(ROOT/"templates"), static_folder=str(ROOT/"static"))

def load_questions():
    if QUESTIONS_JSON.exists():
        return json.loads(QUESTIONS_JSON.read_text(encoding="utf-8"))
    items = []
    if QUESTIONS_JSONL.exists():
        for line in QUESTIONS_JSONL.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line: items.append(json.loads(line))
    return items

def load_json(p, default=None):
    if p.exists(): return json.loads(p.read_text(encoding="utf-8"))
    return default if default is not None else {}

QUESTIONS = load_questions()
ROADMAP   = load_json(ROADMAP_JSON, {"version":1,"stages":[],"kcs":[]})
ROADMAP_PERLANG = load_json(ROADMAP_PERLANG_JSON, {"version":1,"per_lang_stages":{}})
PEDAGOGY  = load_json(PEDAGOGY_REFS_JSON, {"refs":[]})
IMPS      = load_json(IMPROVEMENT_LOG, {"improvements":[]})
LEARNERS  = load_json(LEARNER_REGISTRY, {"learners":[],"logs":[]})
REFS      = load_json(RESEARCH_REFS, {"refs":{}})

def _etag_for(data_bytes):
    return hashlib.sha1(data_bytes, usedforsecurity=False).hexdigest()[:16]

def _add_cache_headers(resp, max_age=300):
    resp.headers["Cache-Control"] = f"public, max-age={max_age}"
    return resp

# ---------------- Landing (Python-only, tiếng Việt) ----------------

@app.route("/")
def index():
    # Direct landing on the Python dashboard
    return render_template("landing.html", total=len(QUESTIONS))

@app.route("/quiz")
def flat_quiz():
    return render_template("index.html", total=len(QUESTIONS))

@app.route("/review")
def review():
    return render_template("index.html", total=len(QUESTIONS), review=True)

# ---------------- Legacy roadmap routes (redirect) ----------------

@app.route("/roadmap")
def roadmap_legacy():
    return redirect("/lang/python/roadmap", code=302)

@app.route("/roadmap/global")
def roadmap_global():
    return render_template("roadmap.html", total=len(QUESTIONS), n_stages=len(ROADMAP.get("stages",[])))

@app.route("/lesson/<stage_id>")
def lesson_legacy(stage_id):
    stage = next((s for s in ROADMAP.get("stages",[]) if s["id"]==stage_id), None)
    if not stage: abort(404)
    return render_template("lesson.html", stage=stage, total=len(QUESTIONS))

@app.route("/mastery")
def mastery_legacy():
    return redirect("/lang/python/mastery", code=302)

@app.route("/mastery/global")
def mastery_global():
    return render_template("mastery.html", total=len(QUESTIONS), n_kcs=len(ROADMAP.get("kcs",[])))

# ---------------- Python track (other langs deprecated) ----------------

def _stage_for(lang, stage_id):
    stages = ROADMAP_PERLANG.get("per_lang_stages",{}).get(lang, [])
    return next((s for s in stages if s["id"]==stage_id), None)

@app.route("/lang/<lang>")
def lang_dashboard(lang):
    if lang != PRIMARY_LANG:
        # All non-Python langs redirect home (Python-only focus)
        return redirect("/", code=302)
    qs_lang = [q for q in QUESTIONS if q["lang"] == lang]
    return render_template("lang_dashboard.html", lang=lang, q_count=len(qs_lang))

@app.route("/lang/<lang>/roadmap")
def lang_roadmap(lang):
    if lang != PRIMARY_LANG:
        return redirect(f"/lang/{PRIMARY_LANG}/roadmap", code=302)
    return render_template("lang_roadmap.html", lang=lang)

@app.route("/lang/<lang>/lesson/<stage_id>")
def lang_lesson(lang, stage_id):
    if lang != PRIMARY_LANG:
        return redirect(f"/lang/{PRIMARY_LANG}/roadmap", code=302)
    stage = _stage_for(lang, stage_id)
    if not stage: abort(404)
    return render_template("lang_lesson.html", lang=lang, stage=stage)

@app.route("/lang/<lang>/mastery")
def lang_mastery(lang):
    if lang != PRIMARY_LANG:
        return redirect(f"/lang/{PRIMARY_LANG}/mastery", code=302)
    return render_template("lang_mastery.html", lang=lang)

# ---------------- Progress + improvements ----------------

@app.route("/progress")
def progress_view():
    return render_template("progress.html")

@app.route("/improvements")
def improvements_view():
    total = len(IMPS.get("improvements", []))
    return render_template("improvements.html", total=total)

# ---------------- APIs ----------------

@app.route("/api/questions")
def api_questions():
    body = json.dumps(QUESTIONS).encode("utf-8")
    etag = _etag_for(body)
    from flask import request, make_response
    if request.headers.get("If-None-Match") == etag:
        resp = make_response("", 304)
    else:
        resp = make_response(body)
        resp.headers["Content-Type"] = "application/json"
    resp.headers["ETag"] = etag
    return _add_cache_headers(resp, 3600)

@app.route("/api/meta")
def api_meta():
    langs = sorted({q["lang"] for q in QUESTIONS})
    topics = sorted({q["topic"] for q in QUESTIONS})
    difficulties = sorted({q["difficulty"] for q in QUESTIONS})
    return jsonify({"total": len(QUESTIONS), "langs": langs, "topics": topics, "difficulties": difficulties})

@app.route("/api/roadmap")
def api_roadmap(): return _add_cache_headers(jsonify(ROADMAP), 3600)

@app.route("/api/pedagogy")
def api_pedagogy(): return _add_cache_headers(jsonify(PEDAGOGY), 3600)

@app.route("/api/stage/<stage_id>")
def api_stage(stage_id):
    stage = next((s for s in ROADMAP.get("stages",[]) if s["id"]==stage_id), None)
    if not stage: abort(404)
    qids = set(stage.get("question_ids", []))
    qs = [q for q in QUESTIONS if q["id"] in qids]
    return jsonify({"stage": stage, "questions": qs})

@app.route("/api/lang/<lang>/roadmap")
def api_lang_roadmap(lang):
    if lang != PRIMARY_LANG: abort(404)
    return jsonify({"lang": lang,
                    "stages": ROADMAP_PERLANG.get("per_lang_stages",{}).get(lang, []),
                    "kcs": ROADMAP_PERLANG.get("per_lang_kcs",{}).get(lang, []),
                    "lang_specific_kcs": ROADMAP_PERLANG.get("lang_specific_kcs",{}).get(lang, [])})

@app.route("/api/lang/<lang>/stage/<stage_id>")
def api_lang_stage(lang, stage_id):
    if lang != PRIMARY_LANG: abort(404)
    stage = _stage_for(lang, stage_id)
    if not stage: abort(404)
    qids = set(stage.get("question_ids", []))
    qs = [q for q in QUESTIONS if q["id"] in qids]
    return jsonify({"stage": stage, "questions": qs, "lang": lang})

@app.route("/api/cohort_progress")
def api_cohort():
    return jsonify({
        "by_iter": LEARNERS.get("cohort_pass_rate_by_iter", {}),
        "n_learners": LEARNERS.get("distinct_learner_ids_cum", 0),
        "method": LEARNERS.get("simulation_method", "unknown"),
    })

@app.route("/api/learners")
def api_learners(): return _add_cache_headers(jsonify(LEARNERS), 1800)

@app.route("/api/improvements")
def api_improvements(): return _add_cache_headers(jsonify(IMPS), 1800)

@app.route("/api/research_refs")
def api_research_refs(): return _add_cache_headers(jsonify(REFS), 3600)


# ---------------- Debug routes (env-gated: FLASK_ENV=development) ----------------

def _is_dev():
    return os.environ.get("FLASK_ENV") == "development"

@app.route("/debug/bugs")
def debug_bugs():
    if not _is_dev(): abort(404)
    try:
        return jsonify(json.loads((ROOT/"bug_registry.json").read_text(encoding="utf-8")))
    except Exception:
        return jsonify({"bugs": []})

@app.route("/debug/coverage")
def debug_coverage():
    if not _is_dev(): abort(404)
    try:
        reg = json.loads((ROOT/"bug_registry.json").read_text(encoding="utf-8"))
        logs = reg.get("explorer_logs", [])
        from collections import Counter
        return jsonify({
            "explorers": len(logs),
            "routes_visited": Counter([r for L in logs for r in L.get("routes_visited",[])]),
            "bugs_per_route": Counter([b["route"] for b in reg.get("bugs",[])]),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug/changelog")
def debug_changelog():
    if not _is_dev(): abort(404)
    try:
        return jsonify(json.loads((ROOT/"fix_log.json").read_text(encoding="utf-8")))
    except Exception:
        return jsonify({"fixes": []})

@app.errorhandler(404)
def nf(e): return jsonify({"error": "không tìm thấy"}), 404

if __name__ == "__main__":
    print(f"Loaded {len(QUESTIONS)} Python questions, "
          f"{len(ROADMAP_PERLANG.get('per_lang_stages',{}).get('python',[]))} stages, "
          f"{len(IMPS.get('improvements',[]))} improvements.")
    app.run(host="127.0.0.1", port=5000, debug=False)
