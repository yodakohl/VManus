# GDT972 — unchanged R0 header contradicted throughout the literal panel

**Decision: ALL_LITERAL_R0_HEADERS_CONTRADICTED.** None of 561 eligible complete paragraphs satisfies all seven necessary header conditions of the frozen R0 writing rule. All 1,349 complete rows are accounted for, including 788 nonliteral rows that remain unknown. No full code, numeric values, arithmetic, semantic reading or translation was fitted.

## Registration and execution

The exact S0/R0 model and seven conditions are in [PREREGISTRATION.md](PREREGISTRATION.md). Local lock was made before the first header census. Registration commit `0eb1a2524` was publicly pushed and confirmed at 14:28:23 UTC on 15 September 2026. Primary execution started at 14:28:31 UTC and took 0.053 seconds. Preparation, contract review, validation and publication are part of the 14:09–14:35 inclusive budget; computation time alone is not the cost.

The source-only positive control GDT971 identified one decimal digit map under known roles, arithmetic and numeral boundaries. Its second alternative path added zero eliminations. GDT972 asks a different, manuscript-facing question: can any complete literal paragraph have even the necessary header of the unchanged variable-account renderer? It tests no fixed source values or source program length.

## Fixed predictions and observed outcomes

Every candidate must start with the complete 12-group header:

`GRADES A NUM(a) B NUM(b) C NUM(c) TARGET NUM(t) TOTAL NUM(m) FIRST`.

Seven named atomic groups must be distinct prefix-incomparable codes of length 1–8. The five numeral groups have length 2–32; the first four differ; all five have a common nonempty NUM code of length at most 8 that is shorter than each numeral and prefix-incomparable with all seven named codes. At least 14 total groups is a deliberately weak necessary lower bound, not a sufficiency claim. The screen does not parse numeric suffixes, compare number values, fit remaining atom codes or parse any body.

| Reading | Complete rows | Literal eligible | Physical leaves with literal rows | Nonliteral unknown | Header survivors |
|---|---:|---:|---:|---:|---:|
| IT2a | 690 | 529 | 78 | 161 | 0 |
| RF1b | 0 | 0 | 0 | 0 | 0 |
| ZL3b | 659 | 32 | 17 | 627 | 0 |

The alternative transcriptions describe one manuscript; their counts are not independent replications. RF1b supplies no complete paragraph fences in this bound intake.

| Fixed condition | ZL first failure | ZL all contradictions | IT first failure | IT all contradictions |
|---|---:|---:|---:|---:|
| MIN_GROUPS | 2 | 2 | 28 | 28 |
| ATOMIC_WIDTH | 7 | 7 | 135 | 137 |
| ATOMIC_DISTINCT | 2 | 2 | 39 | 45 |
| ATOMIC_PREFIX_FREE | 3 | 7 | 19 | 73 |
| NUMERIC_WIDTH | 1 | 1 | 6 | 15 |
| GRADE_DISTINCT | 1 | 2 | 15 | 20 |
| NUM_PREFIX_DOMAIN | 16 | 30 | 287 | 504 |

First-failure counts partition the eligible paragraphs in the registered order. All-contradiction columns overlap: each applicable condition is computed even if an earlier one fails. Where a literal paragraph has fewer than 12 groups, the remaining header conditions are unknown, while MIN_GROUPS is false. The 788 nonliteral rows have no header verdict and retain their original defect labels; no normalization rescues them.

The complete [candidate/prediction table](artifacts/CANDIDATE_PREDICTIONS.tsv) has one row per complete paragraph, including edition, paragraph ID, page, physical leaf, eligibility/defects, group count, actual first 12 groups, all seven predicted-condition outcomes, every NUM-prefix candidate, all contradictions, and decision. [PREDICTIONS.json](artifacts/PREDICTIONS.json) contains the same exhaustive records in structured form. No successful-looking individual passage was selected.

## Validation and implementation error disclosure

A separately written evaluator reconstructed every row and all panel aggregates, then compared the primary JSON and the exact complete TSV bytes: all 1,349 rows and all 12 comparison fields pass in [VALIDATION.json](artifacts/VALIDATION.json). It does not import the primary evaluator.

Before public registration, root corrected several implementation/schema discrepancies in that validator; these are described in [SOURCE_INDEPENDENT_REVIEW.md](SOURCE_INDEPENDENT_REVIEW.md). Its first full run then stopped because splitting full_text on spaces altered 15 nonliteral ZL group lists containing internal spaces. The corrected validator preserves cached line word lists and checks their joined text, as required by the unchanged primary/protocol. All 15 affected rows were already nonliteral and remain unknown. The primary predicate, output and frozen bindings were unchanged. This correction does not supply independent scientific confirmation.

## Exposure, ambiguity and confirmation capacity

Only the already exposed GDT970 complete-paragraph cache and its GDT915 scope were read. All 179 admitted selectors retain their existing restrictions. No new manuscript page or image was opened. f84/f84r and all other reserves remained closed; f116v was not admitted. The data are exploratory project-exposed material, even though the new test was prospectively registered.

There is no candidate-selection versus independent leaf-confirmation split: the full cache had been used earlier, and the present screen exhaustively tests it. Independent manuscript confirmation capacity is **zero**. The held physical-leaf field makes exposure traceable; it does not manufacture a holdout. No significance claim is made without a suitable whole-search control, and no plant/material/operation name is confirmed.

No eligible candidate remains ambiguous *within this necessary R0 screen*: all contradict at least one required condition. The 788 nonliteral records and missing RF paragraph capacity remain unresolved. Whole-form code families, different fixed renderers, other semantic subjects, source identity, language, units and physical interpretation remain outside the test. This is not a rejection of all arithmetic or mixture content.

## Consequence for the research route

Close this unchanged R0 complete-paragraph renderer in the current literal panel. Do not strip headers, alter NUM prefixes, relax code bounds, reinterpret paragraph boundaries or change predicates after this result. Another run needs genuinely changed admissible data or a separately declared, decision-changing model/falsifier.

R1 was completely drafted source-only and published with the registration before the R0 outcome. It packs atomic arguments into operator groups and specifies context pieces. It remains a raw, untested rival, not a repair or success of R0. R2 is a separate source-only proposal in preparation; neither inherits a positive target result. The numerical content kernel from GDT971 is retained with its conditional assumptions and free-label counterexample. Confirmed Voynich words remain **0**.

The global repository audit retains eight pre-existing failures in GDT600/GDT953. The exact selected staged tree is checked separately; no global-clean claim is made.
