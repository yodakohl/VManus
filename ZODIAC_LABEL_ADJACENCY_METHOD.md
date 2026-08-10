# ZLA001 — zodiac label cyclic adjacency method

Status: **REGISTERED UNSCORED**. No label-adjacency statistic has been
computed. The public label strings were visible during source-format and
provenance checks, but no ordered similarity, target effect, candidate family,
or subgroup was calculated before this registration.

## Question and novelty

Do physically adjacent zodiac `L` records share more partial construction
structure than nonadjacent records in the same human-catalogued ring?

This is not an object-ownership test. It uses only the public clockwise Grove
order of labels within a named ring. It does not assign any label to the
closest nymph, star, barrel, degree, or other object. It is also distinct from:

- CRE001, which tested same-page `C`-to-`L` construction coverage without
  using order inside `L`;
- the duplicate Aries/Taurus and opposition tests, which compared whole-page
  cross-role profiles;
- the stopped universal thirty-position test, which required an unsupported
  phase and continuation across unequal rings; and
- CC003/F69C001, which tested `C` text or one f69 fragment rather than the
  public zodiac label cycles.

The frozen geometry is the independently validated ZLA001 capacity panel:
21 complete rings, 235 slots, 11 pages, and four physical folios. Every slot
has an explicit human Grove key, a primary one-to-one current-locus mapping,
and all three manual readings. No ring is concatenated to another.

## Inputs and isolation

Development and target code may read only:

1. `experiments/semantic_assumptions/results/zodiac_label_cycle_capacity.tsv`;
2. `experiments/semantic_assumptions/results/zodiac_label_cycle_capacity.json`;
3. `experiments/semantic_assumptions/results/zodiac_label_cycle_capacity_validation.json`;
4. `experiments/semantic_assumptions/results/source_sta_group_alignment.tsv`;
5. `experiments/semantic_assumptions/results/source_sta_group_alignment.json`;
6. `experiments/semantic_assumptions/results/source_sta_group_alignment_validation.json`;
7. this method, the scientific core, control runner, independent control
   validator, one-shot target runner, and later freeze manifest.

No parser roots, EVA spelling, object attributes, pixels, OCR, automated
vision, cached embeddings, historical plaintext, or image proximity enters.
ZL3b, IT2a, and RF1b remain linked alternate readings and are never treated as
independent samples.

Before the first target run, a public freeze must bind every allowed input and
scientific file and prove all target/result artifacts absent. Target code may
emit only aggregate effects, support, deletions, counts, hashes, and gates. It
must not emit individual label sequences, family identities, pair scores,
favorable rings, or favorable positions.

## Frozen representation

For each slot and reading, order its manual source groups by
`source_group_index` and read only `primary_sta_families`.

- `FAMILY_ONLY`: concatenate the family tokens from all source groups.
- `BOUNDARY_AWARE`: concatenate the same tokens while inserting one distinct
  `|` token between consecutive source groups.

Every whole label remains intact. Source spaces are therefore tested as a
second structural view, not assumed to be European words. No family or token
is selected from the target.

For two nonempty token sequences `a,b`, let

```
edit_similarity(a,b) = 1 - levenshtein(a,b) / max(len(a),len(b))
length_ceiling(a,b)  = min(len(a),len(b)) / max(len(a),len(b))
pair_score(a,b)      = edit_similarity(a,b) - length_ceiling(a,b)
```

`pair_score` lies in `[-1,0]`; higher is more similar after subtracting the
entire similarity attainable from length alone. Pure repeated-placeholder
length strings score exactly zero for every pair. Exact records also score
zero and remain legitimate evidence in the primary view.

The mandatory `NO_EXACT_RECORD` sensitivity omits a pair in a reading/view
when its two complete `BOUNDARY_AWARE` token sequences are identical. It is
never used to select rings or target families. A ring-distance cell is
eligible in this sensitivity only with at least three retained pairs.

## Physical cyclic statistic

