# D396S05 blind decoder attestation

Decoder: `d396s05_multiconstraint_function`  
API: `2`  
Method family: `matched_conjunctive_signal_lattice`

## Blindness and scope

This decoder was authored in an isolated context. I read only `AGENTS.md`,
`VOYNICH_CURRENT_ROUTE.md`, the GDT396 `README.md`, `METHOD.md`,
`CLAIM_INTERFACE.md`, `DECODER_EXECUTION_SPEC.md`,
`DECODER_QUALIFICATION_SPEC.md`, `CLAIM_RETENTION_PLAN.md`,
`src/decoder_api_v2.py`, `src/observation_api.py`, and blind legacy/development
observations exposed by that observation API.

I did not read any oracle, hidden trace, truth specification, scorer,
validation implementation, GDT395 world/generator/report, sibling decoder or
sibling output, qualification or confirmation observation, Voynich corpus,
`f84`, or `f84r`. No readable role name, hidden concept name, world-specific
rule, or cross-surface mapping is embedded in the decoder. The only use of the
constrained channel's width is the public GDT396 rule that two transport atoms
encode one native atom.

Only these two files were created or changed by this work:

- `decoders/d396s05_multiconstraint_function/decoder.py`
- `decoders/d396s05_multiconstraint_function/ATTESTATION.md`

## Method

Training rows may contain multiple seeds for one world and one surface. Record
containers are keyed internally by `corpus_seed + record_id`; the canonical
JSON model retains explicit per-seed namespace summaries. It learns exact
surface recurrence, boundary/position distributions, neighboring-type degree,
and recurrent proper prefix/suffix pieces. A piece is productive only when it
crosses at least three complete surface types, two records, and (when supplied)
two training seeds. A smaller recurrent family may be labeled fossilized. The
labels are API morphology statuses, not linguistic translations.

At `MULTI_RESOLUTION`, every held event has three matched
`FUNCTION_OPERATOR_CLASS` rows:

- `PRIMARY` is the decoder's ordinary multi-resolution output.
- `MULTI_CONSTRAINT` hashes a conjunction of four separately visible signals:
  training recurrence, agreement with training boundary/position behavior,
  visible neighbor compatibility, and recurrent-construction participation.
- `SCALAR_BOTTLENECK` quantizes exactly one statistic selected on training
  observations alone from group length, training recurrence, within-group
  repetition, within-group entropy, and boundary concentration.

The multi and scalar routes both resolve every held event and both have the
same maximum budget of eight clusters. Selection is label-free: robust spread
is rewarded and between-seed drift is penalized. No held outcome or truth
selects the statistic or cuts.

Architecture `MULTI_CONSTRAINT` combines five aggregate signals: recurrent
partition evidence, boundary/context stability, within-record relation/reuse
evidence, reusable proper-piece evidence, and record-schema regularity. Its
positive conjunction requires at least three signals, including relation,
piece, or schema evidence. The matched architecture scalar is exactly one
training-selected statistic from the preregistered set: repetition rate,
type-token ratio, unigram entropy, mean group length, or record-length
variation. Multi and scalar architecture partitions have the same six-cluster
budget and complete coverage.

All class and subtype IDs are anonymous hashes or anonymous bounded-bin IDs.
All nine API tables are emitted. Every claim-bearing table has explicit
`PRIMARY` resolved or abstaining rows; target abstention is represented in
`target_queries` because `target_ranks` has no status field. Architecture and
matched function rows add the two comparison variants only where required.

## Frozen candidate and span policies

- `GENERIC_RELATION`, `COORDINATOR_RELATION`, and `ALTERNATIVE_RELATION`:
  every other visible event in the same record is eligible.
- `REFERENCE_ANAPHORA` and `ENTITY_REUSE_ANTECEDENT`: every strictly earlier
  visible event in the same record is eligible.
- Ties are resolved by event ID; ranks are contiguous, nonduplicated,
  nonincreasing, and capped at five.
- Scope is a forward span beginning after the source and ending at the first
  visible line/boundary stop or after four events, whichever comes first. A
  negative scope claim has empty endpoints.
- Morphology offsets are half-open offsets in the selected visible surface;
  constrained-channel native-unit offsets are multiplied by the public width
  of two.

The decoder uses held rows only to construct the visible within-record context
and candidate sets for that held seed; `DECODER_META` therefore declares
`transductive_within_held_seed: true`. The fitted model is never mutated.

## Development self-test

The self-test fit three blind legacy training seeds (`0,1,2`) for a single
world/surface model and decoded development seed `3960000`. It was run
separately for both `FREE_SURFACE` and `VOYNICH_SURFACE`, through all seven
supported representations. For every cell it checked API-V2 shape, canonical
JSON safety, model immutability, Python `bool` types, matched event coverage,
cluster caps, and byte-identical repeated `MULTI_RESOLUTION` decoding. It used
no oracle feedback.

A second portability sweep fit two blind legacy seeds (`0,1`) independently
for every one of the ten opaque world IDs on each surface, decoded a bounded
sample of development seed `3960001` at `MULTI_RESOLUTION`, and repeated the
shape, canonical-JSON, typed-Boolean, nine-table, and immutability checks. All
20 world/surface cells passed.

SHA-256 results:

| artifact | SHA-256 |
|---|---|
| `decoder.py` | `2d24f18f9ec74e17a49ad0ea7ed09d436a90b3ed4af5b953d2e08b55f3f8776c` |
| free-surface canonical model | `c3b643a4c4874a1d643463484104ea69d28b4707d602e8cce1031e6d3ffd0ef8` |
| free-surface repeated multi-resolution output | `409166374510e9cd37a7b514c9cea29135e3c5477e403beebaf93c7627cdd098` |
| constrained-surface canonical model | `deb95650129981cd6a69019f381b12a4b4a101e6041b51a8a098394a05afc5a3` |
| constrained-surface repeated multi-resolution output | `2c2bfc68fc932c82fa6ad9f175c494cc2b351db12f92db2c7a559f173c15b93e` |

In this blind self-test, both channels independently selected
`training_recurrence` for the event scalar and `mean_group_length` for the
architecture scalar. Selection is repeated by `fit`; these names are reported
for audit and are not hard-coded choices.

## Caveats

This is an unsupervised decoder instrument, not a semantic interpretation.
Behavioral clusters, morphology statuses, relations, scopes, and architecture
flags are hypotheses generated from visible structure. Development shape and
determinism checks do not establish recovery, calibration, or qualification.
No qualification/confirmation packet or oracle has been opened, and no result
licenses a claim about the Voynich manuscript.
