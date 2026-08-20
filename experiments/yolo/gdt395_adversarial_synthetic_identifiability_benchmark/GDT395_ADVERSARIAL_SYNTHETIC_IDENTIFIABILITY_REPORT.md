# GDT395 adversarial synthetic writing-system identifiability benchmark

Status: `CURRENT_VMANUS_METHOD_FALSE_NEGATIVE_ON_POSITIVE_CONTROLS`

GDT395 does not validate a Voynich semantic decoder. It instead shows that the
current blind-decoder panel and output interface are not yet adequate to decide
most of the requested identifiability questions. No Voynich corpus was scored,
and GDT395 accessed neither `f84` nor `f84r`.

## Validated execution

Ten independently designed synthetic worlds were generated at 20 seeds each.
Five oracle-blind decoders (two Sol, three Luna) produced 2,150 frozen claim
files before any held oracle was opened. The final score uses held seeds
15--19 only and contains 422,697 held events.

The scorer/validator initially disagreed on their aggregate contract. V5
conformed the producer to the independently published pre-oracle validation
design; the eight earlier V4 outputs were hash-bound first. The independent V3
validator then passed all 14 checks and reproduced:

- 25,500 authentic panel rows;
- 10,200 pair-panel HOLD rows;
- 1,020 world/representation rows;
- 42 W10 diagnostics;
- 17 property decisions;
- 25 architecture diagnostics; and
- six explicit method-stress HOLDs.

This correction changed diagnostic serialization/aggregation, not the frozen
blind claims or underlying contingency counts. The seven scored decisions
remain `EXPLORATORY_UNCONFIRMED`; the other ten are
`UNSCORED_INTERFACE_HOLD`. Record-block nulls and the frozen 9,999-null family
were not available in the accepted interface.

## Strict identifiability matrix

| Hidden property | Strict result | Strongest exploratory recovery |
|---|---|---|
| Lexical identity | No world clears the 3-decoder/2-Luna gate | D02 recovers FULL_GROUP identity on 8/9 meaningful worlds, 5/5 held seeds each; D01 does so on 5/9 |
| Semantic-entity co-identity | No world clears | D02 HOST_LIKE clears W02/W03/W04/W05/W08, 5/5 seeds |
| Historical-stem shared partition | No world clears; genealogy itself was not tested | D02 HOST_LIKE clears W02/W03/W04/W05/W08, 5/5 seeds |
| Function class | No signal | Zero seed passes in every representation/decoder |
| Recurring entity reuse | No world clears | Mirrors D02 entity co-identity on five worlds; singleton truth is excluded |
| Register-local realization | No world clears | D01 clears W01/W02/W03/W05 and semantics-light W10 across all six representations |
| Semantic-category partition | No signal | Zero seed passes in every representation/decoder |
| Productive morphology | Interface HOLD | Decoder outputs were opaque component IDs, not Boolean productive-status claims |
| Fossilized morphology | Interface HOLD | Same interface mismatch |
| Coordinator / alternative relations | Interface HOLD | No frozen typed, ranked relation-target output |
| Reference/anaphora | Interface HOLD | No direct oracle-reference target output |
| Temporal gate / operator class | Interface HOLD | No matching claim/truth channel |
| Scope | Interface HOLD | No validated event-order contract in scorer input |
| Record schema | Interface HOLD | `record_id` absent from accepted scorer input |
| Actual lexical meaning | Interface HOLD | No gloss/meaning claim channel; external grounding remains necessary |

The full row-level matrix is in `panel_metrics.tsv`; all pair properties are
intentionally unscored in `pair_panel_metrics.tsv`.

## Real positive-control recovery that the panel gate suppresses

The strict all-panel result hides genuine decoder-specific recovery:

| Endpoint / representation / decoder | Held-world recovery | Typical held medians |
|---|---:|---|
| Lexical identity / FULL_GROUP / D02 | 8 meaningful worlds, all 5 seeds | NMI .77--.93; ARI .45--.86; pair-F1 .46--.86 |
| Lexical identity / FULL_GROUP / D01 | 5 meaningful worlds, all 5 seeds | NMI .78--.86; ARI .35--.64; pair-F1 .36--.64 |
| Entity identity / HOST_LIKE / D02 | 5 worlds, all 5 seeds | NMI .70--.85; ARI .35--.66; pair-F1 .39--.68 |
| Shared stem partition / HOST_LIKE / D02 | 5 worlds, all 5 seeds | NMI .69--.85; ARI .35--.66; pair-F1 .39--.68 |
| Register realization / FULL_GROUP / D01 | 4 meaningful worlds plus W10, all 5 seeds | NMI .69--1.00; ARI .47--1.00; pair-F1 .56--1.00 |

