# GDT1193 — a reversible artificial writer passes the basic screen

**Result: FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS.** A single fixed table writes all four complete projected source collections and passes all ten inherited basic conditions against each of the three cached Voynich reader summaries. It also passes the stricter edit-one tolerance ±.01 declared before this construction. This is a fitted artificial control system, not a Voynich translation or a convincing historical reconstruction.

## What changed and what was tested

The failed GDT1191 H2048 writer's glyph map, greedy source segmentation, six-state counter, three public initial styles, source-word ending flags and recipe resets remain fixed. GDT1192 excluded every single pair exchange by necessary length conditions. This experiment exchanges the whole codes of exactly three source dictionary entries in one closed cycle. It does not repair the old reports retrospectively.

The pre-output contract capped affected occurrences at 2,048 across four 8,000-group samples. Exact interval queries covered 1,094,627,348 possible distinct-length oriented triples before that cap/filter; this is a mathematical candidate-space count, not a count of independently tested models. There were 358 qualifying actual cycles. The first in the predeclared affected-count order passed the full screen, so no further complete test was needed. It changes 244 sample occurrences. Source entry IDs 1412,1252,1026 (literal source fragments `pph`, `n`, `j`) take the reverse cycle. These are source-table entries, never native Voynich glosses.

All 1,054 complete projected recipes (80,931 source words) in b4,w1,bs1,gr1 encode and decode exactly. Statistics use the first 8,000 printed groups per book, with existing physical line wrapping. ZL3b, IT2a and RF1b are three alternate readings of the same manuscript; all four sources and target summaries were already exposed. Joint fitting on them is not independent transfer or confirmation. The frozen criteria are engineering tolerances, not a statistical significance test.

| Measure | b4 | w1 | bs1 | gr1 |
|---|---:|---:|---:|---:|
| Mean group length | 5.42275 | 5.50413 | 5.48963 | 5.50038 |
| Distinct types / groups | .30813 | .32025 | .28788 | .28175 |
| Top ten type share | .12875 | .13063 | .09438 | .12350 |
| Adjacent edit-one rate | .03845 | .03311 | .03247 | .03320 |
| All ten conditions × all three readers | PASS | PASS | PASS | PASS |
| Additional edit-one ±.01 × all readers | PASS | PASS | PASS | PASS |

See `artifacts/SCREEN.tsv` for every difference and limit, and `RESULT.json` for all counts and metrics. Several conditions are close to the allowed boundary: worst mean uses 99.84% of its tolerance, length-TV 99.81%, glyph-JS 98.99%. Passing is not an exact statistical replica. Sample glyph inventories contain 22,19,22,18 distinct glyphs respectively, all from the same offered 22-glyph working alphabet.

## Critical limits already visible

The cached metrics include features outside the ten-condition selection screen. A post-fit descriptive audit finds clear mismatches:

| Extra feature | Cached native summaries | Fixed artificial writer |
|---|---:|---:|
| o immediately after a nonfinal q | 97.75–98.11% | 25.66–30.35% |
| Groups ending in y | 37.05–41.51% | 19.50–25.06% |
| Marginal glyph entropy, bits | 3.858–3.873 | 3.095–3.180 |

These diagnostics were not retroactively added to the registered decision and were not used to refit this table. They preserve the basic-screen pass while preventing adoption as a satisfactory Voynich word-formation model. Matching the coarse filter demonstrably leaves important known constraints unresolved. No manuscript discovery follows from re-reporting these cached values. Source-word meaning is supplied by an openly invented cipher table, not recovered from manuscript context.

The procedure can be stated as longest source-fragment lookup, an initial shifted by a counter from 0 to 5, and an ending that marks source-word continuation or completion. **The dictionary has 2,130 entries.** Its learned assignment is part of the model cost. Small execution rules do not make that table small or historically attested. No error recovery, medieval speed or memorability claim is made.

## Validation and reproduction

The pre-output lock binds the contract, interval method, programs, baseline and inherited source/target dependencies. Before outcomes, 84,000 exhaustive small integer interval cases and range-query fixtures passed. After outcomes, all 358 retained cycles were checked by literal per-position length reconstruction (1,432 book checks); enumeration and the tested complete decision were replayed. The selected four full books were then checked with frozen GDT1174 metrics and all 1,054 public inverse/rewrite checks. `artifacts/VALIDATION.json` records this source/software consistency pass separately from the scientific scope.

Run from the repository root:

```bash
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1193_three_source_code_cycle/src/run.py
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1193_three_source_code_cycle/src/validate.py
python3 experiments/yolo/gdt1193_three_source_code_cycle/src/summarize.py
```

`PUBLIC_TABLE.json`, the four complete encoded text files and `MANUAL_INVERSE.tsv` make the construction inspectable. The manual packet is a post-result teaching illustration, not a source holdout or selection test. The blinded assistant recovered both fixed eight-group samples exactly: 16 groups and 15 source words. Root verified every recorded counter/rank/tail/fragment step against the source. No unprovided decoding rule was needed. Electronic exact-row search and supplied glyph segmentation assisted the read; this was not a paper-table or human-participant trial. See `MANUAL_READER.md` and `MANUAL_VALIDATION.json`. Source projection/provenance and exclusions remain those of GDT1177; recipes are complete under that editorial projection, not newly collated diplomatic transcriptions.

## Decision

Retain this as a working artificial source-control writer and a counterexample to treating the ten basic conditions as sufficient. Freeze its parameters and positive result. Do not call it the manuscript's system, reuse its arbitrary values as lexical evidence, or continue tuning this table solely to improve its already passed score. A next reconstruction must confront the known word-formation constraints and table cost explicitly, with a genuinely different fixed falsifier and prior-route review. GDT1191 and GDT1192 retain their original failures. No native word assigned; no raw/reserved target access. This construction is a local checkpoint under the existing 4 October exception, not a publication claim.

Scientific selection, frozen-metric/source validation and blind-reader comparison finished by 08:17 UTC, about 13 minutes into the 08:04–08:24 preparation/implementation/validation/local-closure budget. Local registry closure follows within the same block; no further research run. No commit/push was performed.
