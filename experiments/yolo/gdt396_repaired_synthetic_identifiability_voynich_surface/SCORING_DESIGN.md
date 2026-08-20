# GDT396 scoring design

Status: `REGISTERED_BEFORE_QUALIFICATION_OR_CONFIRMATION`.

## Unit and chronology

The irreducible result row is:

```text
property × world × surface × representation × decoder × seed × method_variant
```

Every registered cell is `SCORED`, `NO_CAPACITY`, `PROHIBITED_SURFACE`, or
`UNSUPPORTED`; missing rows are invalid. Development selects decoder
hyperparameters and one primary representation per property. Qualification
selects eligible decoder/property routes. Confirmation seeds are generated and
opened only after those choices, all thresholds, nulls, scorer, and independent
validator have been frozen.

Seeds are repeated measures inside a world, not independently designed worlds.
Alternate renderings of one event are paired surfaces, not replications.

## Direct truth only

The scorer normalizes GDT395 oracle rows into direct endpoints without changing
them. Pipe-separated IDs are exploded into repeated rows. A typed relation edge
is scoreable only when the frozen oracle supplies an unambiguous type-to-target
association: one relation type may govern one or more targets, or a row may
contain a single target. Rows with multiple independently sorted types and
multiple targets are eligible only for untyped `GENERIC_RELATION` union scoring.

No substring match, function-as-operator proxy, state-pair proxy,
identity-as-meaning proxy, or component-string-as-Boolean proxy may create a
truth. Event-level productive morphology is the direct Boolean oracle field;
fossil presence is direct non-`NONE` fossilized-component truth. Record schema
is evaluated once per record. Actual lexical meaning is not an endpoint.

Historical-stem evidence remains four distinct properties:

1. `HISTORICAL_ANCESTRY`: equality of historical stem IDs;
2. `CURRENT_PRODUCTIVE_COMPONENT`: current morpheme equality restricted by the
   direct productive Boolean;
3. `FOSSIL_COMPONENT`: fossilized component equality/presence;
4. `CURRENT_SHARED_MEANING`: current component-semantics equality.

They are never collapsed into one stem score.

## Qualification

Qualification follows `DECODER_QUALIFICATION_SPEC.md`. Eligibility is per
`decoder × property × representation × surface`. One primary representation
is frozen per property by: most qualifying decoder/world cells, then median
conjunctive margin, then the fixed order in `decoder_api_v2.REPRESENTATIONS`.

Confirmation requires at least three qualified decoders from at least two
method families for that property. There is no Sol/Luna quota.

## Confirmation seed gates

### Partitions

Resolved coverage `>= .25`, NMI `>= .35`, Hubert-Arabie ARI `>= .20`, and
pair-F1 `>= .35`. Unresolved events receive private singleton predictions so
abstention cannot improve co-clustering.

### Binary morphology/state/reuse

Resolved coverage `>= .25`, balanced accuracy `>= .65`, MCC `>= .20`, and FDR
`<= .40`, with both truth classes present. Abstentions are completed
adversarially against truth.

### Ranked relations/references

Resolved query coverage `>= .25`, unconditional Hits@1 `>= .15`, and
`MRR - locality-preserving-null MRR >= .05`. Missed or abstained true targets
score zero. The candidate universe is frozen from visible record/line locality
and includes negative sources; it is never oracle-filtered.

### Scope

Resolved query coverage `>= .25` and all-source mean interval IoU `>= .35`;
endpoint accuracy and exact interval accuracy are mandatory diagnostics.

### Entity reuse

Both the event-level reuse binary gate and recurrent entity co-identity
pair-F1 `>= .35` must pass in the same seed.

### Record schema

Use the partition gate on records with each record weighted once.

## Decoder, world, and property decisions

A decoder passes one world/property when at least three of five confirmation
seeds pass and the hierarchical 95% bound crosses every applicable threshold.

A world passes when at least
`max(3, floor(number_of_qualified_decoders / 2) + 1)` qualified decoders pass,
spanning two method families. Leave-one-decoder-out results are mandatory.

The same development-frozen representation passing at least seven of nine
meaningful worlds supports general identification. Passing two through six
worlds supports only world-family-specific identification. One world,
representation switching, one decoder family, or a W10 semantic false positive
cannot support identification.

Use 9,999 deterministic locality-preserving randomizations. Resample seeds,
then complete records within seed, and recompute the entire seed→decoder→world
decision. Holm correction covers all registered properties and the two surface
conditions.

## Paired surface ablation

Report every property/world/decoder seed metric separately for
`FREE_SURFACE` and `VOYNICH_SURFACE`, plus paired differences. No cross-channel
mapping or transfer is allowed during fitting. A property is surface-robust
only when the identical primary representation and qualified decoder panel
passes both channels.

## Adversarial controls

- Organic versus engineered is evaluated on W02/W03 using truth-recovery
  differences, not nonsignificant surface similarity.
- Meaningful relational versus semantics-light is evaluated on W09/W10.
- W10 structural schema or recurrence recovery is not a semantic false
  positive; resolved lexical semantics, functional classes, typed relations,
  references, productive morphology, or current shared meaning are.
- The hierarchical upper 95% false-claim bound for oracle-absent W10 semantic
  units must be `<= .10`.
- Productive versus fossilized discrimination requires the binary gate plus
  at least `.05` balanced-accuracy and `.10` MCC advantage against status-
  swapped truth on the productive-XOR-fossil subset.

## Multi-constraint comparison

For each eligible function/operator route, `MULTI_CONSTRAINT` and
`SCALAR_BOTTLENECK` share decoder, training bytes, representation, candidates,
abstention rule, and compute budget. Multi-constraint evidence may intersect
position, recurrence, left/right compatibility, variable arity, relation
topology, scope, register substitution, deletion/substitution consequences,
and construction participation. The scalar comparator is selected from the
frozen development set: recurrence, type-token ratio, unigram entropy, mean
group length, or record-length variation.

`MULTI_CONSTRAINT_SUPERIOR` requires the full property gate plus a paired
improvement in four of five seeds, lower 95% bound above the frozen margin, and
Holm-adjusted `p <= .05`, with no required specificity metric worsening beyond
margin. Otherwise report scalar superiority, equivalence only when every
interval is inside its frozen margin, or inconclusive.

## Property decisions

Each property receives exactly one user-specified classification:

`IDENTIFIABLE_UNDER_BOTH_SURFACES`,
`IDENTIFIABLE_ONLY_WITH_FREE_SURFACE`,
`IDENTIFIABLE_UNDER_VOYNICH_SURFACE_IN_SOME_WORLD_FAMILIES`,
`CONFUSED_WITH_ORGANIC_CODEBOOK`,
`CONFUSED_WITH_FOSSILIZED_MORPHOLOGY`,
`SEMANTICS_LIGHT_FALSE_POSITIVE`,
`REQUIRES_EXTERNAL_GROUNDING`,
`CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE`, or
`NOT_IDENTIFIABLE_UNDER_TESTED_CONDITIONS`.

False-negative and false-positive rates are reported separately. No composite
post-hoc score is permitted.
