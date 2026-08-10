# ETR001 exact-template recurrence capacity specification

Status: **FROZEN_SCORE_BLIND_CAPACITY_ONLY**

Date: 2026-08-10

## Question and non-duplicate boundary

Before any target-family equality is computed, determine whether corrected
5--12-group prose records contain enough exact cross-folio natural experiments
to compare:

1. records with the same ordered sequence of non-target source-native family
   groups; and
2. records with the same exact multiset of those groups in a different order.

The masked target bundle consists only of CORE positions carrying the frozen
66-class support bit from LRS001-R1. Its family identities are forbidden in
this capacity pass. The target-position mask and target symbol-count vector
remain fixed inside a stratum.

This is not LRS001-R1 model tuning. ETR001 fits no model, classifier,
embedding, rank, ridge, DCT, coefficient, alignment, or latent column. It asks
only whether exact parallel non-target templates recur. It is also distinct
from root recency, adjacent root-pair mining, higher-order suffix assembly,
label-to-prose reuse, catchwords, and graphical arrays because its comparison
is conditional on one identical source-native context bag across complete
corrected prose records.

## Frozen inputs

- `results/lrs001r1_anonymous_geometry.tsv`, SHA-256
  `37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df`;
- `results/lrs001r1_anonymous_geometry.json`, SHA-256
  `0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542`;
- `results/drawing_reset_segment_atlas.tsv`, SHA-256
  `e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486`;
- `results/drawing_reset_segment_atlas.json`, SHA-256
  `3e7f07d1c22e331f3bde713e79250c03065e83ec5954868be545cb91287d2279`;
- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`;
- `results/source_sta_family_consensus.json`, SHA-256
  `193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7`.

Only manual ZL3b/IT2a/RF1b-derived source-native STA families and corrected
human separator/drawing metadata enter. No OCR, automated vision, legacy
parser root, role, EVA surface, image label, or English gloss is permitted.

## Exact capacity construction

Use all records in the frozen pseudonymous geometry; the prior split is not a
training boundary because ETR001 fits nothing. Reconstruct each geometry group
against the drawing-reset atlas by
`G + sha256("LRS001R1|G|" + consensus_group_id)[:20]`, and verify its family
surface (non-target rows only) and symbol count against the consensus-group
table.

Load the geometry target mask first. For each supported target row, retain only
`(physical ordinal, symbol_count)` and discard its family surface immediately
on reading either source table. For every other row, retain the exact
source-native `family_surface`. No target surface may enter a derived key,
value equality, count, panel digest payload, output, or diagnostic. The six
whole-source-file SHA-256 bindings are the sole provenance exception: they bind
the frozen input bytes without isolating, comparing, counting, or serializing
any target value.

The exact stratum is:

`(record_length, target_position_mask, target_symbol_count_vector, section,
currier, hand, code, segment_count, segment_index, starts_after_drawing,
ends_before_drawing, original_group_count, sorted_non_target_context_bag)`.

Within a stratum, an `IDENTICAL_ORDER` pair is a cross-folio record pair with
the same ordered non-target sequence. A `DIFFERENT_ORDER` pair is a cross-folio
pair with different ordered sequences. A stratum is informative only if both
pair classes are nonempty. Count each record pair once. A masked target
comparison is one aligned target slot within one retained pair.

Capacity orbit bits are `sum(log2(n_s!))` over informative strata. This is the
assignment-label orbit before target-bundle multiplicities are opened; a
future target method must stop before scoring if its exact effective orbit is
below 8,192.

Folio exposure is the largest count of retained pair endpoints belonging to
one physical folio divided by all retained pair endpoints.

## Frozen GO gates

All must pass:

- at least 12 informative strata;
- at least 100 masked target comparisons;
- at least eight physical folios;
- at least 32 `IDENTICAL_ORDER` pairs;
- at least 32 `DIFFERENT_ORDER` pairs;
- capacity orbit at least 13 bits (8,192 assignments);
- maximum folio endpoint exposure at most 0.25.

Failure stops ETR001 unopened at this exact resolution. A pass authorizes only
a separate target-blind synthetic calibration of the direct equality statistic
before any real target-family equality is computed.

## Future statistic and claim ceiling

If capacity passes, the future target statistic is the equally weighted
stratum mean of target-slot agreement for `IDENTICAL_ORDER` pairs minus that
for `DIFFERENT_ORDER` pairs. The exact null permutes whole target bundles
within the frozen stratum and never changes context, geometry, ecology, target
marginals, or bundle integrity. Plant-copy positives and bag-only/random-target
negatives must pass independently before target access.

At most, a fully validated target pass could establish cross-folio exact
formal-template or parallel-passage recurrence and expose internally aligned
records for later study. It cannot name a field, word, POS, recipe stage,
language, sound, cipher, meaning, plaintext, or translation.
