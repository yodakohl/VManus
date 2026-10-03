# GDT1159 — exact unknown-word graph recovery does not pass

**NO_SUPPORTED_GRAPH_LEXICAL_INCREMENT.** The fixed co-occurrence model raises mean named-concept recovery from4.9603% to9.4848%, but fails every registered continuation condition. It does not support exporting any source concept to Voynich words.

## Actual recovery, all six folds

The [complete42-form table](CANDIDATE_TABLE.md) preserves every selected original form, true concept counts, marginal-only and graph predictions, and alternatives. Six cached readable culinary collections supply1,136 recipes. All78,125 many-to-one assignments, including OTHER, are considered in each fit. Editor-provided ingredient spans are given; word identities are hidden from the numeric fit.

|Held collection|Marginal-only named accuracy|Graph named accuracy|Difference|Graph exact optima|Graph1% envelope|
|---|---:|---:|---:|---:|---:|
|b4|0.000000|0.142857|+0.142857|1|61|
|b6|0.047619|0.142857|+0.095238|1|63|
|br1|0.035714|0.000000|-0.035714|1|137|
|bs1|0.000000|0.283372|+0.283372|1|129|
|gr1|0.000000|0.000000|0.000000|1|116|
|w1|0.214286|0.000000|-0.214286|1|56|

Accuracy first averages original gold occurrences within a form, then the seven forms within each held collection, then the six collections. It also averages all exact optimum mappings uniformly. OTHER never counts as a recovered named concept. Occurrence-weighted results and correct out-of-inventory rejection are separate in RESULT/GOLD artifacts.

The graph correctly recovers b4`smalcz` as lard, b6`eir` as chicken egg, and bs1`gewuercz` as spice. Its bs1`wein` assignment is wine for60of61 annotated occurrences; the other occurrence is annotated brandy and remains an exact-concept mismatch under the fixed criterion. These are readable-source recoveries, not newly discovered historical meanings. Counterexamples are extensive: b4`ayr` is assigned wine instead of chicken egg; b4`gewurcz` chicken egg instead of spice; w1 loses both marginal-only successes. None of the42 forms has one graph label throughout its registered1% score envelope. Unique exact minima therefore do not establish stable lexical identity.

## Complete-search controls and fixed decision

Each fold has199 Curveball worlds preserving original recipe-row and form-column totals. Both arms are fully refitted in every world, because alias aggregation can change mapped concept marginals even under fixed surface margins. Every fold produced199 distinct matrices and no unchanged world. The fixed schedule supplies a constructed conditional reference, not a proof of uniform mixing or population significance.

|Registered condition|Observed|Decision|
|---|---:|---|
|Mean named accuracy increment>=0.05|0.0452446006|fails|
|Strict improvement in>=4of6 folds|3of6|fails|
|Inclusive conditional whole-search rank<=0.05|29/200=0.145;28null deltas at least observed|fails|

All controls were completed despite the first two failures. No source, candidate inventory, score weight, tokenization, gate or null count was changed. The numerical inclusive comparison is checked with exact rational tie-averaged gold counts; fitted scores and mappings are unchanged.

## Scope, limitations and retained information

These original surface forms were not normalized into their hidden concepts. Several spellings can map to one concept; semantic polysemy remains in gold. The four training concepts are spice, chicken egg, lard and wine in five folds; gr1's training inventory contains saffron instead of wine. A true concept outside that inventory remains outside and is not silently substituted. The oracle single-label named ceiling varies from0.286 to0.712 across folds; it is a diagnostic, not a selection filter or revised denominator.

Selected forms cover1,772of8,600 eligible source occurrences. This is deliberately a small finite capacity control, not a model of the complete text. Oracle ingredient spans, restricted concept vocabulary, omitted forms and collection distribution differences were registered limitations. They do not excuse wrong assignments or authorize an after-result larger-inventory repair. The exact score minimum can prefer false assignments even with meaningful source relations available.

These are related culinary recipe collections. Exact normalized-title overlap involves250/271 b4 recipes and252/263 w1 recipes, versus17/34 b6,13/45 br1,84/269 bs1 and104/254 gr1. Such overlap is a diagnostic of possible shared content, not proof of recipe identity; collection holdout is not independent historical transmission. Prior project exposure and editor normalization are disclosed. GDT343's supplied-identity retrieval benefit and GDT385's failed parent-link contract remain unchanged.

The result stops this fixed source co-occurrence model. A different route requires a genuinely different justified relation or input, not extra optimization restarts, retuned graph weight or choosing the successful words. No Voynich target unit, grammar, noun, language or meaning is inferred. No reserved or sealed page was read.

## Reproduction and validation

Run `python3 experiments/yolo/gdt1159_corema_unknown_lexical_graph/src/run.py`, then the corresponding `src/validate.py`. The six source XML hashes and public URLs are in `src/SOURCE.json`; CoReMA, University of Graz, CC-BY-4.0. Existing GDT176 caches are required with exactly those bytes. METHOD/PREREGISTRATION hashes are frozen in REGISTRATION_LOCK before extraction outcomes and fitting.

PREDICTOR_INPUTS contains numeric incidence matrices only. GOLD and SOURCE_PROJECTION preserve source identities separately. OBSERVED and six NULL_FOLD artifacts preserve optimum bitmaps, ambiguity envelopes and each null matrix; MAPPING_SCHEMA decodes the complete assignment inventory. No optimizer convergence claim is needed. Independent validation passes17 groups: separate source extraction, all observed scores and all1,194 regenerated null matrices with both complete model fits, optimum/envelope sets and exact-rational gold accounting. Scalar spot checks use a different cost construction. Uniform null mixing and historical/Voynich meaning are not validated. The exact-rational correction leaves28 inclusive control exceedances and all decisions unchanged.
