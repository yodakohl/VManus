# GDT858 — primary held-face versus physical-leaf audit

**PRIMARY_FACE_HOLDOUT_RETAINS_OPPOSITE_LEAF_FACE.** All 963 registered GDT808
primary folds reconstruct exactly: published train/test counts and both
exclusion flags match, with no coverage or metadata mismatch. Training retains
opposite-face events from the held physical leaf in 855 folds.

| Primary model | Audited folds | Opposite-face train retained | None retained |
|---|---:|---:|---:|
| M01_L_TO_L | 569 | 505 | 64 |
| M02_DY_TO_DY | 394 | 350 | 44 |
| Total | 963 | 855 | 108 |

The guarded event projection contains all 1,777 source events, on 175 actual
selectors, 169 faces and 90 physical leaves; 79 leaves have both faces
represented. The allowance was 179 selectors. This audits the two registered
CORE13 models, **not all 4,538 folds or GDT809's actual folds**.

Two deterministic examples from the complete witness collection:

| Model / held carrier / held face | Held test event | Retained training event | Reconstructed train/test | Opposite-face train count |
|---|---|---|---:|---:|
| M01 / ch / f100r | G808-E1498: L, ch, f100r | G808-E1506: L, qok, f100v | 636 / 3 | 4 |
| M02 / ch / f102v | G808-E1538: DY, ch, f102v1 | G808-E1523: DY, cth, f102r1 | 603 / 1 | 2 |

Both examples satisfy carrier exclusion and the published face exclusion;
the two events nevertheless occupy opposite faces of the same physical leaf.
The label `physical_folio_excluded=1` therefore establishes exclusion of the
face-valued field, not whole-leaf exclusion. This matches the static code's
`physical_folio()` normalization. It does not establish a performance penalty,
change any old result, or quantify what refitting with whole-leaf exclusion
would do. No outcome, prediction, score, text or image was accessed.

`artifacts/PRIMARY_FOLDS.json` contains every primary fold, including zeros,
all retained opposite-face event IDs and a direct metadata witness pair per
affected fold. `RESULT.json` contains complete selector/face/leaf inventories
and all coverage diagnostics. `PROJECTED_METADATA.json` and `GUARD.json`
preserve the two exact guarded projections and provenance. The independent
set-based validator repeated both guarded queries, verified byte projection
parity, reconstructed all folds and checked all 855 witness pairs. Validation
PASS; cached runner replay byte-identical; pre-data controls PASS. Legacy
GDT808/GDT809 sources remain byte-identical under the preregistration lock.

Public preregistration: 6e3c7a93, pushed 07:24:38 UTC on 2026-09-06. Data run,
independent validation and replay completed by 07:25:20 UTC. Preparation began
07:12:15 UTC; the source result and handoff fit the 07:27:15 UTC total budget.
This is a validation-unit correction, not decipherment progress.
