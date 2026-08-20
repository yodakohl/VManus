# GDT395 post-freeze oracle scoring design

Status: `FROZEN_SCORER_DESIGN_V2_BEFORE_ORACLE_ACCESS`

This is a conservative post-freeze scorer for the interfaces that actually
exist. It never reads observation text, codebooks, genealogies, generators,
world source, Voynich material, or f84. It joins frozen held-event claims to a
sealed oracle only after all blind-freeze and pre-oracle claim gates pass. It
writes aggregate metrics only: no event ID, oracle label, claim/oracle joined
row, visible string, record, or local machine path is emitted.

## Mandatory authenticated gate

The scorer accepts these exact blind artifacts:

- freeze schema `GDT395_BLIND_CLAIMS_FREEZE_V2`;
- validation schema `GDT395_BLIND_CLAIMS_VALIDATION_V2`;
- freeze `status: PASS`, `phase: FROZEN_BEFORE_ORACLE_ACCESS`, and
  `oracle_blind: true`, plus `oracle_opened: false`, `oracle_rows_read: 0`,
  `voynich_rows: 0`, and an all-false nonempty `f84` seal object;
- validation `status: PASS`;
- a nonempty `checks` object in each artifact, whose values are genuine JSON
  Booleans and all `true`;
- a valid `content_sha256` in each artifact, computed from canonical ASCII JSON
  after removing only the top-level `content_sha256` member, using sorted keys
  and separators `(',', ':')`;
- exactly one validation binding of role `claims_freeze` to the physical freeze
  file and its SHA-256;
- a nonempty freeze `implementation_map` with exactly five decoder IDs. Every
  entry repeats its `decoder_id`, has `oracle_blind: true`, and has
  `model_family` exactly `SOL` or `LUNA`. The panel must be two Sol and three
  Luna decoders.

The freeze has three disjoint binding roles:

```json
{
  "bindings": {
    "authentic_event_claims": [{"path": "...", "sha256": "..."}],
    "pair_event_claims": [{"path": "...", "sha256": "..."}],
    "world_claims": [{"path": "...", "sha256": "..."}]
  }
}
```

Each role is a nonempty list of exact `{path, sha256}` objects. Supplied files
must equal the bound paths for that role exactly; a file bound under one role
cannot satisfy another, and any path occurring in two roles is rejected. The
scorer verifies these bytes before it opens or hashes any oracle path.

The scorer also requires the claims-freeze-bound public
`gdt395_corpus_manifest.tsv`. Before opening any sealed row, it selects the
exact 50 W01--W10/seed15--19 oracle entries and requires the supplied oracle
paths to equal that set. Each sealed file is hashed and must match its frozen
manifest SHA-256 before it is parsed. Training-seed oracle files are not
opened.

## Accepted claim shapes

Authentic and pair event claims are exact `decoder_api.CLAIM_FIELDS` TSVs. The
authentic panel is exactly 10 worlds x held seeds 15--19 x six representations
x five decoders. The pair panel is exactly W02/W03/W09/W10 x five held seeds x
six representations x five decoders. Within each view and world/seed, every
event ID must recur in all 30 representation/decoder panels. Duplicate or
missing compound claim identities are refused.

The scorer accepts the 50 individually frozen world-claim JSON files actually
produced by the decoders: one for every world x decoder. These are not
representation-level rows and are never expanded to an imaginary 300-row TSV.
A file is either the exact seven-field `WORLD_CLAIM_FIELDS` object, with its
single W01--W10 ID taken from a strict path token, an exact flat object adding
`world_id`, or an exact `{"world_id": ..., "claim": {...}}` (also
`world_claim`) envelope. If both
path and envelope contain a world ID, they must agree. The attached decoder ID
must agree with the event panel and frozen implementation map.

