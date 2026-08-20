# GDT397 bounded observability-ceiling and ontology-correction audit

Status: `FROZEN_BEFORE_CEILING_SCORING`

Date: 2026-08-21

## Purpose and ceiling

GDT397 is a small synthetic-only post-mortem of GDT396. It asks which formal
properties are observable under oracle-supervised training and which claims are
logically underdetermined by observational equivalence. It does not train a new
general decoder, generate data, score Voynich, or infer a semantic label.

The audit separates:

1. `FORMAL_IDENTITY`: observable recurrence or equality;
2. `ANONYMOUS_STRUCTURAL_ROLE`: an unlabeled construction, control role, edge,
   state transition, or scope boundary;
3. `REFERENTIAL_SEMANTICS`: external denotation, a domain meaning, an English
   gloss, or a named operator.

Formal recovery never licenses level 3.

## Frozen inputs and hard guards

Only the already generated GDT396 qualification block is admissible:

- worlds: meaningful W02 and W09; semantics-light W10 for false-positive audit;
- seeds: exactly `3961000..3961004`;
- observations: existing `FREE_SURFACE` packets and paired constrained-surface
  metadata/atom streams;
- truth: the already exposed qualification oracle packets;
- claims: the already frozen GDT396 qualification claim packet;
- existing GDT395/GDT396 source files may be hashed or read as specifications,
  but no generator is invoked.

The runner rejects any seed outside that set, any confirmation path, and any
path containing `396200`. Neither `f84` nor `f84r` is an input. No new corpus,
seed, world, decoder, or LLM output is permitted.

## Observational-equivalence witness

The byte-identical W09 seed-3961000 `FREE_SURFACE` observation packet is paired
with two interpretation records:

- `A_ORIGINAL_SEMANTIC_ORACLE`: the exposed original oracle;
- `B_FORMAL_ONLY`: the same rows projected to visible equality, record schema,
  construction, state transition, scope, and formal edge fields, with external
  entity, activity/domain, semantic category, lexical meaning, component
  meaning, and readable function/relation names removed.

Both rows record exactly the same observation SHA-256. A decoder receiving only
that packet must therefore emit the same output under A and B. External
denotation, lexical meaning, English glosses, and the difference between a
meaningful operator and an isomorphic formal symbol are
`NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE`. Observable branch/rejoin or
scope algebra is not erased by this result.

## Fixed cross-seed instrument

Every fitted route is world-local and surface-local. Four qualification seeds
train and the fifth is held; all five rotations are run. Oracle values enter
targets only. Features are computed solely from:

- visible groups or constrained atoms and their 1--3-token substrings;
- exact equality, recurrence, and record-local recurrence;
- separators/boundaries, line/record position, record and line length;
- register, hand, layout role, and ambiguous-boundary flag;
- immediately neighboring visible events and record-local topology.

The one flexible model family is fixed weighted ridge projection with
`lambda=10`, a deterministic signed 256-coordinate hash for event features,
and fixed numeric pair features for ranked relations/scopes. The simple event
baseline is a 64-coordinate position/frequency/boundary ridge model with no
surface identity or substring. Pair baselines are frozen rule scores, not
tuned models. There is no hyperparameter or representation search.

Three observation views are reported:

- `FREE_RAW`;
- `VOYNICH_RAW`, treating each of the 24 atom positions separately;
- `VOYNICH_ATOM_DECODED`, grouping the fixed-width stream into consecutive
  two-atom codewords without consulting FREE text or an oracle.

The last representation is an exact opaque inverse segmentation of the
bijective channel. Any raw constrained-surface loss is a decoder/segmentation
failure, not information destruction. Equality of FREE and atom-decoded scores
is checked to numerical tolerance where their feature algebras are isomorphic.

## Exactly five endpoints

### A. `LEXICAL_IDENTITY` — positive control

Truth is the existing globally stable `lexical_id`. The flexible event model
predicts held labels. The baseline uses position/frequency/boundary only. Exact
visible-equality clustering is reported separately. Metrics are NMI, ARI, and
pair-F1. A fold is strong when flexible NMI >= .70, ARI >= .55, pair-F1 >= .65,
and each exceeds the nuisance baseline by >= .10. Four of five folds suffice.

