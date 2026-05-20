# Quiz App — 1141 Code-Review MCQs

Flask app serving 1141 multiple-choice code-review questions across Python, JavaScript, Go, Rust, and SQL.

## Run locally

```bash
pip install flask
python app.py
# → http://127.0.0.1:5000
```

## Distribution

- **Languages:** python 286, javascript 237, go 222, sql 221, rust 175
- **Topics:** style 234, bug 232, perf 177, edge 175, concurrency 162, security 161
- **Difficulty:** easy 419, med 524, hard 198

## UI

Prism highlight + copy button · 4-option MCQ → submit → correctness + explain + sources · keyboard 1-4/Enter/→/B/R · `localStorage.quiz_progress` resume · sequential / random mode · client filter by lang/topic/difficulty · `/review` saved-answers view · dark-mode toggle · lazy 50/page · mobile-responsive.

## Deploy on Vercel

This repo includes `api/index.py` + `vercel.json` ready for one-click import on https://vercel.com/new.

## Validators (build-time)

`validate.py` runs the §3 gates: jsonschema, code-exec per language (ast.parse / `node --check` / `gofmt -e` / `rustc --emit=metadata` / `sqlglot postgres`), API-existence regex, distractor-quality, pedagogy. `dedup_cosine.py` runs sentence-transformers `all-MiniLM-L6-v2` cosine ≥ 0.85 lang-sharded full-pool dedup.

See `INCOMPLETE.md` for full spec-compliance scorecard.
