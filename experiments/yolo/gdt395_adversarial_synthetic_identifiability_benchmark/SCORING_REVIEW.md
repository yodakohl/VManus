# GDT395 scoring and identifiability review

Status: pre-outcome, read-only interface audit. This review specifies what can
be scored from the frozen observation, claim, and oracle schemas. It does not
inspect a corpus, oracle row, claim, codebook, genealogy, generator, world
source, Voynich source, or other decoder/scorer.

## Executive verdict

The interface supports anonymous recovery of several partitions and two
event-level binary properties, plus interval scope. It does **not** support
every named property in the frozen 17-property list. In particular, the
interface has no lexical-gloss claim or truth, no event-level ancestry graph
claim, no oracle operator class, no separate reference target, no frozen
relation-type vocabulary, and no ranked target output even though the method
requires MRR.

No scorer may repair those gaps by choosing a convenient oracle composite
after seeing claims. A structurally adjacent field is not an interchangeable
target.

## Exact property-to-field map

`GO` below means that the frozen fields can support the stated *anonymous*
endpoint, subject to the eligibility and validation gates in this review.
`HOLD` means that the named property cannot receive a confirmatory verdict
from the frozen interface. `GO (narrow)` deliberately limits a broader name to
the exact partition that the fields express.

| Frozen property | Decoder claim | Oracle truth | Primary unit and metric family | Interface verdict |
|---|---|---|---|---|
| `LEXICAL_IDENTITY` | `lexical_cluster` | `lexical_id` | held event; clustering | **GO** for anonymous lexical-ID equality, not word meaning |
| `SEMANTIC_ENTITY_IDENTITY` | `entity_cluster` | `semantic_entity_id` | held event; clustering | **GO** for anonymous entity co-identity |
| `HISTORICAL_STEM_ANCESTRY` | `stem_cluster` | `historical_stem_id` | held event; clustering | **GO (narrow)** only for the partition “has the same historical-stem ID”; **HOLD** for ancestor direction, stage, path, rule, merger/split history, or a recovered genealogy |
| `PRODUCTIVE_MORPHOLOGY` | `productive_component_prediction` | `productive_morphology` | held event; binary | **GO**, only if the oracle value is a genuine Boolean event target |
| `FOSSILIZED_MORPHOLOGY` | `fossilized_component_prediction` | `fossilized_component_ids` | held event; binary presence/absence | **GO (narrow)** for “one or more fossilized component IDs are present”; **HOLD** for component identity or history |
| `FUNCTION_CLASS` | `function_cluster` | `function_class` | held event; clustering | **GO** for anonymous function-class partition recovery |
| `COORDINATOR_RELATION` | `predicted_relation_target_event_id` | `relation_target_event_id`, filtered by `relation_type` | source event; relation retrieval | **HOLD**: the interface freezes neither the coordinator type allow-list nor a type-to-target association for multi-valued rows; it also lacks ranked predictions required for genuine MRR |
| `ALTERNATIVE_RELATION` | `predicted_relation_target_event_id` | `relation_target_event_id`, filtered by `relation_type` | source event; relation retrieval | **HOLD** for the same reasons as `COORDINATOR_RELATION` |
| `REFERENCE_ANAPHORA` | `predicted_reference_target_event_id` | no direct oracle field; the only possible surrogate is `relation_target_event_id` filtered by `relation_type` | source event; reference retrieval | **HOLD** until a distinct oracle reference target or a frozen, unambiguous relation-type mapping is added; genuine MRR also needs ranked output |
| `TEMPORAL_STATE_GATE` | no matching claim field | closest oracle fields are `state_before`, `state_after`, `construction_id`, and scope endpoints | none defensibly frozen | **HOLD**: neither the gate truth function nor its matching claim is defined |
| `SCOPE` | `predicted_scope_start_event_id`, `predicted_scope_end_event_id` | `scope_start_event_id`, `scope_end_event_id` | scoped event; interval | **GO**, for endpoint recovery and interval overlap only |
| `ENTITY_REUSE` | `entity_cluster` | `semantic_entity_id` | unordered held-event pair; clustering/co-reference | **GO** for repeated anonymous entity identity; it is a pairwise view of the entity partition, not a second semantic meaning endpoint |
| `OPERATOR_CLASS` | `operator_cluster` | no `operator_class` oracle field | none defensibly frozen | **HOLD**: `function_class`, `relation_type`, a state transition, or a constructed tuple of them cannot be selected post hoc as an operator class |
| `RECORD_SCHEMA` | `record_schema_cluster` | `record_schema_id` | held record, not event; clustering | **GO**, after deterministic event-to-record collapse |
| `REGISTER_LOCAL_VARIANT` | `register_variant_cluster` | `register_realization_id` | held event; clustering | **GO** on authentic full corpora only; this recovers realization identity, not a register's meaning |
| `SEMANTIC_CATEGORY` | `semantic_category_cluster` | `semantic_category` | held event; clustering | **GO (narrow)** for anonymous category-partition recovery; aligned cluster success does not recover category names or lexical meanings |
| `ACTUAL_LEXICAL_MEANING` | no matching claim field | no lexical gloss/meaning field | none | **HOLD** and necessarily `PROPERTY_REQUIRES_EXTERNAL_GROUNDING` |