None of the three Luna decoders produces a single seed pass on any of the seven
scoreable endpoints. Their common failure mode is informative: moderate NMI
can coexist with ARI and pair-F1 near zero when almost every event is assigned
its own cluster. The conjunctive gate correctly rejects that over-partitioning,
but requiring two Luna confirmations also rejects the strong Sol positive
controls. The benchmark therefore diagnoses a decoder-panel false negative,
not absence of recoverable structure.

## Adversarial and semantics-light controls

The matched W02/W03 and W09/W10 pair packets cannot adjudicate organic versus
engineered coding because all 10,200 pair endpoints are protocol HOLD without
record identity. This leaves the central adversarial pair comparison unresolved.

The event-level W10 false-co-clustering diagnostics are zero for all scoreable
properties and representations. That means the decoders did not merge known
different W10 items; it does not mean they recognized a semantics-light world.
The direct world-level `SEMANTICS_LIGHT_LIKE` diagnostic fails: balanced
accuracy is .5 for D01/D02/D03 and 0 with MCC -1/FDR 1 for D04/D05. GDT395
therefore neither demonstrates nor excludes a semantic false-positive tendency.

## Representation lesson

No single observation level is universally homologous to a word or semantic
unit:

- FULL_GROUP is the useful level for recoverable lexical equality;
- HOST_LIKE is the useful level for the one-decoder entity/stem signal;
- register realization is recoverable from several levels in one graph
  decoder; and
- function class and semantic category are not recovered at any level.

This supports multi-resolution analysis, but not semantic promotion. It also
shows why an exact composite state cannot be privileged as a universal word.

## Method decisions

| Decision | GDT395 outcome |
|---|---|
| `PROPERTY_IDENTIFIABLE_FROM_INTERNAL_STRUCTURE` | Not established for any property under the full panel gate |
| `PROPERTY_ONLY_IDENTIFIABLE_UNDER_SPECIFIC_WORLD_FAMILIES` | Exploratory only for lexical/entity/stem/register partitions and particular decoders/representations |
| `PROPERTY_CONFUSED_WITH_ORGANIC_CODEBOOK_EFFECTS` | Unresolved because the pair interface is HOLD |
| `PROPERTY_REQUIRES_EXTERNAL_GROUNDING` | Actual lexical meaning, relation meaning, and semantic labels remain outside the scored interface |
| `CURRENT_VMANUS_METHOD_FALSE_NEGATIVE_ON_POSITIVE_CONTROLS` | Yes: strong 5/5-seed Sol recoveries are eliminated by zero Luna replication |
| `CURRENT_VMANUS_METHOD_FALSE_POSITIVE_ON_SEMANTICS_LIGHT_CONTROLS` | Unresolved; W10 architecture recognition itself failed |
| `ORGANIC_STEM_ANCESTRY_RECOVERABLE` | Not robustly established; one decoder recovers only a shared-stem partition in five worlds |
| `ORGANIC_STEM_ANCESTRY_NOT_IDENTIFIABLE_FROM_SURFACE` | Also not established; the D02 signal prevents that stronger negative conclusion |

## Consequence for the Voynich route

Do not create a Voynich GDT396 from this benchmark. The next work should repair
the instrument on new synthetic held seeds before any manuscript scoring:

1. add observation-side `record_id` and typed/ranked relation predictions so
   pair, reference, scope, and record-schema endpoints become scoreable;
2. replace or strengthen the three singleton-producing replication decoders;
3. expose explicit current/fossil morphology claim interfaces without giving
   decoders oracle labels;
4. retain the adversarial organic/engineered and semantics-light worlds; and
5. require replication on untouched generated corpora after the repaired
   decoder set is frozen.

The highest-value result is therefore methodological: some anonymous identity
partitions are plainly recoverable in synthetic Voynich-like systems, but the
current VManus confirmation instrument cannot distinguish that success from a
panel-wide failure. It must be repaired before further internal Voynich
semantic inference.
