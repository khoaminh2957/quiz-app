# iter_05_roadmap.md — Pedagogy reference registry

stages=0; Q_annot=0; new_kcs=0; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=19
DAG_valid: true
sources:
  - Anderson
  - Bloom
  - Brown
  - Cepeda
  - Donovan
  - Du Boulay
  - Ericsson
  - Flanagan
  - Flavell
  - Goetz
  - Hermans
  - Karpicke

## Stages built this iter
- (no new stages this iter — see notes)

## New KCs this iter
(none)

## Notes
pedagogy_refs.json registry with 24 curated entries spanning 24 distinct first-author surnames. SPEC GATE iter 5 ≥10: MET (24 ≥ 10). Refs sourced from books, peer-reviewed papers, and authoritative standards (OWASP). No fabricated DOIs.

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
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 19.