`construction_cluster`/`construction_id` form a potentially scoreable
construction-identity endpoint, but construction identity is not one of the
17 frozen properties. It must not be relabelled as temporal gating or operator
class. The world-level architecture output likewise is not a substitute for
any of the 17 properties and lacks a frozen event-style linkage in the public
world-claim schema.

## Truth and claim normalization

### Reserved values and pipe fields

1. Oracle identifiers are exact, case-sensitive strings. The scorer must not
   stem, case-fold, substring-match, or otherwise reinterpret them.
2. Literal `NONE` means that the property or target is absent. An oracle
   `UNRESOLVED`, empty string, null, or missing field is invalid rather than a
   negative example.
3. A pipe value is split only on literal `|`; empty atoms, duplicate atoms,
   leading/trailing whitespace, and a mixture such as `NONE|x` fail
   validation. The canonical representation is the sorted unique atoms joined
   by `|`, matching the public `pipe` helper.
4. A clustering truth must contain exactly one non-`NONE` atom. More than one
   atom is a multi-label target, whereas ARI, NMI, and ordinary pairwise F1
   require a partition. Such a row is not silently converted to a composite
   label: the property/seed fails the target-shape gate unless a multi-label
   endpoint was separately frozen before claims were opened.
5. A relation/reference target may contain more than one non-`NONE` atom. A
   single predicted target is a hit if it belongs to that accepted target set.
   However, multiple `relation_type` atoms and multiple target atoms have no
   preserved pairing in the schema. A property-specific relation row is
   eligible only when the type is a single atom from that property's frozen
   allow-list, or when a future schema explicitly binds each target to a type.
6. Scope endpoints must each be a singleton. Separate pipe lists of starts and
   ends do not define interval pairing and therefore cannot be scored.
7. Decoder `UNRESOLVED` is an abstention. It is never an oracle class, never an
   aligned cluster, never a correct `NONE`, and never removed from the primary
   denominator. An invalid event ID is an attempted but wrong prediction and
   also triggers an invalid-target report.

### Eligibility universes

- **Clustering:** a unit is recovery-eligible when its oracle field is one
  valid, non-`NONE` scalar atom. Oracle-`NONE` units are retained for the
  false-positive guard, not the recovery partition. A seed has clustering
  capacity only if it has at least two truth classes, at least one same-class
  pair, and at least one different-class pair.
- **Productive morphology:** every event with Boolean
  `productive_morphology` is eligible. The scorer must accept JSON Boolean
  truth, not infer truth from a string or another morphology field.
- **Fossilized morphology:** every event with a valid canonical
  `fossilized_component_ids` value is eligible. Truth is positive exactly when
  the parsed set is nonempty and negative exactly when the field is `NONE`.
- **Relation/reference:** a source is positive-eligible only when its
  property-specific type is eligible and its accepted target set is nonempty.
  Every accepted target must exist in the same held world/seed packet and in
  the endpoint's frozen candidate universe. `NONE` targets form the specificity
  and false-positive universe. Training-seed targets are never eligible.
