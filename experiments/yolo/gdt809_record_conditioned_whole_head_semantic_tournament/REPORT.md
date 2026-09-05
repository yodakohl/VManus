# GDT809 — repaired comparison and four joint paragraph readings

Status: COMPLETE_REPAIR_AND_JOINT_EXPLORATION__MEANINGS_UNRESOLVED

## Practical result

The unfinished comparison is repaired. Four complete source paragraphs now
have two token-aligned, concrete working readings using the same 16-entry
dictionary. The dictionary offers hypotheses at 46 of 145 token positions;
99 positions remain visibly unresolved. This is not a complete translation
and 31.7% hypothesis coverage is not an accuracy estimate.

Read [the complete paragraphs and both German readings](artifacts/JOINT_COMPETING_PARAGRAPH_READINGS.md).
The [small dictionary](artifacts/JOINT_COMMON_DICTIONARY.tsv) records every
meaning's confidence, positive evidence, objections and origin. It does not
replace or erase the larger inherited renderer.

The most useful concrete contrast is still:

| Exact source span | Descriptive working model D | Recipe working model R |
|---|---|---|
| `chor chol daiin` | flower head, dry in the third degree? | dried flowers, three portions? |
| `cthy oltchy` | leaf/herb material, cold and dry? | leaf/herb ingredient, cold and dry? |
| `otshy okaiin` | cold-moist preparation? | cold-moist preparation? |

These meanings are explicit assumptions, including the numbers. The first
span was already analyzed in GDT629; redisplaying it is not a discovery.
The new contribution is a common-dictionary comparison of its complete
paragraphs with the awkward repetitions and unknown neighbours retained.

GDT629 preferred the degree reading from a broader inherited form grid.
That remains a working prior; this small paragraph comparison neither
independently confirms it nor erases it. The recipe reading remains live.

## What the formal computation actually found

The builder reconstructs the inherited 179 selectors, 4,137 lines and 32,339
tokens, with 665 strict paragraphs. It retains 35 exact heads, 1,032 stable
occurrences, 211 occurrence edges, 209 distinct head/pivot links and 189
unique-head windows. There are 795 strict external head occurrences.

Two associations pass the declared contextual relation criteria:

| Head / axis | Base : expanded | Contact folios | Rotation rank | External record direction | ED1 sensitivity |
|---|---:|---:|---:|---|---|
| `cthy` / L | 12 : 0 | 11 | 4/25 | base | retained: 13 : 0 on 12 folios, rank 4/25 |
| `sheo` / DY | 1 : 3 | 4 | 3/25 | expanded | head excluded by the declared ED1 mask |

Removing each contact folio preserves the observed direction in both cases.
The ED1 `sheo` exclusion is not an observed reversal or a semantic rejection.
These are exploratory record/form associations, not water, leaf or operation
identifications, and their ranks are not multiple-testing-adjusted discovery
probabilities.

The external model is not an unseen-folio semantic test. For `cthy`, all
35 external folios (51 occurrences) also occur in its record-model training
population; for `sheo`, 13 of 19 external folios (14 of 21 occurrences)
overlap training. Contact folios are excluded, but training/external folios
are not mutually disjoint. The computation therefore reports record
compatibility and exposes the overlap rather than claiming independent
identity prediction.

## What the repair changes

The previous unfinished design favoured leaf by treating broad botanical
page context as a leaf-specific word-owner association. It also omitted
herba, mixed inherited semantic priors into evidence scores, and lacked
producers for several candidate-specific distinctions.

There are now 20 profiles and 700 head/candidate rows. For `cthy`, folium,
herba and an unnamed botanical head each receive the same contextual score
11. The inherited-prior score 2 is separate and adds no discriminatory
credit. Leaf no longer wins merely because leaves are drawn on a plant page.

All 735 candidate-specific requirement rows are UNOBSERVED with the current
inputs. That is a statement about this comparison's missing measurements,
not 735 negative findings or a rejection of every proposed meaning.
Unmeasured requirements do not count as counterevidence. Ties share rank,
singleton family margins are NA, and automatic literal promotion is disabled.
Water, wine, oil, salt and other candidates remain hypotheses, not successful
decodings just because they appear in a ranked list.

