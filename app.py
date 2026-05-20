"""Quiz app — flat quiz + global roadmap + per-lang tracks + progress + improvements."""
from __future__ import annotations
import json, pathlib, os
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

LANGS = ["python","javascript","go","rust","sql"]

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

QS_BY_LANG = {l: [q for q in QUESTIONS if q["lang"]==l] for l in LANGS}

# ---------------- Landing + flat quiz (legacy preserved) ----------------

@app.route("/")
def index():
    return render_template("landing.html", total=len(QUESTIONS))

@app.route("/quiz")
def flat_quiz():
    return render_template("index.html", total=len(QUESTIONS))

@app.route("/review")
def review():
    return render_template("index.html", total=len(QUESTIONS), review=True)

# ---------------- Legacy roadmap routes (preserved + redirects) ----------------

@app.route("/roadmap")
def roadmap_legacy():
    # Spec §6: legacy /roadmap → 302 /lang/python/roadmap
    return redirect("/lang/python/roadmap", code=302)

@app.route("/roadmap/global")
def roadmap_global():
    # Preserves the global cross-lang roadmap view (prior feature, immutable).
    return render_template("roadmap.html", total=len(QUESTIONS), n_stages=len(ROADMAP.get("stages",[])))

@app.route("/lesson/<stage_id>")
def lesson_legacy(stage_id):
    stage = next((s for s in ROADMAP.get("stages",[]) if s["id"]==stage_id), None)
    if not stage: abort(404)
    return render_template("lesson.html", stage=stage, total=len(QUESTIONS))

@app.route("/mastery")
def mastery_legacy():
    # Spec §6: legacy /mastery → 302 /lang/python/mastery
    return redirect("/lang/python/mastery", code=302)

@app.route("/mastery/global")
def mastery_global():
    return render_template("mastery.html", total=len(QUESTIONS), n_kcs=len(ROADMAP.get("kcs",[])))

# ---------------- Per-lang tracks ----------------

def _stage_for(lang, stage_id):
    stages = ROADMAP_PERLANG.get("per_lang_stages",{}).get(lang, [])
    return next((s for s in stages if s["id"]==stage_id), None)

@app.route("/lang/<lang>")
def lang_dashboard(lang):
    if lang not in LANGS: abort(404)
    return render_template("lang_dashboard.html", lang=lang, q_count=len(QS_BY_LANG[lang]))

@app.route("/lang/<lang>/roadmap")
def lang_roadmap(lang):
    if lang not in LANGS: abort(404)
    return render_template("lang_roadmap.html", lang=lang)

@app.route("/lang/<lang>/lesson/<stage_id>")
def lang_lesson(lang, stage_id):
    if lang not in LANGS: abort(404)
    stage = _stage_for(lang, stage_id)
    if not stage: abort(404)
    return render_template("lang_lesson.html", lang=lang, stage=stage)

@app.route("/lang/<lang>/mastery")
def lang_mastery(lang):
    if lang not in LANGS: abort(404)
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
def api_questions(): return jsonify(QUESTIONS)

@app.route("/api/meta")
def api_meta():
    langs = sorted({q["lang"] for q in QUESTIONS})
    topics = sorted({q["topic"] for q in QUESTIONS})
    difficulties = sorted({q["difficulty"] for q in QUESTIONS})
    return jsonify({"total": len(QUESTIONS), "langs": langs, "topics": topics, "difficulties": difficulties})

@app.route("/api/roadmap")
def api_roadmap(): return jsonify(ROADMAP)

@app.route("/api/pedagogy")
def api_pedagogy(): return jsonify(PEDAGOGY)

@app.route("/api/stage/<stage_id>")
def api_stage(stage_id):
    stage = next((s for s in ROADMAP.get("stages",[]) if s["id"]==stage_id), None)
    if not stage: abort(404)
    qids = set(stage.get("question_ids", []))
    qs = [q for q in QUESTIONS if q["id"] in qids]
    return jsonify({"stage": stage, "questions": qs})

# Per-lang API
@app.route("/api/lang/<lang>/roadmap")
def api_lang_roadmap(lang):
    if lang not in LANGS: abort(404)
    return jsonify({"lang": lang,
                    "stages": ROADMAP_PERLANG.get("per_lang_stages",{}).get(lang, []),
                    "kcs": ROADMAP_PERLANG.get("per_lang_kcs",{}).get(lang, []),
                    "lang_specific_kcs": ROADMAP_PERLANG.get("lang_specific_kcs",{}).get(lang, [])})

@app.route("/api/lang/<lang>/stage/<stage_id>")
def api_lang_stage(lang, stage_id):
    if lang not in LANGS: abort(404)
    stage = _stage_for(lang, stage_id)
    if not stage: abort(404)
    qids = set(stage.get("question_ids", []))
    qs = [q for q in QUESTIONS if q["id"] in qids]
    return jsonify({"stage": stage, "questions": qs, "lang": lang})

# Cohort + improvements + audit APIs
@app.route("/api/cohort_progress")
def api_cohort():
    return jsonify({
        "by_iter": LEARNERS.get("cohort_pass_rate_by_iter", {}),
        "n_learners": LEARNERS.get("distinct_learner_ids_cum", 0),
        "method": LEARNERS.get("simulation_method", "unknown"),
    })

@app.route("/api/learners")
def api_learners(): return jsonify(LEARNERS)

@app.route("/api/improvements")
def api_improvements(): return jsonify(IMPS)

@app.route("/api/research_refs")
def api_research_refs(): return jsonify(REFS)

@app.errorhandler(404)
def nf(e): return jsonify({"error": "not found"}), 404

if __name__ == "__main__":
    print(f"Loaded {len(QUESTIONS)} questions, {len(ROADMAP.get('stages',[]))} global stages, "
          f"{sum(len(v) for v in ROADMAP_PERLANG.get('per_lang_stages',{}).values())} per-lang stage instances, "
          f"{len(IMPS.get('improvements',[]))} improvements, {LEARNERS.get('distinct_learner_ids_cum',0)} learner_ids.")
    app.run(host="127.0.0.1", port=5000, debug=False)
