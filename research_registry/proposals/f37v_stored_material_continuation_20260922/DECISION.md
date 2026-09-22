# IDEA000522 — pre-body decision and capacity freeze

This note freezes the nominated whole continuation before target word retrieval. The nomination body flag was `target_body_opened_for_this_nomination=false`; this freeze records metadata only. After this note, the exact admitted cache may be opened for the selected f37v.8–13 records. No third paragraph, RF whole unit, image, reserve, contact or simulator is admitted.

## Target metadata frozen before body retrieval

- Cache: `experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json`
- SHA256: `667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b`; bytes: `2709048`
- Allowlist: `experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv`, row 83, page f37v; page hash `f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`
- Target ID: `f37v|f37v.8-f37v.13`; loci: `f37v.8` through `f37v.13`; first line `start=true`, last line `end=true`.
- Reader coverage: ZL3b 25 groups; IT2a 23 groups. RF has no nominated whole paragraph.

### ZL3b — 25 groups, 6 lines
| locus | row | groups | start | end | anchor_eligible | offset |
|---|---:|---:|---|---|---|---:|
| f37v.8 | 892 | 4 | true | false | true | 0 |
| f37v.9 | 893 | 5 | false | false | true | 4 |
| f37v.10 | 894 | 6 | false | false | false | 9 |
| f37v.11 | 895 | 4 | false | false | true | 15 |
| f37v.12 | 896 | 5 | false | false | false | 19 |
| f37v.13 | 897 | 1 | false | true | false | 24 |

### IT2a — 23 groups, 6 lines
| locus | row | groups | start | end | anchor_eligible | offset |
|---|---:|---:|---|---|---|---:|
| f37v.8 | 888 | 4 | true | false | true | 0 |
| f37v.9 | 889 | 5 | false | false | true | 4 |
| f37v.10 | 890 | 5 | false | false | true | 9 |
| f37v.11 | 891 | 4 | false | false | true | 14 |
| f37v.12 | 892 | 4 | false | false | true | 18 |
| f37v.13 | 893 | 1 | false | true | false | 22 |

## Frozen inherited lexicon and source family

The following 65 old entries are copied exactly from RAW512 `frozen_parent.all_65_lexical_entries`; all remain fixed. The separate 15 alternate reader assumptions are listed afterward. RAW512 retained 18 old productions, 20 new exact P1 entries, and `dchor=WORK_INTO_PASTE` from the closed f4r offer; those values/effects remain unchanged. `INHERITED_FREEZE.json` is the machine-readable copy.

### All 65 old entries

| form | value | type |
|---|---|---|
| `fcho` | `ACQUIRE` | `InputIntroduction` |
| `kshy` | `ROOT_MATERIAL` | `MaterialKind` |
| `otor` | `FRESH` | `MaterialProperty` |
| `sheol` | `DRY` | `Operation` |
| `ocphal` | `CRUSH` | `Operation` |
| `opsheas` | `FOR_OUTPUT` | `ProspectiveGoalBinder` |
| `cthodaiin` | `POWDER_MASS_Q` | `MeasuredMaterialNP` |
| `oty` | `DRY_STATE` | `MaterialProperty` |
| `okaiin` | `RINSE` | `OperationWithSupply` |
| `sho` | `WATER` | `ExternalSupplyKind` |
| `tshaiin` | `UNTIL` | `OutputConditionBinder` |
| `chkaiin` | `CLEAN` | `MaterialProperty` |
| `sh` | `THEN` | `Sequence` |
| `cthey` | `SPREAD` | `Operation` |
| `cthody` | `THINLY` | `Manner` |
| `cthy` | `PLANT_MATERIAL` | `MaterialSupertypeReference` |
| `s` | `EVENLY` | `Manner` |
| `totchy` | `DRY` | `Operation` |
| `keor` | `IN_SUN` | `LocationAdjunct` |
| `chy` | `GRIND` | `Operation` |
| `ky` | `COARSELY` | `Manner` |
| `qotaiin` | `SEPARATE_BY_GRADE` | `PartitionOperation` |
| `qotchol` | `COARSE_PART` | `PartitionPartReference` |
| `ty` | `FROM` | `PartitionContrast` |
| `ctheey` | `FINE_PART` | `PartitionPartReference` |
| `otaiin` | `WITH_SIEVE` | `ToolAdjunct` |
| `shol` | `KEEP` | `PreservationOperation` |
| `chol` | `FINE` | `MaterialProperty` |
| `tchol` | `COARSE` | `MaterialProperty` |
| `chcthy` | `WITH_CLOTH` | `ToolAdjunct` |
| `otyky` | `COVER` | `Operation` |
| `shey` | `THEN` | `Sequence` |
| `yteol` | `STORE_SEPARATELY` | `PreservationOperation` |
| `shody` | `RESIDUE` | `PartitionPartReference` |
| `ykeey` | `RETRIEVE` | `ExistingMaterialOperation` |
| `chor` | `POWDER` | `MaterialKindReference` |
| `sheey` | `SIEVE` | `PartitionOperation` |
| `ysheol` | `UNTIL` | `OutputConditionBinder` |
| `daiin` | `MASS_UNIT_Q` | `MassUnitToken` |
| `ksho` | `ROOT_MATERIAL` | `MaterialKind` |
| `cpho[s:r]` | `CRUSH` | `UnresolvedReadingWithSameHypothesizedOperation` |
| `she` | `DRY` | `Operation` |
| `sheaiin` | `OVERNIGHT` | `DurationAdjunct` |
| `otshcho` | `IN_SHADE` | `LocationAdjunct` |
| `r` | `THEN` | `Sequence` |
| `dain` | `THOROUGHLY` | `Manner` |
| `shckhy` | `MIX` | `Operation` |
| `odan` | `PREPARED_BULK` | `ExistingMaterialReference` |
| `otchol` | `COARSE_GRIST` | `MaterialKindReference` |
| `ctho` | `POWDER` | `MaterialKindReference` |
| `otchy` | `LIFT_OUT` | `PartitionFocusOperation` |
| `d` | `DEFINITE` | `DefiniteReference` |
| `shan` | `COARSE_FRACTION` | `PartitionPartReference` |
| `qotchy` | `SORT` | `PartitionOperation` |
| `cfhy` | `WITH_SIEVE` | `ToolAdjunct` |
| `skey` | `KEEP` | `PreservationOperation` |
| `chocthy` | `FIBRES` | `PartitionProductKind` |
| `cthaiin` | `GRANULES` | `PartitionProductKind` |
| `keol` | `OIL` | `ExternalSupplyKind` |
| `cpho` | `KNEAD` | `JointInputTransformation` |
| `l` | `TO_RESULT` | `ResultBinder` |
| `cthol` | `PASTE` | `TransformationProductKind` |
| `da` | `ONE` | `PortionCount` |
| `ar` | `PORTION` | `CountUnit` |
| `ol` | `WITH_MEDIUM` | `ExistingMediumBinder` |

