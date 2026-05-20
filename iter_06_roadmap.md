# iter_06_roadmap.md — SMART objectives + misconception maps

stages=0; Q_annot=0; new_kcs=0; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=20
DAG_valid: true
sources:
  - Mager 1962
  - Anderson 2001
  - Pane 2001

## Stages built this iter
- (no new stages this iter — see notes)

## New KCs this iter
(none)

## Notes
Per-Q learning objective generator using verb taxonomy (Identify/Distinguish/Predict) + topic phrase + accuracy threshold. Regex `^[A-Z][a-z]+.*?(≥|by end of stage|within \d+\s*seconds?).*$`: 1141/1141 PASS. Misconception map keyed by distractor index using topic-specific cognitive-bias templates (Pane 2001 study of non-programmer misconceptions).

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
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 20.
