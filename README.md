# CodeReview Quiz

A web app that trains the **code-review skill** — reading code and spotting bugs, security holes, perf traps, and style issues — the thing senior interviews and real work demand, that LeetCode/Codewars don't teach.

> **Positioning:** *They teach you to WRITE code. We train you to JUDGE it.*

Flask web app with **286 Python** multiple-choice code-review questions (the active pool is Python-only; see history below).

## Run locally

```bash
pip install flask
python app.py
# open http://127.0.0.1:5000
```

## Question pool (active)

- Language: **python 286** (the app currently serves Python only)
- Topics: style, bug, perf, edge, concurrency, security (6-category flaw taxonomy)
- Difficulty: easy / med / hard
- Each item: code snippet, 4 options, **server-graded** correct answer, explanation, sources

> Earlier iterations generated a larger multi-language pool (Python/JS/Go/Rust/SQL); the product was later focused to Python-only. `INCOMPLETE.md` documents that history.

## Product features

**Learning:** Prism syntax highlighting + copy buttons, 4-option MCQ with instant feedback + explanation, 15-stage pedagogy roadmap with mastery gates (80/85/90%), Leitner spaced repetition, per-category mastery, gamification (daily card, XP, streak), keyboard shortcuts, dark mode, `localStorage` progress.

**Market-ready (Phase 0 — "Measure & Position"):**
- **Answer-key integrity** — questions are shipped answer-stripped; grading is **server-side** via `POST /api/check` (the key never leaves the server in bulk).
- **Cookieless analytics** — `POST /api/event` funnel (anonymous client-id, no cookies/PII).
- **Email waitlist** — `POST /api/waitlist` → durable external sink via `WAITLIST_WEBHOOK_URL` env (Vercel FS is ephemeral).
- **Fake-door pricing** — `/pricing` with 3 market-anchored tiers to measure willingness-to-pay (zero billing code yet).
- **Programmatic SEO** — per-question SSR permalink `/q/<id>` + `/sitemap.xml` + `/robots.txt` + OG/JSON-LD.
- **Compliance** — `/privacy` + `/terms` (cookieless, minimal-data; Nghị định 13 / GDPR aligned).
- **Hardening** — per-IP rate limiting, `MAX_CONTENT_LENGTH`, payload sanitization, CSV/formula-injection defang on webhook forwards.

### Env vars

| Var | Purpose |
|---|---|
| `WAITLIST_WEBHOOK_URL` | POST target for durable waitlist leads (Sheets/Resend/Formspree/Supabase webhook) |
| `FLASK_ENV=development` | enables `/debug/*` inspection routes |

## API

`GET /api/questions/public` (answer-stripped) · `POST /api/check` (server grading) · `POST /api/event` · `POST /api/waitlist` · `GET /api/daily` · `GET /api/roadmap` `/api/pedagogy` `/api/meta` · `GET /sitemap.xml` `/robots.txt`

## Deploy on Vercel

`api/index.py` and `vercel.json` are included. Import the repo at https://vercel.com/new. Set `WAITLIST_WEBHOOK_URL` for durable leads.

## Product strategy & research

This product's go-to-market direction was developed by a **20-round, 426-agent research harness** (`harness/`) that web-researched the market against verified sources, caught hallucinations, and produced an end-to-end product plan. See **[`product-docs/`](product-docs/)**:

| Doc | What |
|---|---|
| [HARNESS_REPORT.md](product-docs/HARNESS_REPORT.md) | 20-round audit trail + consolidated P0/P1/P2 backlog (64 items) |
| [PRODUCT_RESEARCH.md](product-docs/PRODUCT_RESEARCH.md) | Cited market/competitor/pricing research dossier |
| [PRODUCT_SPEC.md](product-docs/PRODUCT_SPEC.md) | End-to-end product spec (MVP → v1 → v2) |
| [TECH_ARCHITECTURE.md](product-docs/TECH_ARCHITECTURE.md) | Architecture to scale (DB, auth, payments, infra) |
| [GTM_PLAN.md](product-docs/GTM_PLAN.md) | Positioning, pricing, channels, metrics |
| [ROADMAP.md](product-docs/ROADMAP.md) | Phased execution roadmap |
| [RISKS_AND_VALIDATION.md](product-docs/RISKS_AND_VALIDATION.md) | Risk register + anti-hallucination summary |
| [VERIFIED_SOURCES.md](product-docs/VERIFIED_SOURCES.md) · [HALLUCINATIONS_CAUGHT.md](product-docs/HALLUCINATIONS_CAUGHT.md) | 920 verified findings · 581 hallucination flags |

## Validators (build-time)

`validate.py` runs schema + per-language code-execution gates and pedagogy checks. `dedup_cosine.py` does a sentence-transformers cosine dedup pass. See `INCOMPLETE.md` for the content-spec scorecard.
