# iter_07_roadmap.md — Metacognitive prompts + Leitner schedule

stages=0; Q_annot=0; new_kcs=0; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=22
DAG_valid: true
sources:
  - Schraw 1998
  - Flavell 1979
  - Leitner 1972
  - Cepeda 2006

## Stages built this iter
- (no new stages this iter — see notes)

## New KCs this iter
(none)

## Notes
Per-Q metacog_pre + metacog_post by difficulty band. Stage-level metacog_prompt per Schraw 1998 metacognitive awareness framework. Spaced-review intervals 1/3/7/16/35 days (Leitner 5-box, NOT SM-2 — labeled correctly per spec §9). Cepeda 2006 confirms expanding intervals for retention.

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
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 22.