- **Scope:** a source is positive-eligible when both oracle endpoints are
  singleton held-event IDs, the start does not follow the end in the validated
  held-event order, and both endpoints lie in the permitted view. Rows with
  both endpoints `NONE` are negative scope rows. A one-sided oracle endpoint,
  an out-of-packet endpoint, or a reversed interval fails validation.
- **Entity reuse:** eligible pairs are distinct events within the declared
  comparison locality. A pair is positive exactly when both scalar
  `semantic_entity_id` values are equal; it is negative otherwise. Full-corpus
  and pair-view localities must never be mixed.
- **Record schema:** the scoring unit is one record. Oracle
  `record_schema_id` must be constant within the record. Resolved decoder
  `record_schema_cluster` values must also be unanimous within a record; a
  disagreement makes that record's prediction `UNRESOLVED`. Event count must
  not weight a schema class.

No world or seed may disappear from a denominator merely because a property
has no capacity there. It is reported as `ABSENT_OR_NO_CAPACITY` and does not
count as an identifiable-world success.

## Metric definitions

### Clustering and identity properties

The primary partition contains every eligible unit. Each `UNRESOLVED` claim is
represented as a private per-unit abstention singleton; using one shared
`UNRESOLVED` cluster would create artificial agreement. Report:

- Hubert-Arabie adjusted Rand index (ARI);
- normalized mutual information
  `NMI = 2 I(truth; claim) / (H(truth) + H(claim))`, with natural logs and
  `NMI = 1` only when both valid partitions are the same constant partition;
- pairwise F1 from `TP = same truth and same resolved claim`,
  `FP = different truth and same resolved claim`, and
  `FN = same truth and different/unresolved claim`;
- resolved-unit coverage and the predicted co-cluster false-positive rate as
  mandatory diagnostics.

The frozen pass gate is conjunctive: `ARI >= 0.20`, `NMI >= 0.35`, and pairwise
`F1 >= 0.35`. Resolved-only scores may be reported but cannot determine a pass.
For `ENTITY_REUSE`, the same partition metrics are reported, with pairwise F1
as the direct reuse endpoint. All-pairs counts should be obtained from the
contingency table, not by treating event pairs as independent observations.

### Binary morphology properties

Accepted resolved claims are Boolean true/false. For the primary conservative
score, abstentions are completed adversarially: an abstention on a positive
truth is counted as a false negative and an abstention on a negative truth as
a false positive. This supplies a worst-case balanced-accuracy/MCC/FDR bound
without rewarding selective prediction. Report the ordinary resolved-only
confusion matrix separately.

The frozen pass gate is conjunctive: balanced accuracy `>= 0.65`, Matthews
correlation `>= 0.20`, and false-discovery rate `<= 0.40`. Both truth classes
must occur. If there is no predicted-positive denominator, FDR is undefined
and the cell cannot pass, even if another convention would print zero.

### Relation and reference targets

For each eligible source, let `T_i` be its nonempty accepted target set and
`C_i` the frozen candidate set of other visible held events allowed by the
endpoint locality.

- coverage is non-abstaining attempted sources divided by all eligible
  sources;
- top-1 accuracy is `1[prediction in T_i]` averaged over all eligible sources;
- covered precision is the same hit count divided by attempted sources and is
  diagnostic only;
- target-distance error is the absolute difference between the predicted
  event rank and the nearest acceptable target rank, with ranks derived from
  validated held-event order. Report median absolute error and its
  normalization by `max(1, |C_i|-1)`. An invalid predicted ID receives the
  maximum normalized error rather than disappearing.

The current claim schema emits only one target, not a ranked list. Therefore
its reciprocal-rank contribution is necessarily 1 for a hit and 0 otherwise,
making “MRR” identical to unconditional top-1 accuracy. Uniform single-shot
chance is `mean_i |T_i| / |C_i|`. The frozen numerical relation gates would be
coverage `>= 0.25`, this single-shot hit rate `>= 0.15`, and hit rate minus
chance `>= 0.05`; these can be reported as diagnostics, but they do **not**
implement the method's stated retrieval MRR. A confirmatory relation property
remains on HOLD until ranked target lists are added or the endpoint is formally
renamed and re-frozen as single-shot top-1 before outcomes are inspected.