### Fifteen alternate assumptions retained as alternatives

| form | value | type |
|---|---|---|
| `fchokshy` | `ACQUIRE(ROOT_MATERIAL)` | `` |
| `cheol` | `` | `` |
| `opcheas` | `` | `` |
| `shcthey` | `THEN(SPREAD)` | `` |
| `ykeea` | `` | `` |
| `ykee@222;` | `` | `` |
| `@222;sheol` | `` | `` |
| `chyky` | `GRIND(COARSELY)` | `` |
| `cphos` | `` | `` |
| `cphor` | `` | `` |
| `otshchor` | `IN_SHADE;THEN` | `` |
| `daii` | `` | `` |
| `shar` | `` | `` |
| `@152;` | `` | `` |
| `cphol` | `KNEAD_TO_RESULT` | `` |

## Capacity and stop rule

- Maximum 12 new exact whole values; maximum 3 new reusable productions; maximum 4 additional nondefault material/scope bindings; aliases and packing rules remain zero.
- Preserve both readers and every inherited value. If either reader cannot be accounted for within those caps, stop with the complete raw alignment and explicit incompleteness. Do not add a paragraph or enlarge a quota.
- Preserve the old f37v P1 lineage: one plant-solid mass Q, fine and uncomminuted/coarse state as inherited, paste carrier after `dchor`, no automatic free powder stock.
- The actual continuation must distinguish a stored-material withdrawal, a fresh-input constructor, and a type description. Repeated material nouns do not create stock.

## Known counterexamples and required debts

- RAW512 did not establish a sufficient workable hydration ratio for paste formation; h>0 is not enough.
- The Boolean `DRY_STATE` postcondition remains unresolved; the continuation may not set it silently.
- ROOT_VISIBLE and LEAF_VISIBLE updates under CRUSH, GRIND, and WORK_INTO_PASTE are unspecified; no intact-organ endpoint may be assumed.
- The f4r `dchor` offer remains a separate retained conditional entry; exact overlap must be reported, not repurposed.
- Four separated Q occurrences in RAW512 are not automatically four independent supplies; each continuation use must debit the existing stock.
- `NEW_RECIPE` requires an actual input constructor with initial quantity/state. `TYPE_DESCRIPTION` permits assertions without withdrawal only under one reusable assertion construction.

## Planned post-freeze work

Read only the two exact nominated cache records through the admitted paragraph cache/guard. Preserve whole forms, spaces, source IDs, line order, reader differences, and start/end metadata. Build a source receipt, all-groups mapping, inherited/new lexical inventory, material-state ledger, continuation and fresh-stock rival constructions, written consequences, assumptions, and precise incompleteness. No simulation, numeric result, image access, registry/ledger/global-route edit, or source-only audit.
