# GDT384 report — priority role-specific relation

## Decision

`PRIORITY_RELATION_UNIDENTIFIABLE_SOURCE_OVERLAP_STOP_BEFORE_VOYNICH`

The frozen priority COORDINATOR test failed the definition-overlap gate.  Under
the sequential method, the 2,048-world null and the other five role families
were not entered.  Stage B was not created; no Voynich or GDT381 target row was
read.

## Source and capacity

The exact PCEEC2 commit and 84-file parsed bundle reproduce their GDT378 hashes.
The hidden relation builder derived 2,347 sibling-constituent-homology positives
and 25,171 negatives among 27,518 PCEEC2 elements.  It exported no source word,
POS, parse label, concept, or parent identifier.  CoReMA relation capacity was
also inventoried, but no nonpriority outcome was scored.

## Priority result

| quantity | result |
|---|---:|
| hidden COORDINATOR positives | 1,292 / 27,518 |
| held-file role AUC | 0.949269 |
| role codelength gain | +3,148.368 bits |
| sibling-homology positives | 2,347 / 27,518 |
| source-only sibling AUC | 0.797797 |
| exact-signature overlap AUC | 0.516094 |
| source + role sibling AUC | 0.797743 |
| AUC increment from role | -0.000054 |
| relation codelength gain from role | +425.113 bits |
| positive held source-file folds | 76 / 84 |

The role detector therefore works, and its probability improves calibration
enough to save bits.  That is not a valid relational confirmation.  The full
source-side observation predicts the hidden parse relation at AUC `0.797797`,
above the frozen leakage ceiling `0.65`, while adding the role probability does
not improve rank discrimination.  The outcome is substantially encoded in the
same construction/placement variables used by the predictor.

This is exactly the overlap failure GDT384 was designed to catch.  A relation
can be independently derived from a gold parse yet still be non-independent of
the model's source-side observation.  Parse provenance alone does not make it
a disjoint prediction target.

## Sequential stop

The priority pre-null gate failed, so the method requires:

* no null search;
* no scoring of ALTERNATIVE_OR, REF_ANAPHORA, UNTIL_STATE_GATE,
  POLARITY_EXCLUSION, or FUNCTION_WORD;
* no target freeze; and
* no Voynich access.

The retained capacity table is not evidence for those five roles.  It records
only which independently sourced relations could support a future redesigned
comparator test.

## What this teaches us

GDT383's generic short-future target was too weak, while GDT384's first
role-specific parse target is too entangled with the licensed source grammar.
The remaining methodological target is narrower: a relation must be both
role-appropriate and absent from the source representation.  Candidate future
positive controls should use genuinely external links—explicit antecedent IDs,
editor parent/child edges, paired proposition annotations, or held relation
edges—not parse topology that is already recoverable from construction state.

No threshold should be lowered and the attractive `+425`-bit calibration gain
must not be promoted.

## Claim ceiling

This is a comparator instrument failure.  It establishes no Voynich latent
role, coordination, operator, POS, meaning, language, plaintext, or
translation.  GDT381/F1 and the other closed routes remain closed.  f84
remained sealed.
