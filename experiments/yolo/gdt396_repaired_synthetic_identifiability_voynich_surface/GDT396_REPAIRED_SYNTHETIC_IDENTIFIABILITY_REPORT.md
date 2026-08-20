# GDT396 repaired synthetic identifiability benchmark

Date: 2026-08-21  
Final qualification status: `NO_CONFIRMATION_ELIGIBLE_PROPERTY`

## Outcome

The repaired instrument did not qualify a single property for untouched
confirmation.  Confirmation seeds `3962000..3962004` were not generated or
opened.  No Voynich text was scored, and neither `f84` nor `f84r` was accessed.

This is primarily an instrument result, not evidence that the hidden synthetic
properties are intrinsically unrecoverable:

* `CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE`
* `SEMANTICS_LIGHT_FALSE_POSITIVE`

The current decoder panel recovers several direct structural identities, but
it cannot recover a recurrent relation well enough to qualify any decoder and
it frequently invents semantic structure in W10.

## What was actually run

The ten frozen GDT395 hidden worlds, generators, codebooks, genealogies, oracle
traces, and world designs were unchanged.  Five new qualification seeds per
world produced 50 paired corpora and 422,705 paired events.  Each event was
rendered as:

* `FREE_SURFACE`, using its frozen GDT395 rendering;
* `VOYNICH_SURFACE`, using a frequency-free injective two-position code over
  the fixed 24-symbol STA-family carrier.

The constrained renderer copied no Voynich frequency, n-gram, word-length,
Currier, q/s, line-entry, or HPR2 rule.  Five independent blind decoder methods
completed 100 world/surface jobs.  Their 24,300 claim files and 162,102,663
typed claim rows were frozen and publicly hash-bound before qualification truth
was opened.

The exact scorer output contains 117,100 rows at the registered irreducible
unit:

`property × world × surface × representation × decoder × seed × method_variant`.

It is published losslessly in
`artifacts/gdt396_qualification_identifiability_matrix.tsv.gz`.

## Qualification arithmetic

| quantity | result |
|---|---:|
| primary routes | 1,350 |
| routes passing endpoint/world/W10 gates before decoder suite | 18 |
| decoder suites passing | 0 / 5 |
| qualified routes | 0 |
| property/surface panels | 50 |
| confirmation-eligible panels | 0 |
| architecture seed decisions passing | 0 / 40 |
| multi-constraint function seed decisions passing | 0 / 500 |

Four decoders recovered the easy equality control on both surfaces.  The fifth
did not.  All five failed the required simple recurrent-relation control.
Therefore every otherwise positive route was suppressed before confirmation.
The result stays zero under either the obsolete two-decoder sentence or the
authoritative three-decoder/two-family panel rule.

## Direct route-level diagnostics

These are useful positive-control diagnostics, not qualified identification
claims.

| property | surface | decoders passing pre-suite | meaningful worlds |
|---|---|---:|---|
| lexical identity | FREE | 4 | 8 / 9 |
| lexical identity | VOYNICH | 4 | 8 / 9 |
| entity-reuse presence | FREE | 1 | 7 / 9 |
| entity-reuse presence | VOYNICH | 1 | 7 / 9 |
| historical ancestry | FREE | 1 | W02, W05, W09 |
| historical ancestry | VOYNICH | 1 | W02, W05, W09 |
| record schema | FREE | 1 | 4 worlds |
| record schema | VOYNICH | 2 | 5-world union |
| state-after identity | FREE | 1 | W04, W07, W09 |
| state-after identity | VOYNICH | 1 | W04, W07, W09 |
| current productive component | FREE | 1 | W02, W09 |
| current productive component | VOYNICH | 0 | — |

The pre-suite count is nine routes per surface.  Thus the 24-symbol surface
channel did not by itself erase exact lexical equality, ancestry, entity-reuse
presence, record schema, or state-after diagnostics.  It did remove the sole
current-productive-component lead.  None of these observations repairs the
failed relation suite.

When zero pre-suite decoders support a property/surface, the compact table says
`NO_SELECTION`; the raw qualifier's `FULL_GROUP` entry in those cells is only a
deterministic zero-candidate tie-break.

## Semantics-light false positives

W10 is decisive.  Of 648 semantic route cells, 554 are complete explicit
`UNSUPPORTED` cells.  Among the 94 actually rated semantic routes:

* 16 pass the W10 ceiling;
* 78 fail it;
* false-positive route fraction = `78 / 94 = 0.829787`;
* FREE and VOYNICH surfaces each have 39 failures out of 47 rated routes;
* no W10-veto-failing route also passes overall route qualification.

The false-positive failures span function/operator class, coordinator,
alternative, generic relation, reference/anaphora, reuse antecedent, productive
morphology/component, current shared meaning, semantic entity/category, and
temporal/state-gate claims.  In particular, all supported function/operator
routes and the large majority of ranked-relation routes confidently find
semantic organization where the frozen world supplies none.

Correct structural clustering in W10 is not charged as semantic error.  Only
the registered semantic outputs are counted here.

## Required adversarial distinctions

The benchmark does not currently distinguish the requested semantic cases:

* organic codebook versus engineered code: not qualified;
* meaningful morphology versus fossil residue: not qualified;
* shared current semantic stem versus genealogical-only ancestry: ancestry has
  a one-decoder diagnostic, but no qualified contrast;
* true function marker versus frequency/position artifact: fails W10 badly;
* meaningful relation system versus semantics-light generator: fails W10 and
  recurrent-relation qualification;
* reference, coordinator/alternative targets, and temporal/state gates: no
  qualified route.

Architecture multi-constraint detection also fails every seed-level point gate.
No architecture claim survives.

## Property decisions

The complete 26-row decision table is
`artifacts/gdt396_property_decisions.tsv`:

| classification | count |
|---|---:|
| `SEMANTICS_LIGHT_FALSE_POSITIVE` | 12 |
| `CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE` | 13 |
| `REQUIRES_EXTERNAL_GROUNDING` | 1 |

The last row is actual lexical meaning, which was never a scored endpoint.
These labels diagnose the instrument.  They do not say that a property is
scientifically absent or intrinsically unidentifiable.

## Execution corrections and residual debt

The full score completed, but the first qualifier invocation stopped before
writing a result because it demanded a W10 event rate from an explicitly
`UNSUPPORTED` representation cell.  The append-only correction exempts only a
complete five-seed all-`UNSUPPORTED` route; absent or non-unsupported routes
remain fail-closed.  V1 validation passes 13/13, the validator-provenance V2
successor passes 11/11, and independent review is GO.  Claims, metrics,
thresholds, and decoder outputs were unchanged.

Three older specification debts are disclosed and not repaired from exposed
outcomes:

1. an obsolete two-decoder sentence is superseded by the frozen three-decoder,
   two-family correction;
2. architecture qualification omitted its paired-interval conjunct, but all
   40 seed cells already fail the point gates;
3. morphology qualification omitted boundary-F1 and used mean rather than
   per-status AP, but no morphology route passes the looser gate.

None can change the zero qualified-route result.

## Decision

`NO_CONFIRMATION_ELIGIBLE_PROPERTY`

No direct Voynich semantic experiment follows.  Internal inference for lexical
entities, productive versus fossilized components, functional classes,
reference, coordination/alternative relations, temporal/state gates, and
meaning is not calibrated by the current instrument.

A future synthetic attempt would need genuinely new relation-capable decoder
versions and new qualification/confirmation seed blocks.  It may not reuse the
exposed GDT396 qualification or reserved confirmation seeds.  No synthetic
label, role, ontology, sound, language, plaintext, or translation transfers to
Voynich.
