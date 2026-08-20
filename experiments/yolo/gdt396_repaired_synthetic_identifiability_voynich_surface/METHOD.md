# GDT396 repaired synthetic identifiability method

Status: `REGISTERED_UNSCORED_PROTOCOL_IN_DEVELOPMENT`.

## Question

Which lexical, genealogical, morphological, functional, relational, scope,
register, schema, and semantic properties remain recoverable when the same
frozen synthetic writing systems are observed through a 24-atom
Voynich-constrained channel? Does the repaired typed decoder instrument recover
known positive controls without inventing semantics in the frozen W10
semantics-light control?

## Inputs

- The exact ten GDT395 world generator files and their frozen hashes.
- The exact GDT395 world API and normalization layer.
- The GDT395 seed `0..19` corpora as legacy calibration only.
- New seeds from the unchanged generators, preassigned before generation:
  development `3960000..3960004`, qualification `3961000..3961004`, and
  untouched confirmation `3962000..3962004`.
- The official 24-position STA family inventory
  `ABCDEFGHJKLMNPQRSTUVWXYZ` documented in
  `experiments/semantic_assumptions/LRG001_OFFICIAL_ALPHABET_RECOVERY_SPEC.md`.
  The names identify inventory positions only and are never emitted as visible
  surface characters.

No Voynich transcription, page image, annotation row, tuple, frequency,
n-gram, q/s rule, Currier statistic, or other manuscript-derived grammar is an
input. `f84` and `f84r` are forbidden.

## Method

### Frozen hidden worlds

GDT396 may call each GDT395 generator at a new integer seed, but may not modify
the generator, codebook, genealogy, oracle schema, event semantics, or native
rendering logic. Every generator, support module, and GDT395 freeze is
hash-bound before corpus production. The codebook and genealogy must be exact
across every old and new seed.

### Paired surface channels

Each generated bundle yields one hidden event/oracle trace and two observation
views with identical event order and all identical non-surface fields.

`FREE_SURFACE` retains `visible_group` byte-for-byte from GDT395.

`VOYNICH_SURFACE` tokenizes the free group against the world's already frozen
abstract alphabet, then substitutes every abstract atom with a fixed-width
two-atom codeword over the 24 positions. Two atoms are used in every world,
including worlds whose native inventory is smaller than 24, so code width does
not reveal which worlds required composition. A cryptographic random salt and
world-specific permutation are frozen before generation and are constant
across all seeds. This is a bijection on the world's native atom inventory and
therefore preserves equality, recurrence, and the native codebook/evolutionary
structure while removing the unconstrained glyph inventory. It also creates a
known deterministic within-code bigram and doubles native-atom length; both are
reported as channel properties, not recovered grammar.

The constrained surface is serialized as a length-prefixed binary atom stream
whose only values are integers `0..23`. Those integers are transport indices,
not digits in the visible writing system. JOIN/SPACE and page, paragraph,
record, and line boundaries remain separate source fields. No EVA, Latin
letters, digits, punctuation, brackets, private-use characters, or invented
extra surface symbols are emitted by the constrained renderer.

Decoders receive one channel per process and do not receive the cross-channel
mapping. The paired event link is available only to the scorer after all held
claims are frozen.

### Seed chronology

- `0..19`: paired reconstruction of the already exposed GDT395 panel; never
  final confirmation.
- `3960000..3960004`: decoder and interface development; oracle feedback is permitted
  and logged.
- `3961000..3961004`: qualification; decoders are frozen before these oracles are opened
  and cannot be repaired after qualification.
- `3962000..3962004`: untouched confirmation; generated only after the qualified decoder
  panel, scoring code, thresholds, and independent validator are frozen.

### Repaired claim interface

Observation packets retain `record_id`, event order, and all physical boundary
fields. Decoders emit anonymous typed claims for lexical/entity identity,
historical ancestry, current productive components, fossilized components,
current shared meaning, function/operator classes, ranked typed relations and
references, state-gate events, scope spans, recurring entity reuse, record
schema, register realization, semantic-category partitions, and world
architecture. Morphology uses exactly `CURRENTLY_PRODUCTIVE`, `FOSSILIZED`, or
`NO_COMPONENT_CLAIM`.

The API exposes no hidden concept names or world ontology. Unsupported claims
must be `UNRESOLVED`. Relation and reference claims contain ranked candidate
event IDs and calibrated scores; scope claims contain start/end event IDs and
scores.

### Decoder qualification

Eligibility is based on a frozen development/qualification suite, never model
brand. Before any confirmation packet is opened, a decoder must recover an
easy equality partition, avoid singleton-everything and one-cluster collapse,
recover a recurrent relation above a frozen opportunity baseline, emit valid
typed relation/scope/morphology claims, and distinguish at least one meaningful
control from W10 without semantic false positives. Qualification is required
under both surface channels. Several mutually independent Sol-designed
decoders form the primary panel; Luna or other decoders are robustness controls
if and only if they qualify.

### Confirmation matrix

The complete row key is
`property × world × surface_channel × representation × decoder × seed`.
Recovery is reported separately for identity partitions, four distinct stem
truths, morphology status, function/operator classes, ranked relation targets,
references, temporal/state gates, scope, entity reuse, record schema, register
realization, semantic category, and architecture. False-negative and
false-positive rates are separate. Multi-constraint functional detection is
compared with a matched single-score classifier.

W10 semantic claims are false positives even when its structural clustering is
correct. W02/W03 and W09/W10 are evaluated as adversarial contrasts without
collapsing genealogy, current productivity, or current meaning.

## Decision rule and claim ceiling

No follow-on Voynich experiment is licensed unless at least one scientifically
relevant property is recovered under `VOYNICH_SURFACE` on seeds
`3962000..3962004`, in
multiple independently designed meaningful worlds, by multiple independently
qualified decoders, without the corresponding W10 false positive, and with the
relevant organic/engineered adversarial comparison surviving.

Each property receives exactly one of:

- `IDENTIFIABLE_UNDER_BOTH_SURFACES`
- `IDENTIFIABLE_ONLY_WITH_FREE_SURFACE`
- `IDENTIFIABLE_UNDER_VOYNICH_SURFACE_IN_SOME_WORLD_FAMILIES`
- `CONFUSED_WITH_ORGANIC_CODEBOOK`
- `CONFUSED_WITH_FOSSILIZED_MORPHOLOGY`
- `SEMANTICS_LIGHT_FALSE_POSITIVE`
- `REQUIRES_EXTERNAL_GROUNDING`
- `CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE`
- `NOT_IDENTIFIABLE_UNDER_TESTED_CONDITIONS`

The maximum claim is a calibration statement about what the frozen instrument
can or cannot recover from these synthetic observation channels. No synthetic
role, label, code, ontology, or decoder output may be transferred to Voynich.
