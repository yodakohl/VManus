# GDT382 — methodology stress-test / Voynichification audit report

## Result

GDT382 gives a mixed but actionable calibration:

* `CURRENT_PIPELINE_VALIDATED_FOR_COMPOSITE_ENCODING`
* `JOINT_TUPLE_MAPPING_NOT_HOMOLOGOUS`
* `OVERCONTROL_DESTROYS_FUNCTION_SIGNAL`
* `UNIVERSAL_CROSS_DOMAIN_INVARIANCE_TOO_STRICT`

The following failure labels do **not** apply:

* `BOUND_FUNCTIONS_NOT_RECOVERABLE_BY_CURRENT_METHOD` — false; and
* `DISCOVERY_CORRECTION_UNDERPOWERED` — false on this powered panel.

The correct next action is therefore **repair the instrument before another
Voynich operator experiment**.  Earlier negative transfers are not erased,
but negatives that depended on exact joint-tuple homology, universal raw
coefficients, or aggressive residualization are now explicitly
instrument-limited.

## What was tested

The oracle-blind encoder transformed 133,183 elements in 3,235 records from
five independent readable domains into composite states:

`HOST × WRAPPER × POSITION × BOUNDARY × RECORD × RENDERER`.

The encoder was committed publicly before the hidden oracle was evaluated.
No source word, POS, parse label, semantic label, or function label entered the
base observation layer.  The scorer then evaluated six hidden functional
classes over six representation levels, two transfer regimes, eight
overcontrol axes, and seven deliberately marked free/bound positive controls.

## Representation ablation

Held-collection, domain-local recovery separates the units sharply:

| representation | mean macro AUC over six functions | summed held gain (bits) |
|---|---:|---:|
| source-token equality (opaque) | 0.9302 | +93,522.9 |
| fresh domain-local opaque ID | 0.9302 | +93,522.9 |
| host identity | 0.8992 | +101,181.4 |
| complete rendered group | 0.8208 | +37,477.2 |
| exact composite joint state | 0.7160 | -11,188.5 |
| exact field/construction span | 0.4692 | -141,932.4 |

Source-token equality and its fresh opaque rehash are numerically identical,
as they must be: opacity alone destroys no equality information.  Entangling a
stable identity with occurrence-specific wrapper, position, record, and
renderer state does.  Exact composite state is not the best representation for
any of the six hidden functions.  It has positive codelength gain for only two
classes and negative total gain for four.

All six endpoints are nevertheless recoverable from at least one level:

| hidden positive-control class | best frozen level | macro AUC | held gain bits |
|---|---|---:|---:|
| FUNCTION_WORD | source-token equality | 0.9810 | +45,013.1 |
| ALTERNATIVE_OR | source-token equality | 0.9488 | +3,819.9 |
| POLARITY_EXCLUSION | source-token equality | 0.8723 | +1,597.3 |
| UNTIL_STATE_GATE | source-token equality | 0.9138 | +788.7 |
| COORDINATOR | host identity | 0.9975 | +34,805.0 |
| REF_ANAPHORA | source-token equality | 0.8693 | +12,788.1 |

Thus the observation boundary can preserve genuine function, while the
specific assumption `readable word ≈ exact composite joint tuple` is not
homologous in this known-positive world.

## Domain-local versus universal transfer

For every endpoint, the best domain-local AUC exceeds the best strict
held-domain universal AUC by more than 0.24 (range 0.243–0.478).  Every best
universal model has negative held codelength gain.  This directly validates the
hierarchical alternative: corpora can share a latent functional role while
using different opaque inventories, coefficients, and prevalence.  Requiring
one universal feature scale is too strict for this positive control.

## Free versus bound realization

All 42 endpoint×realization domain-local controls exceed AUC 0.80 (minimum
0.9975), and all have positive codelength gain.  The seven realization types
are free marker, prefix, suffix, wrapper alternation, boundary choice,
positional alternation, and zero/suppletive construction.  The universal
structural detector also recovers all 42 because the generic placement of the
domain-local marker remains visible.

This is a ceiling test deliberately encoded from oracle truth, not evidence
that real medieval or Voynich functions are so clean.  It does show that bound
and zero/suppletive functions are recoverable when the representation exposes
their constructional effect; standalone identity is not required.

## Overcontrol

The largest loss caused by moving a grammar variable from evidence into the
nuisance baseline is 14,881.3 bits for global/local frequency on the hidden
FUNCTION_WORD class.  Frequency also removes substantial genuine signal for
COORDINATOR (+5,643.1 bits), REF_ANAPHORA (+2,302.1), and the remaining
classes.  Recurrence and previous-state controls likewise remove thousands of
bits for some endpoints.

This does not mean frequency or position should never be controlled.  It means
the primary functional test must model them as potential grammar channels and
compare causal alternatives; residualizing them away by definition can make a
known function disappear.

## Discovery versus confirmation

Permissive exploration retains 23/36 base endpoint×representation cells.
Strict all-at-once held/fixed-prediction confirmation retains 22/36.  A
predeclared development-domain selection confirms 3/6 chosen representations
on both untouched confirmation domains.  On this large synthetic-positive
panel, the full correction is not the dominant failure mechanism.  The main
failures are representation homology and universal invariance, not max-family
correction.

The 256-world max-family calculation is explicitly a fixed-prediction held
label diagnostic; it does not rerun representation learning in every null
world.  It may not be advertised as a fully nested selection null.

## Ontology audit

The natural-language-like and technical-notation-like inventories are merely
two relabelings of the same six oracle endpoints in this version, so their
aggregate recovery is identical and the ontology comparison is unresolved.
GDT382 therefore does not say whether Voynich is language, notation, or a
hybrid.  A future ontology calibration needs independently authored technical
operations rather than renaming language-derived truth.

## Consequence for GDT376–381

The earlier negative operator-transfer results remain exact results for their
declared instruments.  GDT382 changes their interpretation:

* exact joint-tuple failure is weak evidence against a function because known
  functions often disappear at that level;
* universal cross-domain coefficient failure is weak evidence because all six
  positive controls prefer domain-local realization;
* nuisance conditioning can erase part of the functional channel itself; and
* a clean constructional effect remains recoverable whether encoded freely,
  as an affix, wrapper, boundary, position, or suppletive state.

The next instrument should therefore use domain/register-local realizations,
retain multiple resolutions, treat position/boundary/frequency as competing
grammar channels rather than automatic nuisances, and preregister a disjoint
downstream consequence.  It should be revalidated on these controls before any
new Voynich operator search.

## Claim ceiling and seal

This is comparator positive-control methodology calibration only.  It assigns
no Voynich function, operator, POS, meaning, language, plaintext, or
translation.  No Voynich row was scored.  No f84 file, row, image,
transcription, or formal payload was opened, parsed, retained, or scored.
The independent validator passes 66/66 checks, including a non-importing
rebuild of every held-collection opaque-token model.
