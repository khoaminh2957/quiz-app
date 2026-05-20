# Quiz app

Flask web app with 1,141 multiple-choice code-review questions covering Python, JavaScript, Go, Rust, and SQL.

## Run locally

```bash
pip install flask
python app.py
# open http://127.0.0.1:5000
```

## Question pool

- Languages: python 286, javascript 237, go 222, sql 221, rust 175
- Topics: style 234, bug 232, perf 177, edge 175, concurrency 162, security 161
- Difficulty: easy 419, med 524, hard 198

## UI

Prism highlighting with copy-to-clipboard buttons. Four-option MCQ with submit, correctness feedback, explanation, and source links. Keyboard shortcuts: 1-4 to pick, Enter to submit, B for back, R to reset. Progress is saved to `localStorage` and resumes on reload. Sequential or random order, client-side filters by language/topic/difficulty, a `/review` page for saved answers, dark-mode toggle, 50 questions per lazy page, mobile responsive.

## Deploy on Vercel

`api/index.py` and `vercel.json` are included. Import the repo at https://vercel.com/new.

## Validators (build-time)

`validate.py` runs the schema + per-language code-execution gates (ast.parse, `node --check`, `gofmt -e`, `rustc --emit=metadata`, `sqlglot postgres`), API-existence regex, distractor-quality, and pedagogy checks. `dedup_cosine.py` does a sentence-transformers `all-MiniLM-L6-v2` cosine >= 0.85 lang-sharded dedup pass.

See `INCOMPLETE.md` for the spec-compliance scorecard.
