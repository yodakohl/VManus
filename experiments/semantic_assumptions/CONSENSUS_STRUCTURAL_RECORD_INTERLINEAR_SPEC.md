# Consensus structural record interlinear v1

## Purpose

Produce a readable record-level companion to the validated source-native group
interlinear and drawing-reset segment atlas.  The unit is one unanimous
drawing-reset segment, not a legacy cleaner line or inferred sentence.  This
is a descriptive consolidation of already confirmed formal evidence; it fits
no model and assigns no English gloss.

## Frozen source

The only scientific table is
`results/drawing_reset_segment_atlas.tsv` at SHA-256
`e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486`.
Its independent validation JSON is required at SHA-256
`6bca45bd2cdc01eb2c3d6cad6ad8f0999e9fb6b2ecc0237d9552f33316f97442`
with status `PASS`.  The atlas already preserves all 23,281 strict
source-native groups in 4,012 drawing-reset segments and contains no English
gloss.

No legacy parser root/role, OCR, automated-vision output, historical-language
guess, external decoder, or inferred picture ownership may enter.

## Record construction

Preserve first occurrence order of `segment_id` in the source atlas.  Within a
segment, require exact consecutive `segment_group_index=1..N`, one invariant
metadata tuple, and the declared `segment_group_count=N` on every row.

For each segment emit:

- the factual page metadata and physical-line segment coordinates;
- space-separated family surfaces and three separate STA/basic-EVA readings;
- exact-member, lossy-EVA, and internal-boundary agreement counts;
- counts of favored, disfavored, and unresolved within-group family
  transitions;
- counts of resolved exact-position tendency slots;
- opening-feature, closing-feature, and favored-path group coverage;
- one compact formal expression per group.

An exact-position tendency slot is resolved only for
`FIRST_ASSOCIATED`, `LAST_ASSOCIATED`, `EDGE_ASSOCIATED`, or
`CORE_ASSOCIATED`.  A transition is resolved only when labeled favored or
disfavored.  The formal-resolution fraction is

`(favored + disfavored transitions + resolved tendency slots) /
 (all within-group family transitions + 2 * group_count)`.

All rates use six fixed decimal places.  A segment with no internal boundary
has boundary-consensus rate `1.000000` by vacuous completion.

`ALL_MEMBER_AND_BOUNDARY_STABLE` requires every group's three STA-code strings
to be byte-identical and every internal boundary to have support three.
Everything else is `READING_OR_BOUNDARY_VARIANT`.

The compact group expression is

`POSITION:SURFACE{adj=SIGNATURE;fl=LABEL;ec=LABEL;o=N;c=N;p=PATH}`

where position is `S/F/C/L`; adjacency characters are `F/D/U`; first/last
labels are `F/L/U/I/N`; edge/core labels are `E/C/U/I/N`; and `p=-` means no
favored path.  These are formal abbreviations, not words or semantic roles.

## Compact packet

A record is packet-eligible only when it is confirmed prose, contains 5--12
groups, and is `ALL_MEMBER_AND_BOUNDARY_STABLE`.  Rank eligible records within
the exact `(section, Currier)` cell by:

1. descending exact formal-resolution fraction;
2. descending group count;
3. ascending UTF-8 `segment_id`.

Select at most the first three records per cell.  This packet is a balanced
inspection aid, not a statistical sample, optimum, held test, or semantic
discovery set.  No selection uses EVA spellings, historical language, image
content, or English meaning.

## Claim ceiling

The result is a consensus structural interlinear over already validated
source-native evidence.  It may expose where formal annotation is dense or
sparse and where readings disagree.  Position, adjacency, boundary, path,
and packet tags are not words, parts of speech, meanings, sounds, morphemes,
lexemes, plaintext, language, cipher, or translation.  Basic EVA remains an
explicitly lossy display convenience.
