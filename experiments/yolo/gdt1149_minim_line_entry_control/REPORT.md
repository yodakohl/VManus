# GDT1149 — continuation-line constraint, no lexical assignment

The registered descriptive outcome is **MINIM_SPECIFIC_CONTINUATION_AVOIDANCE**. Bare `ain/aiin/aiiin` have zero starts even on physical continuation lines in complete multiline paragraphs. D forms do occur there; other a-initial forms supply exceptions to an absolute a-initial ban. This outcome name does **not** establish a statistically distinctive minim-specific mechanism: other a-initial words also strongly avoid this position. No meaning, silent d, shared lexical identity, or independent confirmation follows.

## Complete primary comparison

| Native reading | Continuation slots (all / pure) | Bare internal | Bare continuation | D internal | D continuation | Other-a internal | Other-a continuation |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | 3093 / 2979 | 564 | 0 | 739 | 182 | 1051 | 8 |
| IT2a | 3061 / 3054 | 511 | 0 | 759 | 175 | 1019 | 8 |

ZL has 665 complete paragraphs, IT 697; eligibility further excludes single-line paragraphs and single-group lines. Bare-bearing complete multiline paragraphs span 65/64 physical leaves; other-a continuation cases span 5/6. All predeclared capacity thresholds pass. Paragraph starts contain 0 bare, 0 other-a, and 2/3 D forms. RF lacks native paragraph flags, so has no primary paragraph comparison. RF all-P inventory has 591 bare forms, none first; this is diagnostic only. Editions are alternate readings of the same manuscript, not replicated independent samples.

| Exact form | ZL internal | ZL continuation | IT internal | IT continuation |
|---|---:|---:|---:|---:|
| ain | 100 | 0 | 82 | 0 |
| aiin | 422 | 0 | 389 | 0 |
| aiiin | 42 | 0 | 40 | 0 |
| dain | 145 | 44 | 143 | 42 |
| daiin | 579 | 136 | 604 | 131 |
| daiiin | 15 | 2 | 12 | 2 |

These are P-text counts in the primary scope, not all manuscript text kinds. All exact candidate/control forms, diagnostic scopes and paragraph-start counts appear in [CANDIDATES.tsv](artifacts/CANDIDATES.tsv), with full denominators in [RESULT.json](artifacts/RESULT.json).

## Every other-a continuation control

| Reading | Native locus | Exact group |
|---|---|---|
| ZL3b | f105v.24 | alcheey |
| ZL3b | f95r1.5 | atar |
| ZL3b | f95v2.3 | archytaiin |
| ZL3b | f46r.13 | ar |
| ZL3b | f48r.6 | alshey |
| ZL3b | f48v.3 | alchey |
| ZL3b | f86v3.14 | ar |
| ZL3b | f86v6.27 | alshdr |
| IT2a | f105v.24 | alcheey |
| IT2a | f85r2.20 | ar |
| IT2a | f95v2.3 | arcsy |
| IT2a | f46r.13 | arakaiin |
| IT2a | f48r.6 | alshey |
| IT2a | f48v.3 | alchey |
| IT2a | f86v3.14 | ar |
| IT2a | f86v6.27 | alshdr |

Reading differences are retained. These 16 reader events must not be treated as 16 independent manuscript observations. Uncertain groups stay in the native denominators and never shift subsequent groups to first position. All 7,467 target/control cases and all 552 first-position target/control source lines are retained in compressed JSON; source snapshots preserve all other full lines. No visual adjudication was performed.

## What changes, what remains open

The zero cannot be explained solely by paragraph-opening behavior: it extends to continuation lines. An absolute ban on all a-initial forms is contradicted in the scoped transcriptions. A strong but nonabsolute general a-initial tendency remains compatible; these fixed descriptive thresholds are not a significance test comparing rates. Physical continuation is not necessarily syntactic continuation. A left-dependent expression may attach across a line break; a nonbreaking written group and a line-initial variant are different hypotheses. Neither dependency nor bare/D correspondence was established here. High internal D counts retain the known counterexample to a d-only-at-line-start rule.

This adds a controlled continuation-line distinction to already known profile zeros, not a new discovery of those zeros. GDT1047 concerned necessary paragraph hosts; GDT1148's failed neighbour prediction remains unchanged. GDT318's s/q and GDT1073/1074's p/y constraints are different contrasts. No old gloss is imported. No basis to call aiin THREE or AND, or daiin WINTER. Frequency alone does not prove function-word status either.

A useful next hypothesis must jointly account for internal bare forms, internal D forms and continuation-entry D without inventing interchangeable meaning. Existing IDEA000002 already concerns wrap continuity; check that primary before any follow-up. No automatic allomorph decoder or repeated zero census is authorized by this outcome.

## Registration, exposure and reproduction

[PREREGISTRATION.md](PREREGISTRATION.md) and identical METHOD were hash-locked at 2026-10-02T19:12:00.236782+00:00 before this census. Existing project profiles already exposed the bare ain/aiin line-entry zeros; this is explicitly not a blind discovery. All six GDT915 snapshots cover the same 179 admitted selectors; no new images or source admissions. f84/f84r remain sealed, f116v unadmitted, reserves closed. Independent meaning-confirmation capacity is zero; no search-wide null or significance claim. The 25-minute implementation/validation/publication budget was a scope limit, not a threshold for accepting a result.

Run `python3 experiments/yolo/gdt1149_minim_line_entry_control/src/run.py`, then `python3 experiments/yolo/gdt1149_minim_line_entry_control/src/validate.py`. Independent reconstruction checks pins, registration, complete paragraph selection, native denominators, candidate rows, cases and the fixed decision; see [VALIDATION.json](artifacts/VALIDATION.json). Computational agreement validates accounting, not a linguistic interpretation. Confirmed translated words: **0**.
