# GDT168 — synthetic architecture calibration report

Status: **HOST_NEGATIVES_DO_NOT_DISTINGUISH_LEXICAL_FROM_DISTRIBUTED_CODE**.

## Ground truth

| system | true architecture | host information fraction | full tuple + slot information fraction | held-unit host decoder accuracy/coverage |
|---|---|---:|---:|---:|
| A | injective 2--3-character concept codebook | 1.000 | 1.000 | 1.000/0.516 |
| B | slot/wrapper/100-way host/right/closure mixed-radix code | 0.443 | 1.000 | 0.048/1.000 |

The encoders are exactly reversible by construction.  Held-unit decoders are
stricter empirical tests: they cannot decode representations absent from all
other source units.

## What the blind diagnostics recovered

| diagnostic | A | B | calibration verdict |
|---|---|---|---|
| GDT113_RECORD_CLOSURE | PERFECT | PERFECT | TRUE_POSITIVE_BOTH_NONDISCRIMINATING |
| GDT160_COMPATIBLE_PAIRING | density=0.016450 | density=0.185258 | POSITIVE_BOTH_BUT_STRONGLY_ENRICHED_FOR_DISTRIBUTED_CODE |
| GDT162_SHORT_HOST | SHORT_AND_RECURRENT | SHORT_AND_RECURRENT | NONDISCRIMINATING_BY_LENGTH_RECURRENCE |
| GDT162_HOST_TO_COMPILER | -0.611066 | -2.144632 | NEGATIVE_BOTH_FALSE_NEGATIVE_FOR_TRUE_CODEBOOK |
| GDT163_SAME_GROUP_SUBSTITUTION | +0.004493 | +0.111927 | CORRECTLY_LOCALIZES_DISTRIBUTED_COMPILER_COUPLING |
| GDT164_EXTERNAL_SUBSTITUTION | +0.000274 | -0.003385 | TRUE_NEGATIVE_BOTH |
| GDT165_NEXT_HOST | -0.384428 | -1.069926 | NEGATIVE_BOTH_FALSE_NEGATIVE_FOR_LEXICAL_CODEBOOK |
| GDT166_UNORDERED_CONTEXT | line=-0.474019 | line=-0.116159 | NEGATIVE_BOTH_AND_NONLEXICAL_WORLD_LOOKS_LESS_NEGATIVE |
| GDT167_RENDERER_ALIGNMENT | 1.000000 | 1.000000 | TRUE_RENDER_ALIGNMENT_BUT_FALSE_POSITIVE_IF_CALLED_LEXICAL |
| GDT113_TRUTH_RETRIEVAL | host_MI=1.000 | host_MI=0.443;full_MI=1.000 | UNBLIND_TRUTH_SEPARATES_WORLDS_WHERE_FORMAL_CONTEXT_TESTS_DO_NOT |


## Main finding

The negative exact-host results do **not** distinguish the two hypotheses.
The true lexical codebook loses every held compiler/external-context test,
while the nonlexical distributed host often looks less negative.  Conversely,
surface compatibility and perfect cross-register alignment are positive in
both systems and are stronger in the distributed notation on compatibility.

The one useful discriminator is endpoint localization: compiler-coupled
one-glyph substitution coherence appears in B (0.112)
but not A (0.004),
and disappears on the parser-independent external endpoint in both.  That is
exactly the pattern expected from distributed same-group coding rather than a
productive external lexical relation.

## Consequence for Voynich work

GDT162--167 negative host likelihoods may reject a *predictive opaque context
codebook at their tested resolution*, but they cannot reject a real sparse
lexical address whose compiler is independent of content.  GDT167 alignment
can establish re-rendering geometry but not lexicality.  To distinguish the
hypotheses, a future test needs an external content endpoint or recoverable
cross-record referent, not another host-to-neighbor likelihood.

No Voynich source table or image was used.  f84r was not accessed.
