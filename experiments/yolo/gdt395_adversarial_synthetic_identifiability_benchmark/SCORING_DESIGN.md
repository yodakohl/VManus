# GDT395 post-freeze oracle scoring design

Status: `FROZEN_SCORER_DESIGN_BEFORE_ORACLE_ACCESS`

This scorer is a post-freeze evaluator. It reads no observation text, generator,
codebook, genealogy, world source, or Voynich material. It consumes frozen blind
claim TSVs, the corresponding world-claim TSV, and sealed event-oracle TSVs. It
emits aggregate metric tables only; it never writes a claim/oracle joined row.

## Mandatory safety gate

`score_identifiability.py` refuses before opening or hashing an oracle unless all
of the following hold.

1. The claims-freeze JSON has status `PASS`, phase
   `FROZEN_BEFORE_ORACLE_ACCESS`, and `oracle_blind: true`.
2. Every main claim, pair-view claim, and world-claim input has an exact
   `{path, sha256}` binding in that freeze. A `hashes` mapping is also accepted
   as a compact spelling of the same bindings.
3. The validation JSON has status `PASS` and binds the claims-freeze file
   itself by path and SHA-256. The validation artifact's schema name is owned
   by the revised freezer and is not guessed by this scorer.

This is deliberately strict. The expected freeze shape is:

```json
{
  "status": "PASS",
  "phase": "FROZEN_BEFORE_ORACLE_ACCESS",
  "oracle_blind": true,
  "bindings": {
    "event_claims": [{"path": "...", "sha256": "..."}],
    "pair_event_claims": [{"path": "...", "sha256": "..."}],
    "world_claims": [{"path": "...", "sha256": "..."}]
  }
}
```

The validation artifact analogously binds the freeze under `bindings`. A PASS
word without the cryptographic link is insufficient.

## Input and panel invariants

Event claims use exactly `decoder_api.CLAIM_FIELDS`. Oracle rows use exactly
`world_api.ORACLE_FIELDS`. The scorer independently embeds those frozen field
lists so importing either API cannot execute workspace code. World claims add
the envelope fields `world_id` and `representation` to
`WORLD_CLAIM_FIELDS`; this repairs the API's otherwise absent keys without
altering a decoder's returned hypothesis.

The authentic panel must contain W01--W10, held seeds 15--19, all six frozen
representations, and exactly five decoder IDs. Every event must have exactly
one claim in every world/seed/representation/decoder panel and exactly one
oracle row keyed by `(world_id, corpus_seed, event_id)`. Joins use only that
key. Main oracle files may also contain training seeds, which are ignored.

The pair panel must contain W02, W03, W09, and W10 at all held seeds,
representations, and decoders. Its event IDs must be a subset of the authentic
oracle. Every selected event must occur in every pair representation/decoder
panel. The separate pair-view validator remains responsible for the ten
complete-record and carrier-match guarantees, because record/layout fields are
not in the scorer's allowed inputs.

## Frozen 17-property mapping

Cluster metrics treat claim labels as anonymous. NMI, ARI, and pair-F1 are
permutation invariant, which is equivalent to optimal label alignment without
assigning semantic names. Each `UNRESOLVED` claim becomes a private per-unit
abstention singleton, never a shared artificial cluster and never a removed
primary-denominator row. A seed needs at least two truth classes, a same-class
pair, and a different-class pair; otherwise it is `ABSENT_OR_NO_CAPACITY`.

