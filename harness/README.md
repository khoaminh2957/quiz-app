# Product Evolution Harness

A reusable multi-agent harness that evolves a web-app idea into an end-to-end,
market-ready product plan — grounded in **verified** web sources, with explicit
**anti-hallucination** verification at every step.

## Run

```bash
# Full 20-round run (default):
#   invoked via the Workflow tool with scriptPath = product_evolution_harness.js
#
# Args (optional JSON):
#   { "startRound": 0, "endRound": 19,   # round range (0-based)
#     "fast": false,                      # fewer web searches per agent
#     "skipDocs": false,                  # skip final doc synthesis (for batching)
#     "priorState": "...",                # carry product state across batches
#     "priorVerified": [...], "priorHallu": [...] }
```

## Architecture (per round — 21 agents)

```
8 research agents   (real WebSearch/WebFetch, 8 lenses: market/competitor/
                     authoritative/user-pain/pricing/tech/pitfalls/trends)
        │  pipeline (per-lens, no barrier)
        ▼
8 verify agents     (independent anti-hallucination: is the URL real? does it
                     support the claim? → keep only verified, flag hallucinations)
        │  barrier (improve needs all verified findings)
        ▼
3 improve agents    (product / engineering / business lenses → concrete changes)
        ▼
1 judge agent       (accept/reject + P0/P1/P2 priority + round score)
        ▼
1 synth agent       (update cumulative product state → fed into next round)
```

After 20 rounds, **6 doc agents** synthesize the deliverables in `../product-docs/`.

## Output

- `output/full_result.json` — the complete machine-readable run result.
- `output/backlog.json` — the 64 accepted improvements (P0/P1/P2).
- `../product-docs/*.md` — the 6 product documents + evidence files.

## Engineering notes (lessons baked in)

- **Doc agents return plain text, not structured output** — large markdown via the
  StructuredOutput tool gets truncated → schema-mismatch retry loops. Plain final-message
  text sidesteps this.
- **Schemas are kept small** (verify dropped its nested `checked` array) — complex/large
  structured outputs have a high mismatch/retry rate.
- Concurrency is capped at `min(16, cores-2)`; 426 agents ran in ~2.9h on a 12-core box.