### Scope

Construct an inclusive interval from validated event ranks, not by subtracting
opaque event-ID strings. For each eligible source:

- coverage requires both predicted endpoints to be non-abstaining valid held
  IDs in the permitted view;
- marginal endpoint accuracy is the number of exactly correct start/end
  endpoints divided by twice the number of eligible sources;
- exact-interval accuracy requires both endpoints to match;
- interval IoU is intersection length divided by union length for inclusive
  rank intervals. A missing, invalid, or reversed predicted interval has IoU
  zero and incorrect endpoints.

The primary IoU is the mean over **all** eligible sources, not only covered
sources. The frozen pass gate is coverage `>= 0.25` and mean interval IoU
`>= 0.35`. Endpoint and exact-interval accuracies remain required reports even
though the original freeze gives them no numerical pass threshold.

## Seed, decoder, representation, and world aggregation

1. Seeds 0--14 are training only. Each of seeds 15--19 is scored separately.
   A seed is a corpus replicate, never an independent writing system.
2. A decoder/property/world/representation cell passes only when the complete
   conjunctive metric gate passes in at least three of the five held seeds.
   Also report each seed and the coordinate-wise median across the five; do not
   manufacture a pass from different metrics clearing in different seeds.
3. “Median decoder” is implemented as a majority of complete decoder passes,
   not a coordinate-wise median assembled from different decoders. With the
   frozen minimum panel of two Sol and three Luna decoders, at least three of
   five decoders must pass and at least two of the three independent Luna
   decoders must pass. Report every decoder and a leave-one-decoder-out
   sensitivity analysis. A best-decoder success is a method-sensitivity
   diagnostic, not property identifiability.
4. Representation is not selected separately for each world. All six
   representations are separate registered endpoints. A property-level result
   must use the same representation across every counted world. If the winning
   representation is selected after scoring, the six-way search is included
   in multiplicity correction and the selected representation is named.
5. The semantics-light world is a guard, not a positive world in the world
   count. A general result requires the same property/representation to pass
   in at least seven of the nine meaningful worlds W01--W09 **and** to pass the
   W10 false-positive guard. A family-specific result requires two through six
   meaningful-world passes at that same representation and the same guard.
6. A result in one meaningful world, a result only in W10, a result requiring
   world-specific representation switching, or a result that fails the guard
   is `NOT_IDENTIFIABLE_BY_THIS_PANEL` rather than family-specific.

World counts describe the ten frozen designed systems. They do not estimate a
population prevalence over all historical writing systems.

## Semantics-light false-positive guard

The frozen maximum is `0.10`. It must be applied to a property-specific false
claim rate, not to a generic world-classifier confidence:

- clustering: on oracle-`NONE` units, the resolved-cluster claim rate; when a
  valid truth partition exists, also the co-cluster rate among truth-different
  pairs. Use the larger applicable rate;
- binary: false-positive rate among oracle-negative events;
- relation/reference: non-abstaining target claims on oracle-`NONE` sources;
- scope: two-ended interval claims on oracle-no-scope sources.

The 95% upper uncertainty bound, clustered by held seed and complete record,
must be `<= 0.10`; a point estimate alone is insufficient. If W10 contains a
real formal analogue of a structural property rather than oracle absence,
successful recovery is not itself a false positive. Instead, comparable W09
and W10 recovery demonstrates that the endpoint does not identify meaningful
semantics. Such recovery may support a structural property but must block a
semantic or lexical-meaning interpretation.

`SEMANTIC_CATEGORY` can therefore establish only anonymous category
partitioning. It cannot clear the guard for *meaning* merely because its
clusters align. `ACTUAL_LEXICAL_MEANING` has no score at all.

## Adversarial-pair scoring restrictions

The amended pair views are separate from the authentic full-corpus matrix.
They may not replace or augment full-corpus world counts.

Allowed pair-view endpoints are limited to:

- `LEXICAL_IDENTITY`, `SEMANTIC_ENTITY_IDENTITY`, and `ENTITY_REUSE`, using
  only equality/reuse within the same selected complete record (same-line
  results may be reported separately);
