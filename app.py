"""Local quiz web app — serves questions.json (compacted from questions.jsonl)."""
from __future__ import annotations
import json, pathlib, os
from flask import Flask, jsonify, render_template, send_from_directory, abort

ROOT = pathlib.Path(__file__).parent
QUESTIONS_JSON = ROOT / "questions.json"
QUESTIONS_JSONL = ROOT / "questions.jsonl"

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

QUESTIONS = load_questions()

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

@app.errorhandler(404)
def nf(e):
    return jsonify({"error": "not found"}), 404

if __name__ == "__main__":
    print(f"Loaded {len(QUESTIONS)} questions.")
    app.run(host="127.0.0.1", port=5000, debug=False)
