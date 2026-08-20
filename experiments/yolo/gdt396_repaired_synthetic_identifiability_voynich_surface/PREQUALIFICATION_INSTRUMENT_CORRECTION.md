# GDT396 pre-qualification instrument correction

Status: `AUTHORITATIVE_VERSIONED_CORRECTION_BEFORE_QUALIFICATION_GENERATION`.

The early protocol freeze remains byte-frozen and historical. Its validator
now intentionally reports one failed binding check because Boolean enforcement
and phase-authority enforcement changed two bound implementation files. The
paired-corpus validator correspondingly fails only its inherited
`protocol_valid` check; all 17 corpus/scientific checks pass. A versioned
prequalification correction freeze records the exact two old/new hashes and
must validate before the decoder panel can freeze. Independent
development-only review then found execution ambiguities and implementation
defects before qualification observations existed. This document narrows and
corrects the executable instrument; the later decoder-panel freeze binds it,
all repaired code, and a new independent GO review.

## Interface corrections

- Decoders emit Python Boolean values in memory. The runner validates their
  type and serializes them canonically as uppercase `TRUE`/`FALSE`; the scorer
  accepts only those stored literals. Positive scope rows are validated before
  serialization.
- `classify_world` may return decoder-private JSON-safe descriptors. All
  scoreable architecture rows must already be normalized into the nine output
  tables by `decode`; the runner never interprets private descriptors.
- Missing event endpoints are normalized to explicit `UNSUPPORTED` rows before
  validation. Silence is never treated as an abstention or negative claim.
- Pipe-valued identity/component oracle fields are sorted and retained as one
  exact unordered composite signature, as frozen in `ORACLE_TRUTH_SPEC.md`.
  Only relation-target sets are exploded. This corrects the contradictory
  sentence in the earlier scoring design.

## Qualification corrections

- Confirmation requires three qualified decoders spanning at least two method
  families. The earlier two-decoder sentence is superseded; no model-brand vote
  quota applies.
- The three-relation-type capacity gate applies to the generic recurrent-
  relation endpoint. Typed coordinator/alternative/reference routes retain
  their direct single-type truth.
- The GDT395 oracle contains no component-span offsets. Morphology spans remain
  schema/locality diagnostics and cannot be truth-scored. Productive/fossil
  qualification uses the direct event Boolean truths and exact direct component
  partitions; no span truth is fabricated.
- W10 vetoes a semantic route when more than 10% of oracle-absent events receive
  resolved positive/partition/relation claims. Structural lexical equality,
  record schema, recurrence, historical ancestry, and fossil residues are not
  semantic false positives in W10.
- Decoder-wide eligibility requires easy equality recovery and at least one
  recurrent relation route under both surfaces, plus deterministic and
  schema-valid runner output.
- Event-level multi-constraint versus scalar comparison is registered only for
  `FUNCTION_OPERATOR_CLASS` at `MULTI_RESOLUTION`. It requires matched held
  event coverage and a pair-F1 lead of at least .10 in four of five seeds in at
  least two meaningful worlds. Architecture variants remain a separate direct
  world-metadata diagnostic.

## Execution corrections

- One fresh restricted process handles exactly one decoder, world, and surface.
  A runtime audit hook denies repository reads outside that decoder, process or
  network creation, and writes outside the claims root after blind observations
  are materialized. Decoder-facing manifests contain no oracle path, oracle
  hash, hidden trace, or mapping commitment.
- Actual supplied-model immutability and a byte-identical second decode are
  checked. Rank caps, unique targets, explicit query coverage, candidate
  locality, morphology ranks, Boolean type, and status-dependent fields are
  mechanical gates.
- The fixed `CLAIM_RETENTION_PLAN.md` serializes every endpoint at one primary
  representation rather than duplicating it across all seven. Decoder-emitted
  tables are shape-checked; every retained endpoint is completed and fully
  validated before serialization. Omitted representation cells are explicit
  `UNSUPPORTED` aggregate rows rather than millions of redundant event claims.
- Qualification generation and decoding require a hash-complete decoder-panel
  freeze plus independent PASS validation. Confirmation requires a later
  confirmation-instrument freeze binding qualification decisions, final nulls,
  scorer, aggregator, and independent validator.

No qualification or confirmation observation or oracle existed or was opened
when these corrections were made. No Voynich corpus, image, transcription,
`f84`, or `f84r` material is an input.