- `RECORD_SCHEMA`, with one unit per selected complete record;
- coordinator/alternative/relation and reference targets only after their
  missing type mappings are frozen, and only when source and target remain in
  the same selected complete record;
- `SCOPE`, only when source, start, end, and every ranked event in the interval
  remain inside one selected complete record.

Pair-view exclusions are page/paragraph conclusions, register/hand effects,
layout effects, glyph-internal or component claims, morphemes, productive or
fossil morphology, historical genealogy, temporal-state semantics, operator
semantics, semantic category, and lexical meaning. Cross-record endpoints and
cross-record recurrence are excluded because the amended endpoint is
record/line-local. Masked `NONCOMPARABLE` fields must never be treated as a
real shared category. Corpus-local recoded glyph strings support equality
partitions only; their shapes, substrings, edit distances, or inferred
components are inadmissible.

The W02/W03 codebook pair can test whether an allowed local structural endpoint
distinguishes organic from engineered organization. It cannot adjudicate
genealogy or morphology because those endpoints are expressly excluded. The
W09/W10 pair can test whether an allowed local structural endpoint separates a
meaningful from a semantics-light system; failure to separate blocks semantic
interpretation but does not erase authentic-full-corpus structural recovery.

## General, family-specific, confused, and grounding decisions

- `PROPERTY_IDENTIFIABLE_FROM_INTERNAL_STRUCTURE`: the same representation
  satisfies the median-decoder gate in at least seven meaningful worlds, the
  semantics-light guard, uncertainty gate, and multiplicity gate.
- `PROPERTY_ONLY_IDENTIFIABLE_UNDER_SPECIFIC_WORLD_FAMILIES`: the same
  representation satisfies those gates in two through six meaningful worlds.
  Name the successful frozen families; do not infer a broader family from a
  post hoc cluster of winners.
- `PROPERTY_CONFUSED_WITH_ORGANIC_CODEBOOK_EFFECTS`: available only for an
  endpoint allowed in the W02/W03 pair view. Require a paired equivalence
  analysis, not merely a nonsignificant difference. Before claims are opened,
  freeze equivalence margins; defensible defaults are `0.05` for ARI, NMI,
  pairwise F1, balanced accuracy, FDR, coverage, hit rate, normalized distance,
  endpoint accuracy, and IoU, and `0.10` for MCC. The 95% paired interval must
  lie wholly inside every applicable margin. Otherwise the result is
  inconclusive, not “indistinguishable.”
- A claim that the pairs are distinguished requires an endpoint difference
  beyond the same margin, in the predeclared direction in at least four of five
  held seeds, with a multiplicity-corrected paired randomization result.
- `PROPERTY_REQUIRES_EXTERNAL_GROUNDING`: mandatory for actual lexical meaning
  and for any named semantic interpretation not represented by an anonymous
  frozen claim/truth pair. Semantic-category clustering may be reported, but
  category names, word glosses, historical narratives, and Voynich
  interpretations remain external-grounding claims.

## Uncertainty and multiple testing

Every primary table must include raw unit count, truth-class/positive count,
number of records, five seed values, decoder values, unresolved and invalid
rates, effect estimate, 95% interval, chance/null value, raw p-value where a
test is used, adjusted p-value, and threshold verdict.

- Never use 8,448 events as independent replicates. Use a hierarchical or
  randomization interval that resamples the five held seeds first and complete
  records within seed; line blocks replace records only for genuinely
  line-local endpoints. Pair-view inference resamples matched complete-record
  units within held seed.
- For cluster metrics, permute truth labels within the predeclared record/line
  block while preserving class sizes. For binary metrics, permute the Boolean
  truth within the same block. For relation and scope, use locality-preserving
  target/interval nulls with the same eligible sources and candidate-set sizes.
  Use at least 9,999 randomizations for a confirmatory p-value.
- The six representations are six opportunities. In the absence of one
  pre-frozen primary representation per property, control Holm family-wise
  error at `0.05` across all scoreable property-by-representation primary
  claims (up to 17 x 6 cells). Unsupported properties remain listed as HOLD;
  they are not silently replaced with new endpoints.
