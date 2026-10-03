# GDT1159 — unknown lexical assignment from source recipe graphs

Registered 2026-10-03 04:32 UTC, before extraction outcomes or fitting. Source-only fixed control. Total preparation/implementation/validation/publication budget60minutes; checkpoint05:32UTC, reassess expansion rather than alter gates. The active ten-hour block continues independently.

## Decision and predecessors

Can a finite graph alignment recover original unknown ingredient forms better than the identical-capacity marginal-only assignment? GDT343 supplies normalized identity and finds no extra flow retrieval value; here identity is unknown. GDT176 supplies annotated medieval culinary recipes, not a demonstrated Voynich ingredient segmentation. GDT385 parent-link calibration failed its original transfer gate. No existing failure is superseded. A positive retains co-occurrence alignment as a source-calibrated candidate mechanism; a negative stops this fixed small model. Neither permits a Voynich decoder or reserve access.

## Data and exposure

Use all six GDT176 cached CoReMA XMLs, exact hashes in gdt176_corema_collection_manifest.tsv: b4,b6,br1,bs1,gr1,w1. No reacquisition with changed bytes. Source texts are CC-BY-4.0, CoReMA, University of Graz; public URLs in that manifest. These sources and their labels have substantial prior project exposure. This is prospective algorithm separation, not fresh blind source discovery or six independent manuscript traditions. No Voynich data. f84 and f84r sealed, f116v unadmitted, all reserves closed.

Extract ingredient elements having a nonempty commodity identifier, no commodity-bearing descendant, and no nonempty ana attribute. Render concatenated itertext, NFC and outer-whitespace trim only; require exactly one whitespace-delimited token. Preserve case, punctuation, u/v, spelling, repetitions and polysemy. No concept-based merging of held forms. Retain excluded counts/reasons. Recipe identifiers and XML element ordinals bind original spans; rendering offsets optional audit metadata, not predictors. Use all recipes as presence denominators, including recipes with zero eligible spans. Oracle ingredient boundaries and oracle training normalization make this a favorable control, not raw-text decipherment.

Six leave-one-collection-out folds. Train candidate concepts are the four most prevalent Q identifiers by pooled training-recipe presence, ties by identifier. Held forms are the seven most prevalent eligible original surface forms by held-recipe presence, ties by UTF-8 byte order. Selection never consults held Q identities or English labels. Insufficient four/seven makes a fold NO_CAPACITY, not a replacement or smaller search. No title-based exclusion; report exact normalized-title overlap diagnostically if metadata supports it. Shared recipes/traditions limit independence. Training is recipe-pooled, not equally weighted by collection.

## Predictors and exhaustive assignment

Predictor receives training recipe-by-concept incidence for the four selected concepts and held recipe-by-opaque-form incidence for seven forms only. Held strings, concept labels, Q identities, role attributes and gold counts are not predictor inputs. Every mapping g from seven forms to OTHER or four named concept slots is enumerated:5^7=78,125, including many-to-one aliases, unused concepts and all OTHER. No optimization restarts, spelling similarity, embeddings or learned parser.

For each concept, OR the held recipe presence of all forms assigned to it; unassigned concepts have zero presence. OTHER contributes to neither term. Let pS(c),pS(c,d) be pooled train recipe incidence, pT(c),pT(c,d) the mapped held incidence. Marginal arm F minimizes mean_c[(pT(c)-pS(c))^2]. Graph arm G minimizes that same quantity plus mean_{c<d}[(pT(c,d)-pS(c,d))^2], fixed weight1. Raw pair incidence remains frequency-related; control comparisons, not the score itself, assess any increment. These discrepancies are not calibrated semantic probabilities.

Enumerate mapping digits deterministically with OTHER=0 and source concepts1..4 in selected order. All scores within absolute1e-12 of minimum are exact optima for reporting. Primary accuracy is uniform mean across all such optima, not gold-selected best optimum or arbitrary unique winner. Retain optimum IDs and per-form alternative labels. Also report a sensitivity envelope of loss <= minimum +0.01*(maximum-minimum), and all per-form label possibilities; this is not a confidence interval. Show a canonical lowest-ID optimum only as one example, never as uniqueness.

## External outcome

Gold remains the original commodity Q identifier for each held eligible occurrence. For each selected form, named accuracy is fraction of its occurrences whose Q equals the proposed named Q; OTHER scores zero even when correctly rejecting an out-of-inventory concept. Average across seven forms then six folds for primary named macro accuracy. Occurrence-weighted counterpart, explicit correct OTHER rejection, true-Q mixture, unselected-form coverage and oracle single-label named upper bound are separate diagnostics. Polysemy is retained and never resolved using predictions. Report every selected form and each contradictory occurrence count. No fold/word is dropped for OOV truth, bad scores or ambiguity.

## Whole-search controls

199 constructed null worlds per fold. Start each world from observed held binary recipe-by-seven-form matrix. Perform exactly100*N_recipe Curveball trades: uniformly choose two distinct rows; uniformly redistribute their symmetric-difference columns preserving both original row sizes; common columns remain. Use numpy default_rng seed1159000+1000*fold_index+world_index, folds above indexed0..5, worlds1..199. Row and column sums must remain exact. No adaptive extra mixing, resampling until a desired result, or null count expansion. Report unchanged worlds and incidence changes. Refit BOTH F and G exhaustively for every world: OR alias aggregation means preserved raw margins do not preserve every mapped concept marginal. Score each world's mappings against original held form gold, aggregate same-index world deltas across all six folds.

Report inclusive conditional control rank (1+number null aggregate deltas >= observed delta)/200. It describes this constructed complete-search control, not proven uniform mixing, an exact randomization p-value, population significance or independent confirmation. Original source gold and copied recipes remain limitations. Merely permuting concept names is not a valid control and is not used.

## Fixed continuation decision and validation

SUPPORTED_LIMITED_SOURCE_RECOVERY requires all six folds adequate, mean named macro G-F>=0.05, strictly positive G-F in at least four folds, and conditional control rank<=0.05. Otherwise NO_SUPPORTED_GRAPH_LEXICAL_INCREMENT, with NO_CAPACITY separate if necessary. Report positives even on failure. No weight, candidate number, token rule, source subset, null or gate repair after outcomes.

Independent validation checks source hashes, extraction and selection, exhaustive mapping count, scalar reconstruction of observed scores/optima, gold accounting, null row/column preservation, same-capacity refits, tie handling and gate arithmetic. A planted/small artificial sanity case may check arithmetic only; no post-result parameter tuning. GDT388 concerns separately owned Voynich inscription edges; this is source recipe co-occurrence and creates no target relation packet.

Assumptions retained: ingredient spans are given; concept inventories are restricted; each form gets one label per mapping, while aliases are allowed; polysemy cannot be perfectly recovered by this model; recipes need not share distributions; repeated textual traditions weaken independence. A pass does not establish comparable Voynich units, any target noun, language, historical source identity or word meaning.