| Property | Claim | Oracle truth | Kind / qualification |
|---|---|---|---|
| `LEXICAL_IDENTITY` | `lexical_cluster` | `lexical_id` | cluster |
| `SEMANTIC_ENTITY_IDENTITY` | `entity_cluster` | `semantic_entity_id` | cluster; identity, not meaning |
| `HISTORICAL_STEM_ANCESTRY` | `stem_cluster` | `historical_stem_id` | GO (narrow): shared historical-stem-ID partition only; no direction, path, stage, merger/split history, or genealogy |
| `PRODUCTIVE_MORPHOLOGY` | `productive_component_prediction` | Boolean `productive_morphology` | GO only for the event-level Boolean |
| `FOSSILIZED_MORPHOLOGY` | `fossilized_component_prediction` | valid pipe-set presence in `fossilized_component_ids` | GO (narrow): presence only, not component identity/history |
| `FUNCTION_CLASS` | `function_cluster` | `function_class` | cluster |
| `COORDINATOR_RELATION` | no defensible frozen typed/ranked channel | none | `UNSCORED_INTERFACE_HOLD` |
| `ALTERNATIVE_RELATION` | no defensible frozen typed/ranked channel | none | `UNSCORED_INTERFACE_HOLD` |
| `REFERENCE_ANAPHORA` | no direct matching oracle target | none | `UNSCORED_INTERFACE_HOLD` |
| `TEMPORAL_STATE_GATE` | no matching claim field | no frozen truth function | `UNSCORED_INTERFACE_HOLD` |
| `SCOPE` | predicted start/end | oracle start/end | interval |
| `ENTITY_REUSE` | `entity_cluster` | `semantic_entity_id` restricted to IDs occurring at least twice in that world/seed | cluster |
| `OPERATOR_CLASS` | `operator_cluster` | no `operator_class` oracle field | `UNSCORED_INTERFACE_HOLD` |
| `RECORD_SCHEMA` | `record_schema_cluster` | `record_schema_id` | cluster |
| `REGISTER_LOCAL_VARIANT` | `register_variant_cluster` | `register_realization_id` | cluster |
| `SEMANTIC_CATEGORY` | `semantic_category_cluster` | `semantic_category` | GO (narrow): anonymous category partition only |
| `ACTUAL_LEXICAL_MEANING` | none | none | `UNSCORED_INTERFACE_HOLD`; requires external grounding |

No relation-type substring match, state-pair construction, `function_class`
alias, or lexical-identity proxy is permitted for a HOLD endpoint. Every HOLD
cell in both authentic and pair matrices is emitted as
`UNSCORED_INTERFACE_HOLD`, is excluded from thresholds and aggregation, and
receives no property decision. `ACTUAL_LEXICAL_MEANING` remains distinct from
lexical/entity identity: aligned anonymous clusters are not word meanings.

## Metrics

Cluster panels report NMI (arithmetic entropy normalization), adjusted Rand
index, and pair-F1 from contingency counts. Binary panels report balanced
accuracy, Matthews correlation, and positive-call FDR. `UNRESOLVED` binary
claims are treated as no positive call, while coverage is also reported.

Relation/reference coverage, top-1, distance, and singleton-hit diagnostics
are not produced: the review holds all three named endpoints because the
frozen interface lacks exact type mappings and genuine ranked predictions.
Their reserved metric columns remain `NA` so the compact matrix schema stays
stable.

Scope endpoint accuracy counts the two exact endpoints over twice the eligible
interval count. Exact-pair accuracy and inclusive interval IoU are also
reported. A missing or invalid prediction contributes zero. Pair endpoints and
intervals are eligible only if every truth endpoint is inside the selected
pair-view event universe; predictions leaving that universe are invalid.

Panel threshold PASS requires all frozen metrics for its kind:

- cluster: NMI >= .35, ARI >= .20, pair-F1 >= .35;
- binary: balanced accuracy >= .65, MCC >= .20, FDR <= .40;
- scope: coverage >= .25 and mean IoU >= .35.

No threshold is invented for diagnostic top-1, endpoint accuracy, target
distance, or cluster coverage.

## Aggregation and decision logic

