# GDT606 method

## Question

Can the stable GDT605 98-unit stream support a historically scaled mixture of
letter homophones, doubles, two-/three-letter signs, nulls and a small
whole-word nomenclator, and do any concrete held readings retain the same
source carriers across restarts?

## Inputs

The target is rematerialized only through `vmanus-exp query-tsv` with all 180
GDT327 page selectors explicitly allowed and `f84` forbidden before row
materialization. The guarded target contains 4,165 lines on 91 physical folios.
GDT605's unchanged split supplies 68 train and 23 held folios. Its 64 train-only
collapsed-glyph merges yield 98 train units, 97 held units and no held-only
unit. Certain spaces and drawing interruptions remain hard chunk boundaries;
uncertain separators are joined before segmentation.

Pinned public Caesar Latin, Dante Old Italian and five MHG4SNA texts provide
reference character models and candidate strings. They contribute no target
alignment or key.

## Decoder

Three category grids are tested: 42/4/34/7/11, 36/4/40/7/11 and
46/4/30/7/11 for letter/double/syllable/null/whole-word signs. Letter outputs
allow at most six homophones; other non-null outputs are unique inside a key.
Train chunks are scored by a character four-gram, modest lexicon support,
overlength cost and structural category priors. Simulated annealing changes
both category and output. Six primary real starts, four matched
within-word-order-destroyed starts and six capacity-sensitivity starts are run
for each of three languages, yielding 48 complete keys and all six-start held
decodes.

All unordered unit collections are sorted before seeded randomization. This
corrects an early process-hash-order error and makes repeated full executions
byte-identical.

## Carrier audit and interpretation

Restart agreement is measured by category and exact output, both by type and
held occurrence weight. A candidate word must recur from the same source-unit
span, not merely at the same chunk position. Common substrings of different
whole-word outputs are retained separately as prefix-family leads.

The experiment may identify robust output categories and reject this exact
decoder as a reading. It cannot turn a category into a word, sound or meaning
without stable carrier-aligned outputs.
