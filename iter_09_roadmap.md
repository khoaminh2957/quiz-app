# iter_09_roadmap.md — Q annotation pass (1141 questions)

stages=0; Q_annot=1141; new_kcs=0; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=23
DAG_valid: true
sources:
  - (consolidation iter — refs reused from prior)

## Stages built this iter
- (no new stages this iter — see notes)

## New KCs this iter
(none)

## Notes
Atomic rewrite of questions.json with full annotation set {learning_objective,kc_tag,est_difficulty,calibration_method,stage_id,misconception_map,metacog_pre,metacog_post}. Stage rebalance pass ensures every stage has ≥5 Qs. Gate 3.x: 1141/1141 PASS (obj=0 fail, kc=0, diff=0, stage=0, misconception=0, metacog=0). hallu_drops=0 (no fabricated citations — all refs from registry).

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
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 23.