Each held seed receives its complete conjunctive threshold verdict. A decoder
clears a world/property/representation only when all five seeds are reportable
and at least three of five complete seed verdicts pass; coordinate-wise seed
medians are diagnostics only. The "median decoder" rule is then a majority of
complete decoder passes: at least three of five decoders at the same property,
world, and representation. The revised validation PASS is responsible for the
frozen two-Sol/three-Luna provenance and requires at least two Luna passes for
any confirmatory promotion.

The interface freeze does not specify how six representations collapse to one
property decision. The pre-oracle operational rule here is: evaluate every
representation, then allow a world/property to clear if any single
representation clears. Cross-world general/family decisions must use one
common representation; representations cannot be mixed world by world to
reach a count threshold. The selected representation is the first frozen-order
representation with the largest cleared-world count.

The decision vocabulary is applied as follows.

1. `PROPERTY_IDENTIFIABLE_FROM_INTERNAL_STRUCTURE`: one representation clears
   at least seven of W01--W09 and its W10 false-discovery guard is <= .10.
2. `PROPERTY_ONLY_IDENTIFIABLE_UNDER_SPECIFIC_WORLD_FAMILIES`: otherwise, one
   representation clears two through six meaningful worlds (W01--W09), passes
   the same guard, and names the clear
   frozen broad-family names are reported.
3. `PROPERTY_CONFUSED_WITH_ORGANIC_CODEBOOK_EFFECTS` is withheld unless a
   predeclared paired equivalence analysis has 95% intervals wholly within the
   review's applicable .05 margins (.10 for MCC). A similar pass/fail result or
   nonsignificant difference is not equivalence.
4. Semantic interpretations beyond anonymous category partitions require
   external grounding. `ACTUAL_LEXICAL_MEANING` itself remains an interface
   HOLD rather than receiving a data-derived decision.

For a scoreable property satisfying none of these definitions, the output is
`NOT_IDENTIFIABLE_BY_THIS_PANEL`. HOLD properties have no decision. Organic
confusion is reported unscored until its full equivalence gate exists.

W10 false discoveries are explicit positive claims made where no corresponding
truth is eligible. For `SEMANTIC_CATEGORY`, every resolved W10 category claim
is conservatively a false semantic discovery because W10 is the frozen
semantics-light world. For other cluster properties, a resolved claim is false
only on truth-missing rows. Binary and endpoint FDRs use their natural positive
calls. The scorer emits a dedicated aggregate W10 table.

## Pair amendment and architecture scoring

Pair-view scoring is limited to lexical/entity identity, entity reuse,
record-schema/topology, and scope. Relation/reference properties remain HOLD
even in the pair view. It excludes
`INFERRED_COMPONENTS` entirely and marks all disallowed property/representation
cells `UNSCORED_PAIR_PROTOCOL_PROHIBITED`. Pair results do not enter the main
seven-world verdict; only the explicitly labeled W02/W03 confusion diagnostic
uses them.

World architecture clusters are compared with the ten frozen broad-family
labels using NMI/ARI/pair-F1. The four boolean world hypotheses are scored with
BA/MCC/FDR against pre-oracle public-assignment proxies: language-like =
W01/W07; notation-like = W04/W05/W08/W09; codebook-like = W02/W03/W06; and
semantics-light-like = W10. The first three are acknowledged coarse proxies,
not sealed oracle facts; the last is explicit in the interface freeze.

The six named method stress tests have no dedicated prediction fields in the
decoder contract. Each is emitted as
`UNSCORED_NO_EXPLICIT_DECODER_PREDICTIONS`; the scorer does not reverse-engineer
a stress-test claim from ordinary clusters.

## Compact outputs

The output directory contains `panel_metrics.tsv`, `pair_panel_metrics.tsv`,
`world_representation_metrics.tsv`, `property_decisions.tsv`,
`w10_false_discoveries.tsv`, `architecture_metrics.tsv`,
`method_stress_tests.tsv`, and `summary.json`. TSVs contain counts and aggregate
metrics only. The JSON records input hashes, decision summaries, and the
ambiguity notes above; no event ID, oracle label, or joined record is written.
