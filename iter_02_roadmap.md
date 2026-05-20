# iter_02_roadmap.md — Intermediate stage design (i1-i5)

stages=5; Q_annot=521; new_kcs=18; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=10
DAG_valid: true
sources:
  - Sweller 1988
  - Flanagan 2020
  - OWASP 2021
  - Klabnik 2023
  - Schwartz 2008

## Stages built this iter
- i1 (Mutability & reference semantics, 153 Qs, gate 85%)
- i2 (Performance: complexity & hot paths, 63 Qs, gate 85%)
- i3 (Resource & lifetime management, 24 Qs, gate 85%)
- i4 (Input validation & injection, 121 Qs, gate 85%)
- i5 (Error handling & retry semantics, 160 Qs, gate 85%)

## New KCs this iter
`aliasing`, `shallow_vs_deep`, `unintended_mutation`, `big_o_recognition`, `quadratic_inside_loop`, `memo_opportunity`, `wasted_alloc`, `close_handle`, `ownership_borrow`, `drop_order`, `raii`, `sql_injection`, `xss_sink`, `unvalidated_input`, `path_traversal`, `swallowed_exception`, `wrong_exception_type`, `retry_idempotency`

## Notes
5 intermediate stages covering aliasing/mutability, complexity, resource lifetime, injection, error handling. diff_band -1.0..2.5.

## §7 budget accounting (this iter)
- fan-outs used this iter: 0 (heuristic + curated; no Agent fan-out)
- cumulative fan-outs (this /goal): 0
- §7 cap ≤24: COMPLIANT for this /goal scope
- (Prior /goal '/build 2000 MCQs' used 36 fan-outs and is documented separately in INCOMPLETE.md as terminated state.)

## §9 forbidden-list compliance
- Fabricated citations: NONE — all 24 refs in pedagogy_refs.json are real published works or standards.
- Unanchored Qs: NONE — every Q has stage_id + kc_tag.
- Non-SMART objectives: NONE — regex 1141/1141.
- Prereq cycles: NONE — DAG verified acyclic.
- "SM-2" mislabel: AVOIDED — labeled as `spaced_review[5]` (Leitner 5-box), not adaptive SM-2.
- False IRT/Rasch: AVOIDED — `calibration_method="content_heuristic"`.
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 10.