Before oracle access, confidence must be finite and within `[0,1]`; every
cluster/component field must be a nonempty opaque ID or literal `UNRESOLVED`;
every target field must be literal `UNRESOLVED` or one non-pipe event ID in the
same held view; and endpoint IDs must occur among claim event IDs for the same
view/world/seed. The morphology claim columns are deliberately validated as
opaque IDs, not coerced to Booleans.

Oracle rows must have exactly `world_api.ORACLE_FIELDS`, one row per held
`(world_id, corpus_seed, event_id)`, and 8,448--8,512 events per world/seed.
The authentic claim/oracle join must be a complete one-to-one set equality;
the pair event set must be an exact subset. Oracle identifier normalization is
case-sensitive. Literal `NONE` is absence. Empty/null/`UNRESOLVED` oracle truth
is invalid. Pipe values must be sorted unique nonempty atoms with no whitespace
and cannot mix `NONE` with another atom. A clustering truth must be a singleton.
Refusal text names only the field/gate and never echoes a raw oracle value.

## Frozen endpoint disposition

`endpoint_qualification` is a machine-readable column in panel, aggregate,
decision, and JSON summary output.

| Property | Disposition and exact qualification |
|---|---|
| `LEXICAL_IDENTITY` | score anonymous `lexical_cluster` / `lexical_id` equality only; not word meaning |
| `SEMANTIC_ENTITY_IDENTITY` | score anonymous entity co-identity only |
| `HISTORICAL_STEM_ANCESTRY` | score only the shared-`historical_stem_id` partition; no ancestor direction, stage, path, rule, merger/split history, or genealogy |
| `PRODUCTIVE_MORPHOLOGY` | `UNSCORED_INTERFACE_HOLD`: produced resolved values are opaque component IDs, not Boolean predictions |
| `FOSSILIZED_MORPHOLOGY` | `UNSCORED_INTERFACE_HOLD`: produced resolved values are opaque component IDs, not Boolean predictions |
| `FUNCTION_CLASS` | score anonymous function-class partition only |
| `COORDINATOR_RELATION` | `UNSCORED_INTERFACE_HOLD`: no frozen typed and ranked target mapping |
| `ALTERNATIVE_RELATION` | `UNSCORED_INTERFACE_HOLD`: same interface gap |
| `REFERENCE_ANAPHORA` | `UNSCORED_INTERFACE_HOLD`: no direct oracle reference target |
| `TEMPORAL_STATE_GATE` | `UNSCORED_INTERFACE_HOLD`: no matching claim/truth field |
| `SCOPE` | `UNSCORED_INTERFACE_HOLD`: accepted inputs contain no validated event-order contract |
| `ENTITY_REUSE` | score only recurring anonymous entity IDs, restricting recovery truth to IDs occurring at least twice in that held world/seed; singleton IDs are ineligible rather than false reuse claims |
| `OPERATOR_CLASS` | `UNSCORED_INTERFACE_HOLD`: no oracle operator class |
| `RECORD_SCHEMA` | `UNSCORED_INTERFACE_HOLD`: accepted claim/oracle scorer inputs contain no `record_id`, so event-to-record collapse is impossible |
| `REGISTER_LOCAL_VARIANT` | score authentic-corpus register-realization identity only; never pair view and never register meaning |
| `SEMANTIC_CATEGORY` | score anonymous category-partition recovery only; not category names, ontology, or lexical meaning |
| `ACTUAL_LEXICAL_MEANING` | `UNSCORED_INTERFACE_HOLD`: no gloss/meaning claim or truth |

No HOLD property is mapped to a surrogate, thresholded, aggregated into a
scientific verdict, or assigned an identifiability decision. In particular,
the scorer contains no relation-type substring mapping, state-pair proxy,
function-as-operator alias, component-ID-as-Boolean coercion,
oracle-row-order-as-scope-order substitution, or identity-as-meaning proxy.

## Scoreable clustering metrics

