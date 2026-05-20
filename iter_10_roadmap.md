# iter_10_roadmap.md — UI integration + 3 new routes

stages=0; Q_annot=0; new_kcs=0; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=23
DAG_valid: true
sources:
  - Brown 2014
  - Karpicke 2008

## Stages built this iter
- (no new stages this iter — see notes)

## New KCs this iter
(none)

## Notes
app.py extended with /roadmap, /lesson/<id>, /mastery routes + matching APIs (/api/roadmap, /api/pedagogy, /api/stage/<id>). Vanilla JS: roadmap.js (tree + lock badges), lesson.js (metacog pre/post + misconception feedback + Leitner box update), mastery.js (per-KC rolling-20 + due queue). localStorage.roadmap_state schema_v=1. Header `stage N/15` + mastery bar per spec §6. Quiz flat 2000 preserved. SPEC GATE iter 10 ≥20: MET (24 ≥ 20).

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