### B. `ANONYMOUS_CONTROL_ROLE`

Readable names are collapsed before fitting. W02 positive truth is exactly
`semantic_category == FUNCTION`; W09 positive truth is exactly
`function_class in {relator, schema_marker, quantifier}`. These values define
only a binary control-like/content-like partition for calibration. Metrics are
AUROC and average precision. A fold is strong when AUROC >= .75, AP exceeds
prevalence by >= .15, and both AUROC and AP exceed the nuisance baseline by
>= .05. The endpoint passes only with >=4/5 strong folds in both worlds.

### C. `REFERENCE_OR_REUSE_EDGE`

The source queries are W02 `PREVIOUS_MENTION` and W09 `REFERENCE` rows whose
direct target is earlier in the same seed. Every earlier event is eligible.
One weighted ridge ranker uses only source/candidate observation features.
Frozen baselines are recency, nearest same-form then recency, and nearest
same-record then recency. Metrics are MRR and Hits@1. A fold is strong only if
the learned ranker exceeds every baseline by >= .05 MRR and >= .03 Hits@1.
The endpoint passes only with >=4/5 strong folds in both worlds.

### D. `ALTERNATIVE_OR_BRANCH_TOPOLOGY`

The exact capacity gate is at least 25 direct alternative/branch positives in
every seed of at least two meaningful worlds. W09 passes; W02 has zero. This
endpoint is frozen as `CAPACITY_INSUFFICIENT` and is not replaced or fitted.

### E. `STATE_GATE_OR_SCOPE_ENDPOINT`

Each unique, same-record oracle scope supplies one start and one variable-
horizon end. The learned ranker chooses an end among all later events in the
record. Frozen baselines choose the physical record end or start+3 clipped to
the record. Metrics are exact endpoint accuracy and span IoU. A fold is strong
only if accuracy exceeds both baselines by >= .10 and mean IoU exceeds both by
>= .05. The endpoint passes only with >=4/5 strong folds in both worlds.

No endpoint name is transferred to Voynich and no readable role label is an
output of the fitted models.

## W10 ontology correction

The frozen GDT396 claims are rescored descriptively against W10's formal oracle:

- `FUNCTION_OPERATOR_CLASS` partitions are compared with construction,
  record-schema, and state-transition partitions. A route is called formally
  aligned only if one fixed formal partition has NMI >= .25 and ARI >= .10 in
  at least four seeds. Alignment does not validate a semantic label.
- `TEMPORAL_STATE_GATE` binary claims are compared only with actual scope-end
  events. Detecting such an endpoint is formal, not semantic.
- W10 has no oracle relation edges. Any positive frozen
  `REFERENCE_ANAPHORA` or `ALTERNATIVE_RELATION` target assertion is therefore
  a genuine invented formal edge.

This descriptive rescore does not enter the hard-stop gate.

## Decisions and hard stop

Each endpoint receives exactly one registered decision:

- `OBSERVABLE_AND_CURRENT_DECODER_LIMITED`
- `STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE`
- `NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL`
- `CAPACITY_INSUFFICIENT`
- `CURRENT_GDT396_RESULT_WAS_GATE_CONTAMINATION`
- `NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE`

The positive identity control is `CURRENT_GDT396_RESULT_WAS_GATE_CONTAMINATION`
if strong: it was already recovered by GDT396 decoders but suppressed by the
unrelated recurrent-relation suite. A passing B--E endpoint is
`STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE`; a powered failure
is `NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL`.

Further internal operator-decoder development is closed unless at least one of
B--E passes under `VOYNICH_ATOM_DECODED` in both independently designed worlds,
with >=4/5 strong held seeds and improvement over its strongest baseline. If
several pass, only the one with the largest minimum normalized gate margin is
nominated for a future targeted decoder. GDT397 itself stops after the audit;
it neither starts nor designs GDT398.
