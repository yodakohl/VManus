# GDT395 independent identifiability validation design

Status: `FROZEN_INDEPENDENT_VALIDATOR_V1_BEFORE_ORACLE_ACCESS`

`src/validate_identifiability.py` is an independent, non-importing validator
for the V2 scorer. It duplicates the public claim/oracle field tuples and
metric formulae. It does not import or inspect a decoder, generator, scorer,
codebook, genealogy, observation packet, Voynich/f84 source, or project
history. Development verification is restricted to source compilation and the
built-in fabricated self-test.

## Invocation

```text
python src/validate_identifiability.py \
  --root REPOSITORY_ROOT \
  --claims-freeze CLAIMS_FREEZE_V2.json \
  --claims-validation CLAIMS_VALIDATION_V2.json \
  --corpus-manifest artifacts/gdt395_corpus_manifest.tsv \
  --oracle-root ORACLE_CORPUS_ROOT \
  --scorer-output-dir SCORE_OUTPUT \
  --validation-output OUTSIDE_SCORE_OUTPUT/independent_validation.json
```

The validation output is one-shot and must be outside the scorer directory.
Failure output contains only a stable gate code. It never echoes a path, event
ID, claim label, or oracle value.

## Authentication order

1. Validate canonical-JSON content hashes, schemas, PASS statuses, genuine
   Boolean checks, blind/pre-oracle/Voynich/f84 seals, the single validation to
   freeze binding, the five-decoder implementation map, and the exact 2-Sol /
   3-Luna split.
2. Resolve and SHA-256-check all three disjoint claim roles from the freeze.
   Validate the full authentic, pair, and world-claim schemas and panel shapes.
   No oracle path has yet been opened or hashed.
3. Require the public corpus manifest to occur exactly once in the freeze's
   implementation bindings and verify its exact eight-column, 10-world x
   20-seed schema.
4. For held seeds 15--19 only, require the exact manifest path
   `sealed/Wxx/seed_SS_oracle.tsv.gz`, hash all 50 files against the manifest,
   and only then parse their exact `ORACLE_FIELDS` rows.
5. Require authentic event-set equality with the oracle and pair event-set
   subset relations before computing a metric.

All bound paths are portable repository-relative paths without symlinks or
`..`. Oracle paths are resolved beneath the explicit oracle root.

## Frozen endpoints and metrics

Exactly seven authentic endpoints are recomputed as clustering partitions:

- `LEXICAL_IDENTITY`: `lexical_cluster` / `lexical_id`
- `SEMANTIC_ENTITY_IDENTITY`: `entity_cluster` / `semantic_entity_id`
- `HISTORICAL_STEM_ANCESTRY`: `stem_cluster` / `historical_stem_id`, shared-ID
  partition only
- `FUNCTION_CLASS`: `function_cluster` / `function_class`
- `ENTITY_REUSE`: `entity_cluster` / `semantic_entity_id`, after excluding
  oracle IDs that occur only once in that held world/seed
- `REGISTER_LOCAL_VARIANT`: `register_variant_cluster` /
  `register_realization_id`, authentic view only
- `SEMANTIC_CATEGORY`: `semantic_category_cluster` / `semantic_category`,
  anonymous partition only

`UNRESOLVED` is a private per-event singleton. NMI uses
`2I/(H_truth+H_claim)`, ARI is Hubert-Arabie, and pair-F1 is computed from
contingency counts. A seed has capacity only with at least two truth classes,
one same-truth pair, and one different-truth pair. The complete seed gate is
NMI >= .35, ARI >= .20, and pair-F1 >= .35. `primary_index` is the minimum of
the three threshold ratios and is diagnostic only.

The other ten properties are exact `UNSCORED_INTERFACE_HOLD` rows with all
metric cells `NA`. Every property in every pair panel is
`UNSCORED_PAIR_INTERFACE_HOLD`; no pair claim is used for a scientific metric.

A decoder clears after at least three complete seed passes. A world clears
after at least three decoder clears, including at least two Luna decoders.
World/representation diagnostics are coordinate-wise medians of decoder
medians and never manufacture the Boolean clear.

For every scoreable W10 property/representation, the validator takes the
median across five decoders within each seed and enumerates all 3,125 ordered
five-seed bootstrap samples. `false_positive_upper95` is the nearest-rank 95th
percentile of resampled medians. The point guard is `upper95 <= .10`;
confirmatory guard and promotions remain false because record-block nulls and
9,999 frozen permutations are unavailable.

The exploratory representation for `property_decisions.tsv` is selected
deterministically by, in order: W10 point-guard pass, number of meaningful
world clears, smaller W10 upper bound, then frozen representation order.
Decisions remain `EXPLORATORY_UNCONFIRMED`; raw and Holm p-values are `NA`.

## Architecture diagnostics

The reviewed inputs contain no frozen broad-family map or Boolean truth maps
for language/notation/codebook proxies. Those architecture cells must be
numerically `NA` with an explicit unscored truth basis. Only
`semantics_light_like` has direct truth: W10 true and W01--W09 false. Boolean,
finite [0,1] (threshold .5), and HIGH/LOW predictions are accepted; MEDIUM and
`UNRESOLVED` abstain. Abstentions are completed adversarially before BA/MCC/FDR
are recomputed. These diagnostics cannot substitute for an event property.

## Exact scorer artifacts

The scorer directory contains exactly these eight regular, non-symlink files:

- `panel_metrics.tsv`
- `pair_panel_metrics.tsv`
- `world_representation_metrics.tsv`
- `property_decisions.tsv`
- `w10_false_discoveries.tsv`
- `architecture_metrics.tsv`
- `method_stress_tests.tsv`
- `summary.json`

The exact columns are duplicated as constants in the validator from the
frozen schema. Rows are keyed by their full aggregate identity, duplicate and
extra rows fail, required rows cannot disappear, nonapplicable metrics must be
literal `NA`, counts compare exactly, and finite metrics compare to absolute
`1e-12` / relative `1e-10` tolerance.

The summary has frozen `schema: GDT395_IDENTIFIABILITY_SCORE_SUMMARY_V1`,
`status: PASS`, exactly the frozen keys, `contains_event_rows: false`,
`voynich_rows: 0`, `confirmatory_promotions_enabled: false`, compact aggregate
input hashes, the exact endpoint qualifications/HOLD list, and projections of
the recomputed decisions. Exact aggregate-only schemas prevent event-ID,
oracle-label, joined-row, visible-text, record, and local-path leakage.

On PASS, the validator writes a compact canonical-content-hashed artifact
containing only stable input/output SHA-256 values, output row counts, Boolean
checks, and total oracle rows read. A mismatch at any authenticated,
scientific, aggregation, HOLD, W10, architecture, output-content, or leakage
gate fails validation.