The seven scoreable authentic endpoints use NMI, Hubert-Arabie ARI, and
pairwise F1. Labels are anonymous and the metrics are permutation invariant.
Every decoder `UNRESOLVED` is a private per-event abstention singleton; it is
not a shared cluster and is not dropped. A seed is
`ABSENT_OR_NO_CAPACITY` unless truth has at least two classes, one same-class
pair, and one different-class pair. The point threshold is conjunctive:
NMI >= .35, ARI >= .20, and pair-F1 >= .35.

The table also reports resolved eligible-unit coverage, unresolved count,
oracle-`NONE` count and claims on those absent units, and predicted
co-clustering false-positive rate among truth-different pairs. For W10 the
property-specific false-positive rate is the larger applicable value of:

- resolved-claim rate on oracle-`NONE` units; and
- resolved predicted co-cluster rate among truth-different eligible pairs.

Successful recovery of a real W10 formal partition is not itself called a
semantic false positive. `SEMANTIC_CATEGORY` remains anonymous even when its
partition aligns.

## Replicate, decoder, W10, and inference handling

Each seed is thresholded as a complete conjunction. A decoder point-clears a
world/property/representation only if at least three of five held seeds pass;
the coordinate-wise seed median is diagnostic only. A world point-clears only
if at least three of five complete decoders pass and at least two of those
passes are from the three frozen Luna decoders. All six representations remain
separate; a common representation is used for any cross-world point pattern.
W10 is a guard and never counts as a meaningful positive world.

For each W10 property/representation, the scorer first takes the median across
decoders within each held seed, then enumerates all `5^5 = 3,125` seed-cluster
bootstrap resamples and reports the one-sided 95th percentile upper bound. The
guard's point diagnostic requires that upper bound to be <= .10. Because the
accepted inputs contain no record IDs, this cannot perform the review's
required within-seed complete-record resampling.

Likewise, the accepted inputs do not supply frozen record-block nulls or the
9,999 locality-preserving permutations needed for raw p-values, Holm familywise
correction, and lower confidence-bound threshold checks. The scorer therefore
takes the required conservative option: every non-HOLD cross-world result is
`EXPLORATORY_UNCONFIRMED`, raw and Holm-adjusted p-values are `NA`,
`confirmatory_promotions_enabled` is false, and it is impossible for this code
to emit `PROPERTY_IDENTIFIABLE_FROM_INTERNAL_STRUCTURE` or a confirmatory
family-specific/confused verdict. It may describe a
`POINT_THRESHOLD_GENERAL_PATTERN`, `POINT_THRESHOLD_FAMILY_SPECIFIC_PATTERN`,
or `NO_POINT_THRESHOLD_PATTERN`, but none is a scientific promotion.

## Pair and world-level outputs

Without `record_id`, same-record locality cannot be verified. All pair
property endpoints are therefore hard-disabled in the scorer. Pair claim bytes
remain frozen and validated as part of the adversarial protocol, but the
current interface cannot produce a defensible pair identifiability metric.

The 50 world JSON claims produce one architecture panel per decoder, without a
representation column. Architecture clusters are compared with frozen broad
families using NMI/ARI/pair-F1. Boolean world hypotheses use BA/MCC/FDR; only
the semantics-light flag has direct frozen truth, while the other public world
assignment mappings are labeled proxies. World-level output is diagnostic and
cannot substitute for any of the 17 event properties.

The six named method stress tests still lack dedicated decoder predictions and
are emitted as `UNSCORED_NO_EXPLICIT_DECODER_PREDICTIONS`.

## Aggregate-only outputs

The output directory contains `panel_metrics.tsv`, `pair_panel_metrics.tsv`,
`world_representation_metrics.tsv`, `property_decisions.tsv`,
`w10_false_discoveries.tsv`, `architecture_metrics.tsv`,
`method_stress_tests.tsv`, and `summary.json`. These contain only counts,
metrics, qualifications, provenance hashes under portable labels, HOLD or
exploratory statuses, and compact diagnostics. No event-level material is
written.
