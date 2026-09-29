# GDT1091 — blind cup contrast: one target, two controls

**Registered decision: `PARTIAL_ONE_TARGET`.** Both independent readers saw
the strict dark-blue fringed cup on f22r and f26v, but both marked the other
exact-`ofchy` target f39v `NO`. They also marked two of four metadata-matched
controls `YES` (f33v, f40v). Thus the proposed f22r cup-to-`ofchy` mapping
fails its fixed cross-page differential. The two `schor`-only references were
both `NO` for the strict cup, but that does not repair the failed target and
control conditions.

## Frozen process and complete observations

The [preregistration](PREREGISTRATION.md), nine-page roster, image-access note,
rubric, map SHA-256 commitment and executable decision rule were pushed before
the five new image pixels were downloaded. Two independent readers saw only
random B01–B09 images and wrote separate tables without folio identities,
target/control roles, transcription or each other's codes. Their files were
frozen before release of [the map](src/BLIND_MAP.tsv): A SHA-256
`d665ca472c45d858dccb17d899d1f94e38d6be9acf6786378fd9d7a28b0a4665`;
B SHA-256
`83b2c6c72f468c3247a188ecc18f55a6d8472058e4e0b1da0a011598f9d2cba9`.
The committed map hash matched. Root had prior text/image exposure, so the
blindness is limited to these two new image readers; this is not an
independent confirmation set. Official Yale image provenance and hashes are
in [SOURCE.tsv](src/SOURCE.tsv); image binaries are not republished.

The following are **A/B consensus** cells. `Y` means both YES, `N` both NO,
and `D` reader disagreement. The [joined table](artifacts/JOINED.tsv) preserves
both individual codes; the [reader tables](artifacts/BLIND_A.tsv) and
[B](artifacts/BLIND_B.tsv) include the original visual notes.

| Folio | Fixed role | Strict blue fringed cup | Any open cup | Multi-unit spike | Spiny round head |
|---|---|:---:|:---:|:---:|:---:|
| f22r | prior co-present reference | Y | Y | Y | N |
| f26v | `ofchy` target | Y | Y | N | N |
| f31r | matched control | N | N | N | N |
| f32r | `schor`-only reference | N | N | N | N |
| f33v | matched control | Y | Y | Y | Y |
| f39v | `ofchy` target | N | N | N | N |
| f40v | matched control | Y | Y | N | Y |
| f42v | `schor`-only reference | N | D | N | N |
| f43v | matched control | N | N | Y | N |

The primary rule required strict-cup YES on f22r **and both** `ofchy` targets,
at most one of four controls YES, and both `schor`-only references NO. Its target
condition fails at f39v; its control condition also fails at f33v/f40v. The
registered hierarchy returns `PARTIAL_ONE_TARGET` for one YES and one NO
target. All nine entries and four prespecified features are reported, including
the broad-cup disagreement at f42v. The broader `OPEN_CUP_TERMINAL` code does
not rescue f39v and also appears in the same two controls. f22r has a spike,
f26v has none, and f33v has both spike and cup, so these codes do not separate
two f22r organs into two textual owners.

This is a manuscript-image finding: the unusual-looking f22r cup form is not
specific to the exact-`ofchy` pages in this small matched set. It does not
prove that `ofchy` never denotes a flower, fruit, material or preparation: an
entry could mention an unpictured item. It does retire the direct visual
argument `ofchy≈f22r dark-blue fringed cups` on the registered evidence. No
botanical species name, p-value, word-to-organ pointer or translated word
follows. f84/f84r and reserves were not accessed.

Replay: `python3 experiments/yolo/gdt1091_ofchy_cup_spike_blind/src/run.py`
then `python3 experiments/yolo/gdt1091_ofchy_cup_spike_blind/src/validate.py`.
The validator passed for map commitment, reader/source rows, every joined cell
and the fixed decision.
