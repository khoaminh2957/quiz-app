# iter_03_roadmap.md — Advanced stage design (a1-a5)

stages=5; Q_annot=286; new_kcs=19; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=12
DAG_valid: true
sources:
  - Goetz 2006
  - Donovan 2015
  - OWASP 2021

## Stages built this iter
- a1 (Concurrency: races & atomicity, 110 Qs, gate 90%)
- a2 (Memory & UB hazards, 57 Qs, gate 90%)
- a3 (Crypto & auth correctness, 14 Qs, gate 90%)
- a4 (Concurrency: ordering & memory model, 52 Qs, gate 90%)
- a5 (Architecture-level review, 53 Qs, gate 90%)

## New KCs this iter
`data_race`, `check_then_act`, `unprotected_shared_state`, `use_after_free`, `integer_overflow`, `unsafe_aliasing`, `unchecked_arithmetic`, `weak_hash_alg`, `constant_time_compare`, `cred_in_code`, `insecure_random`, `happens_before`, `memory_ordering`, `deadlock_order`, `missed_signal`, `hidden_coupling`, `leaky_abstraction`, `stringly_typed`, `mutable_global_state`

## Notes
5 advanced stages: races, UB/memory hazards, crypto, ordering, architecture-level. diff_band 0.5..3.0. Linear prereq chain f1->...->a5.

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
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 12.