- Correct the two adversarial-pair families separately across every allowed
  property-by-representation pair test. Correct the six method stress tests as
  a separate registered family. Any unregistered family subdivision or
  best-decoder/best-world search is exploratory.
- Frozen effect-size thresholds remain necessary after p-value correction.
  For a positive claim, the 95% lower bound should clear lower thresholds and
  the upper bound should clear upper-bound gates such as FDR and the
  semantics-light false-positive maximum. Report a threshold crossing as
  uncertain rather than rounding it into a pass.
- Decoders are a fixed method panel, not IID population samples. Report
  majority, Sol/Luna strata, and leave-one-decoder-out sensitivity rather than
  a misleading decoder-level standard error.

## Concrete pre-score validation gates

Scoring stays locked unless all applicable gates pass.

1. **Freeze integrity:** verify the bound hashes and statuses of the original
   interface and the pre-decoding pair amendment; verify that authentic main
   corpora were not changed by pair-view construction.
2. **Blind provenance:** each decoder attests `oracle_blind=true`, was not a
   designer of the scored world, and used no oracle, family label, codebook,
   genealogy, generator source, other decoder output, or Voynich source.
3. **Exact schemas:** observations, oracle rows, and claims have exactly their
   public field sets; event keys are one-to-one; claim world, seed,
   representation, and decoder provenance match; there is exactly one claim
   row per held event.
4. **Split integrity:** all learned state is fit on seeds 0--14. Seeds 15--19
   are decoded separately and never tune vocabularies, components, thresholds,
   confidence, candidate restrictions, or representation choice.
5. **Claim validity:** representation is supported; confidence is finite in
   `[0,1]`; cluster labels are anonymous; binary values are Boolean or
   `UNRESOLVED`; endpoint predictions are `UNRESOLVED` or visible IDs in the
   permitted held view.
6. **Oracle shape:** reserved values and pipes satisfy the normalization rules;
   Boolean truth is truly Boolean; record schema is constant within a record;
   target IDs exist in the same held world/seed; scope order is valid; truth
   prevalence/capacity is reported for all five held seeds.
7. **Missing mapping gate:** do not score coordinator, alternative, or
   reference properties until exact relation-type allow-lists and multi-target
   typing are frozen. Do not score genuine MRR until ranked claim fields and a
   candidate-order contract are frozen. Do not score temporal gates or
   operator classes until matching truth and claim fields are frozen.
8. **Abstention gate:** primary denominators include abstentions under the
   rules above. Resolved-only results can never be promoted to primary.
9. **Representation gate:** no world-specific representation switching and no
   oracle-selected level. Any post-score representation choice receives the
   full six-way correction.
10. **Pair-view gate:** exactly ten complete records per world/seed; exact
    matching channels and the three recurrence-difference limits pass;
    equality partitions are unchanged by injective recoding; all masked
    fields are `NONCOMPARABLE`; local IDs do not restore original carrier
    channels; every scored endpoint satisfies the same-record locality rule.
11. **Null and uncertainty gate:** null candidate sets, blocking units,
    interval method, equivalence margins, and multiplicity families are fixed
    before claim/oracle joining. Report all seeds, worlds, representations, and
    decoders, including failures and no-capacity cells.
12. **Decision gate:** apply complete per-seed gates, decoder majorities,
    fixed-representation world counts, the W10 guard, uncertainty bounds, and
    multiplicity correction in that order. No grand mean can override a failed
    gate.

## Final interface disposition

The frozen interface is **GO** for anonymous lexical identity, semantic-entity
identity, shared historical-stem identity (not full ancestry), productive
morphology presence, fossilized-component presence, function class, scope,
entity reuse, record schema, register realization, and semantic-category
partition recovery.

It is **HOLD** for coordinator relation, alternative relation, reference
anaphora, temporal state gating, operator class, full historical genealogy,
component-specific fossil/productive history, and actual lexical meaning until
the specific schema gaps above are corrected before outcome access. No GDT395
result, including a GO endpoint, can assign a meaning, ancestry narrative, or
synthetic ontology to Voynich material.
