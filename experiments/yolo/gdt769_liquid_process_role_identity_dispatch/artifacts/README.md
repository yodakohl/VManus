# GDT769 artifacts

Status: `PASS`. All 17 declared runner outputs are present; 26,743 independent checks and byte-identical replay of all 17 outputs pass. The decisions in the parent [REPORT.md](../REPORT.md) remain replaceable working interpretations, not confirmed translations.

The runner declares the following compact reproducible output set:

## Target and control atlases

- `TARGET_640_RAW_OCCURRENCE_ATLAS.tsv` — raw admitted target occurrences before exact-reader restriction.
- `TARGET_526_EXACT_CONTEXT_ATLAS.tsv` — reader-exact target contexts used by the dispatch.
- `TARGET_5_CENSUS.tsv` — census for `ol`, `ckhy`, `pcheey`, `ols`, and `otar`.
- `TARGET_5_ROLE_GEOMETRY.tsv` — positional and local role geometry for each target.
- `SIGNATURE_5_SUMMARY.tsv` — compact signature counts by target.
- `SUPPORT_52_LOCUS_ATLAS.tsv` — admitted support-locus evidence.
- `LEAVE_ONE_LOCUS_OUT.tsv` — strongest-locus and leave-one-locus-out stability checks.
- `CONTROL_SPAN_ATLAS.tsv` — matched control spans.
- `DONOR_BLOCK_REGISTRY.tsv` — blocked target/family donors and provenance controls.

## Role and identity dispatch

- `FRAME_16X5_EVIDENCE.tsv` — F01–F16 evidence for five targets.
- `FRAME_LOCUS_EVIDENCE.tsv` — occurrence-level frame evidence needed for conjunction checks.
- `ROLE_5X5_SCOREBOARD.tsv` — R01–R05 role results.
- `IDENTITY_CANDIDATE_SCOREBOARD.tsv` — identity candidates scored only after their role gate.
- `GDT769_5_WORKING_DICTIONARY.tsv` — replaceable target defaults, rivals, evidence, and confidence.

## Reader and result

- `TWELVE_COMPLETE_LINE_READER.tsv` — all 109 tokens in the twelve specified complete lines, with exactness and replacement fields.
- `HISTORICAL_ROLE_IDENTITY_READER.md` — human-readable dispatch plus architecture-only historical comparison.
- `RESULT.json` — machine-readable result, claim ceiling, counters, and status.

Two interpretation rules are mandatory when reading these outputs. First, R03 product evidence is valid only when its amount/value axis and result/endpoint axis occur around the same exact target occurrence and recur after strongest-locus ablation. Second, F14 medial two-sided geometry contributes no R05 support by itself; it must coincide locally with F15 or F16 and meet the page and ablation thresholds.

The selected-role column is not automatically an evidence victory. `ol` has equally passing R05, R01, and R03 roles; `ols` has equally passing R04 and R01; and `otar` has equally passing R05 and R01. Their displayed roles are selected by `SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES`. Only `pcheey` has one uniquely passing role; `ckhy` remains open. Accordingly, `ol` and `otar` carry `C1_LOCAL_FRAME__C0_ROLE_TIEBREAK`, and `ols` keeps only the replaceable `Maß-/Produktposten` default.

The twelve-line reader includes two explicit leak repairs: `sain=zwei Drachmen` is a fused-value working default with C0 unit identity, while `chekar=Zwischenzubereitung` is a forced local C0 placeholder after source-composed heat/dry/fraction semantics were quarantined.

Historical rows contribute architectural predictions only. They provide no EVA-to-Latin identity, no substring meaning, and no confirmed translation. Large exhaustive tables require an explicit retention justification before publication.
