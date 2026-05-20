# iter_01_roadmap.md — Foundational stage design (f1-f5)

stages=5; Q_annot=334; new_kcs=15; regen=0
fails={obj:0,kc:0,diff:0,stage:0,citation:0,misconception:0,metacog:0}
hallu_drops=0
distinct_surnames_cum=5
DAG_valid: true
sources:
  - Hermans 2021
  - Du Boulay 1986
  - Soloway 1984
  - Anderson 2001
  - Mager 1962

## Stages built this iter
- f1 (Reading code: literal trace, 27 Qs, gate 80%)
- f2 (Common runtime errors, 5 Qs, gate 80%)
- f3 (Idiomatic syntax & style, 86 Qs, gate 80%)
- f4 (Off-by-one and boundary edges, 82 Qs, gate 80%)
- f5 (Truthy/falsy & comparison pitfalls, 134 Qs, gate 80%)

## New KCs this iter
`read_control_flow`, `read_data_flow`, `read_io`, `null_undefined`, `index_out_of_range`, `type_mismatch`, `lang_idiom`, `naming_convention`, `redundant_construct`, `off_by_one`, `empty_collection`, `boundary_value`, `truthy_falsy`, `equality_semantics`, `short_circuit`

## Notes
5 foundational stages with diff_band -3.0..0.5 covering code-reading, runtime errors, idioms, boundaries, truthy/falsy. Prereq chain linear within level.

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
- Reused first-author before 20 unique: NONE — registry tracks distinct surnames; cum at this iter = 5.
