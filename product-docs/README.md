# Product Docs — CodeReview Quiz

These documents were produced by a **20-round, 426-agent Product Evolution Harness**
(`../harness/product_evolution_harness.js`) that turned the quiz-app idea into an
end-to-end, market-ready product plan grounded in **verified** web sources.

- **426 agents** · **920 verified findings** · **581 hallucination flags caught & removed** · ~2.9h
- Each round: 8 research agents (real WebSearch/WebFetch) → 8 verify agents (independent
  anti-hallucination) → 3 improve agents → 1 judge (P0/P1/P2) → 1 synth (cumulative state).

## Read in this order

1. **[HARNESS_REPORT.md](HARNESS_REPORT.md)** — the audit trail: per-round trajectory + the
   consolidated **64-item backlog** (27 P0 / 22 P1 / 15 P2). Start here.
2. **[PRODUCT_RESEARCH.md](PRODUCT_RESEARCH.md)** — cited market / competitor / pricing dossier.
3. **[PRODUCT_SPEC.md](PRODUCT_SPEC.md)** — end-to-end product spec (MVP → v1 → v2).
4. **[TECH_ARCHITECTURE.md](TECH_ARCHITECTURE.md)** — architecture to scale (DB, auth, payments, infra).
5. **[GTM_PLAN.md](GTM_PLAN.md)** — positioning, pricing, acquisition, retention, metrics.
6. **[ROADMAP.md](ROADMAP.md)** — phased execution plan.
7. **[RISKS_AND_VALIDATION.md](RISKS_AND_VALIDATION.md)** — risk register + anti-hallucination method.

## Evidence

- **[VERIFIED_SOURCES.md](VERIFIED_SOURCES.md)** — every verified finding with its source URL.
- **[HALLUCINATIONS_CAUGHT.md](HALLUCINATIONS_CAUGHT.md)** — claims/URLs the harness flagged & dropped.

## What shipped from this (Phase 0 — "Measure & Position")

The harness's top strategy was **measure-before-build**: instrument demand and protect
integrity before building Stripe/DB. Implemented in code (see repo root `app.py`, `static/`,
`templates/`):

| P0 (round) | Shipped |
|---|---|
| Answer-key leak (R06/09/11/16/17/18) | `/api/questions/public` (stripped) + server grading `/api/check` |
| Analytics (R01/R16) | cookieless `/api/event` + `static/analytics.js` |
| Waitlist (R01/R20) | `/api/waitlist` → `WAITLIST_WEBHOOK_URL` sink |
| Fake-door pricing (R01/R05) | `/pricing` 3 tiers + intent capture |
| Reposition (R02/R04) | landing hero "JUDGE code, not WRITE code" (real 286 count) |
| SEO (R14/R20) | `/q/<id>` SSR + `/sitemap.xml` + `/robots.txt` + OG/JSON-LD |
| Compliance (R17) | `/privacy` + `/terms`, rate-limit, sanitization, formula-injection defang |

The remaining P0s that need a database (OAuth + cloud sync R08, Stripe + tier column R10)
are specced in `TECH_ARCHITECTURE.md` / `ROADMAP.md` as Phase 1.
