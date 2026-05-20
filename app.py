"""Local quiz web app — serves questions.json + roadmap.json (annotated with stage/KC/pedagogy)."""
from __future__ import annotations
import json, pathlib, os
from flask import Flask, jsonify, render_template, send_from_directory, abort

ROOT = pathlib.Path(__file__).parent
QUESTIONS_JSON = ROOT / "questions.json"
QUESTIONS_JSONL = ROOT / "questions.jsonl"
ROADMAP_JSON = ROOT / "roadmap.json"
PEDAGOGY_REFS_JSON = ROOT / "pedagogy_refs.json"

app = Flask(__name__, template_folder=str(ROOT/"templates"), static_folder=str(ROOT/"static"))

def load_questions():
    if QUESTIONS_JSON.exists():
        return json.loads(QUESTIONS_JSON.read_text(encoding="utf-8"))
    items = []
    if QUESTIONS_JSONL.exists():
        for line in QUESTIONS_JSONL.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def load_json(p):
    if p.exists(): return json.loads(p.read_text(encoding="utf-8"))
    return None

QUESTIONS = load_questions()
ROADMAP = load_json(ROADMAP_JSON) or {"version":1,"stages":[],"kcs":[]}
PEDAGOGY = load_json(PEDAGOGY_REFS_JSON) or {"refs":[]}

@app.route("/")
def index():
    return render_template("index.html", total=len(QUESTIONS))

@app.route("/api/questions")
def api_questions():
    return jsonify(QUESTIONS)

@app.route("/api/meta")
def api_meta():
    langs = sorted({q["lang"] for q in QUESTIONS})
    topics = sorted({q["topic"] for q in QUESTIONS})
    difficulties = sorted({q["difficulty"] for q in QUESTIONS})
    return jsonify({"total": len(QUESTIONS), "langs": langs, "topics": topics, "difficulties": difficulties})

@app.route("/review")
def review():
    return render_template("index.html", total=len(QUESTIONS), review=True)

# ---------------- Roadmap routes ----------------

@app.route("/roadmap")
def roadmap_view():
    return render_template("roadmap.html", total=len(QUESTIONS), n_stages=len(ROADMAP.get("stages",[])))

@app.route("/lesson/<stage_id>")
def lesson_view(stage_id):
    stage = next((s for s in ROADMAP.get("stages",[]) if s["id"]==stage_id), None)
    if not stage: abort(404)
    return render_template("lesson.html", stage=stage, total=len(QUESTIONS))

@app.route("/mastery")
def mastery_view():
    return render_template("mastery.html", total=len(QUESTIONS), n_kcs=len(ROADMAP.get("kcs",[])))

# ---------------- Roadmap APIs ----------------

@app.route("/api/roadmap")
def api_roadmap():
    return jsonify(ROADMAP)

@app.route("/api/pedagogy")
def api_pedagogy():
    return jsonify(PEDAGOGY)

@app.route("/api/stage/<stage_id>")
def api_stage(stage_id):
    stage = next((s for s in ROADMAP.get("stages",[]) if s["id"]==stage_id), None)
    if not stage: abort(404)
    qids = set(stage.get("question_ids", []))
    qs = [q for q in QUESTIONS if q["id"] in qids]
    return jsonify({"stage": stage, "questions": qs})

@app.errorhandler(404)
def nf(e):
    return jsonify({"error": "not found"}), 404

if __name__ == "__main__":
    print(f"Loaded {len(QUESTIONS)} questions, {len(ROADMAP.get('stages',[]))} stages, {len(ROADMAP.get('kcs',[]))} KCs.")
    app.run(host="127.0.0.1", port=5000, debug=False)