## The paragraph evidence that must survive interpretation

All four paragraphs are complete under the cached boundary flags:
f17r.4–6, f21r.8–12, f32v.7–11 and f29v.1–4. Their 17 lines contain nine
declared pattern occurrences; eight patterns are supported by all three
alternative readings of this one manuscript.

- `cthy chor shor` permits a plant-part or ingredient-list hypothesis. It does
  not identify the three organs or settle flower versus seed/fruit direction.
- `chor chol daiin` appears at both known locations in all three readings.
  Both descriptive degree syntax and recipe amount syntax remain possible.
- `daiin daiin` and two `chol chol` occurrences are left repeated. One
  `chol chol` occurrence has only two-reader support. Neither model may
  silently turn the repeats into one intensified state, six portions, or an
  invented second operation.
- `chocthy daiin cthaiin daiin` supplies two adjacent head/value-like fields
  in all three readings. The head identities and value axis remain open.
- `shol chol shol` does not by itself establish a wet-dry-wet treatment.
  The interpreted qualities or states still need subjects and scope.
- Repeated `okaiin` on f29v.4 establishes repeated spelling, not necessarily
  one preparation, the same batch, or a directional process.

At f32v.8, ZL3b/IT2a have `daiin [ctho daiin] qotaiin`, while RF1b has
`daiin [cthodaiin] qotaiin`. The matched inner character sequence motivates
a local word-boundary alternative. It does not identify `ctho`, export a
`cth` root, or establish that spaces are generally optional.

Historical comparison adds a useful distinction: dry as a constitutional
quality, dried as a material state, and an imperative to dry are different
claims. The primary comparators and their dates/access limits are documented
in [the historical review](src/HISTORICAL_PASSAGE_REVIEW.md). Historical
compatibility is not a Voynich-to-Latin dictionary match.

## Continuity and next useful work

The route-check query `daiin daiin whole paragraph scope degree quantity
repeated value attachment` returned GDT764, GDT686, GDT626, GDT630 and
other predecessors. The primary GDT686/GDT764/GDT629 reports confirm that
value-series repetition, local degree-versus-amount dispatch and the two
`chor chol daiin` clauses were already investigated. Do not restart those
as a fresh statistical route or claim that this pass first noticed them.

Keep the descriptive interpretation as a provisional presentation where
the inherited quality analysis applies, with recipe/state/amount rivals
beside it. The unresolved work is assigning subjects, scope and connective
roles to the visible neighbouring text so one small dictionary accounts for
complete passages. Existing local dispatches are inputs to that work, not
independent support for their own glosses. A new run of the same contextual
candidate ranking cannot fill the unobserved identity requirements.

In particular, do not choose an unexplained neighbour's meaning separately
at each occurrence merely to make each line read smoothly. Any proposed
attachment must retain the written repetitions and say which observable
context makes it apply. Further implementation needs a genuinely distinct
proposal beyond the already completed GDT686/GDT764 local-head dispatch.

## Reproduction and checks

Registration and sources were published in commit `e6ac61f1` before the
official build. The design openly disclosed inherited capacity and known
paragraph selection. No fresh manuscript page or image was opened; the
existing 30-page visual spine was reused. f84/f84r stayed forbidden.

```sh
python3 experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament/src/run_experiment.py
python3 experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament/src/validate_joint.py --no-write
python3 experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament/src/validate.py --no-write
```

The independent validator passes 15 reconstruction/contract groups and
invokes 61 joint paragraph checks. These check source conservation, counts,
models and provenance, not the truth of a translation. GDT388 intake runs
on both new packets: two formal head relations and nine paragraph relations.
All are explicitly unsealed text-only evidence: zero eligible edges and
`score_ready=false`. They do not gain visual-owner evidence credit.

The repository-wide check still reports the seven pre-existing unbound
GDT600 reproducibility files. They are unrelated, untouched and not included
in publication. GDT809's manifest and staged privacy/scope checks pass.