For a ring of size `n`, undirected distance `d` ranges from 1 through
`floor(n/2)`. The ring score is the mean `pair_score` over
`i` versus `(i+d) mod n`; the even-ring diameter may appear twice but has the
same mean either way. Physical adjacency is exactly `d=1`. Null distances are
exactly `2..floor(n/2)`. This removes any start, clockwise/anticlockwise
direction, rotation, or reflection choice.

Aggregation is fixed:

1. mean the two representation views for the composite;
2. equal-weight eligible rings within page;
3. equal-weight pages within physical folio;
4. equal-weight the four physical folios.

The two component views are retained separately. No result is weighted by the
number or length of labels.

## Frozen null and joint inference

Each null world chooses one allowed nonadjacent distance for every ring and
uses the same distance vector in all readings and views. Let the product of
per-ring alternative counts be `K`. Generate exactly 65,536 unique mixed-radix
ranks by

```
rank_i = (start + i * step) mod K,  i=0..65535
```

where `start` and the initial step candidate are SHA-256 integers under the
domain `ZLA001|NONADJACENT_DISTANCE_ORBIT|v1`; increase the step until it is
coprime with `K`. Decode each rank in canonical `ring_id` order. The runner and
validator must store the exact `<u2`, C-order assignment-matrix SHA-256 and
must reject duplicate rows.

For each reading, center and scale the composite null scores with population
SD. Compute the observed z and all null z values. The joint statistic is the
minimum z across the three readings. The one-sided plus-one Monte Carlo p is

```
(1 + count(null_joint_z >= observed_joint_z - 1e-15)) / 65537.
```

The material raw effect is the minimum across readings of observed composite
score minus that reading's null mean.

## Target gates fixed before access

Confirmation requires every gate:

1. all frozen hashes, schemas, 21 rings, 235 unique loci, 11 pages, four
   folios, reading links, target absence, and no-forbidden-input checks pass;
2. the 65,536 assignment rows are unique and their digest matches the freeze;
3. every matrix and score is finite and every reading has nonzero null SD;
4. joint composite `p <= .01`;
5. minimum-reading composite raw effect `>= .015`;
6. both `FAMILY_ONLY` and `BOUNDARY_AWARE` minimum-reading effects are
   `>= .010`;
7. `NO_EXACT_RECORD` keeps at least 18/21 rings in every reading, spans all
   four folios, has minimum-reading effect `>= .010`, and joint `p <= .05`;
8. at least three of four physical folios have positive observed-minus-null-
   mean effects in every reading;
9. deleting any physical folio leaves every reading's composite effect
   positive;
10. no one folio contributes more than 60% of the sum of absolute folio
    effects in any reading;
11. exact cyclic rotation and ring reflection leave every aggregate score,
    null orbit, effect, and decision unchanged within `1e-15`;
12. all target-blind controls and an independent nonimporting reconstruction
    pass before target access, and the final target is independently rebuilt.

Failure of any gate is a final nonconfirmation of this exact representation.
No page, ring, folio, reading, view, distance, threshold, or family may be
mined afterward.

## Target-blind controls

Controls use only the frozen ring/page/folio geometry and synthetic token
sequences. The unchanged complete scorer must:

- confirm a distributed neighbor-sharing construction in every reading and
  all four folios;
- reject a random null;
- reject a one-folio construction by support/deletion/concentration;
- reject a third-reading disagreement;
- reject an exact-record-only construction through the mandatory
  `NO_EXACT_RECORD` gate;
- reject a length-only construction whose token identity is constant;
- reject a distance-two rather than distance-one construction; and
- pass cyclic rotation, reflection, serialization, duplicate-rank, missing-
  slot, reordered-ring, reading-order, and nonfinite mutation controls.

Controls must demonstrate at least 7/8 distributed planted worlds confirm and
0/8 worlds confirm for every negative family. Those thresholds may not change
after target access.

## Claim ceiling

If every gate passes, the claim is only: neighboring public zodiac-label
records share a transferable, length-adjusted STA-family construction signal
beyond nonadjacent positions in the same rings. This would support a locally
ordered label register and would be useful for later structural work.

It would not establish authorial word boundaries, label-to-object ownership,
a counter, a number system, degrees, a starting position, direction, sign
names, sounds, a language, a cipher, any English word, plaintext, or a
translation.
