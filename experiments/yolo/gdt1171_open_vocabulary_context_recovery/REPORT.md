# GDT1171 — open vocabulary recovers new spellings; context adds no useful gain

**Registered decision: NO_USEFUL_OPEN_CONTEXT_RECOVERY.** With the true source
sign values supplied, the fixed character model reconstructs many complete
words absent from its other-book reference vocabulary. However, crossing word
boundaries does not improve the registered primary endpoint over the reset
model or the shuffled-order control. Three of four practical gates fail.
No Voynich input, unknown-key recovery or translated word is involved.

Preregistration `facf6275f7fe70a9ad8a22789c4063529115c2c0` was public before any
real count-model fitting or decoding. All three arms and six folds were run
once, with no model, source, threshold, spelling or candidate repair. Every
prediction was locked before the answer scorer ran. Existing source exposure
is retained; this is procedural input separation, not analyst blindness.

## Main result

Primary weights each novel written type equally within its held book, then
weights the six books equally. It covers2,558 types/5,359 occurrences. U resets
character history at each word, C carries it across spaces, S carries it but
learns from shuffled reference-word order. All use the same legal output
relation, including strings absent from the reference vocabulary.

| Fixed arm | Primary exact words | Novel OOV type accuracy |
| --- | ---: | ---: |
| U, no cross-word history |59.277%|51.973%|
| C, original cross-word history |58.910%|52.568%|
| S, shuffled reference-word order |59.156%|52.171%|

The OOV column uses the same type-then-book weighting but only novel written
forms whose exact answers are absent from their reference. Its complete scope
is1,731 book/form types and2,363 occurrences. These are reconstructed source
spellings, not recovered meanings of previously unknown signs.

| Registered gate | Actual | Decision |
| --- | --- | --- |
| C primary>=70% |58.910%|FAIL|
| C-U>=3points; C>U in>=4books |−0.367points;3/6books|FAIL|
| C-S>=2points; C>S in>=4books |−0.246points;3/6books|FAIL|
| C novel-OOV>=50% |52.568%|PASS|

| Held source | Novel occurrences | Novel types | U | C | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| B4 |469|299|61.689%|63.093%|61.736%|
| B6 |48|42|16.667%|19.048%|16.667%|
| Br1 |105|81|69.136%|64.506%|68.724%|
| Bs1 |1,144|491|75.067%|73.611%|75.637%|
| Gr1 |2,372|1,086|66.868%|66.122%|66.701%|
| W1 |1,221|559|66.234%|67.080%|65.472%|

B6's poor result is retained with its predeclared equal book weight. Neither
dropping that book nor promoting U after the outcome is a successful C result.

## Complete accounting and qualified positive

All98,720 source groups receive a prediction under each arm, with unknown
groups receiving explicit nulls. All11,724 selected groups remain, including
204 unresolved obligations. U/C/S exactly recover9,634/9,560/9,428 selected
occurrences; their respective overall whole-record counts are294/273/264
out of1,173. Ordinary largely literal groups dominate overall text accuracy;
it is not the registered hard-case endpoint. No empty output was selected
among the11,724 selected groups, and all204 unresolveds remain null/error.

On novel occurrences, U/C/S recover4,023/3,978/3,868 out of5,359
(75.070%/74.230%/72.178%). Equal-type pooling across books gives
66.945%/66.590%/66.810%; these alternate weightings do not replace the primary.
C repairs165 of U's novel-occurrence errors and spoils210 correct U answers.
This descriptive cross-tab accounts for the net45-word loss; it is not a
separate selected test or significance claim.

C correctly recovers1,376 of2,363 reference-absent novel occurrences; U recovers
1,398 and S1,373. Thus the earlier55.906% reference-word intersection ceiling
is NOT an intrinsic limit of the complete declaration relation. The former
census correctly bounded its restricted vocabulary design. This distinct
open-output test can exceed that occurrence ceiling, with the source alphabet
and output values still supplied. Success on those strings does not establish
that all exact historical spelling choices are inferable.

## Decision and remaining scope

Stop this fixed contextual instrument. Do not enlarge its order, smooth it
again, switch to a neural model, add a reference corpus or hide the key as an
automatic next stage. Its useful positive is open-vocabulary conditional
source reconstruction; the proposed contextual advantage is not supported.
GDT1160's supervised context positive, GDT832's original failure, GDT833's
orthography result and GDT1164/1166's failures keep their original scopes.

This result does not refute longer-range syntax, other languages, abbreviation
as a historical practice or every possible contextual decoder. The chosen
order5 model sees only four preceding characters. It can let endings affect
the following word, but cannot implement general clause grammar. One shuffled
reference is a fixed diagnostic, not a calibrated null distribution. Related
books, editorial restorations and known sign values remain strong assumptions.
No target-writing mechanism or Voynich candidate interpretation was selected;
confirmed Voynich words remain0. A later proposal needs a genuinely different
identifying constraint and decision, not another unmotivated model variant.

## Validation and reproduction

All22 preregistered synthetic checks passed, including exact decoding against
exhaustive enumeration, empty emissions, duplicate derivations, normalization
and deterministic repetition. The separate validator recomputes all18 count
models and all296,160 group predictions, using its own count builder,
likelihood evaluator and Viterbi replay. It verifies all score paths, anchored
regex rule membership, source-to-prepared projection, split exclusion,
all98,720 scored rows, every metric and the original four decision gates.
Maximum live DP states were276, far below the fixed100,000-state limit;
no beam, candidate cutoff or resource fallback was used.

The validator imports shared I/O and the pinned source projector, not the
production model/decoder in its full run. Projector replay does not constitute
independent native-image collation. No manuscript image or reserve was opened.
Hashes and public commit are in PREREG_LOCK and PREDICTION_LOCK; complete
per-book predictions and SCORED_ROWS are compressed, not discarded. RESULT
and VALIDATION provide compact exact accounting. Reproduction commands and
CoReMA attribution/license are in README.md. Frozen code refuses a second run
over an existing prediction lock; use a preregistration checkout to repeat.

The bounded idea producer reviewed only design/predecessor evidence before
predictions, identified the word-bigram OOV limitation and supported including
the shuffle arm. Existing raw supply was sufficient; no quota idea was added.
That design review is not an independent performance replication.

Publication checks: the owned experiment's full scientific validation, live
context and registry freshness pass. The global repository check retains
pre-existing route-literal, historical manifest/hash, cached-layout and stale
index issues outside1171; no global PASS is claimed. The exact staged tree is
checked separately for1171 bindings, task scope and privacy, including decoded
gzip artifacts. Unrelated local work and every legacy source byte are preserved.
