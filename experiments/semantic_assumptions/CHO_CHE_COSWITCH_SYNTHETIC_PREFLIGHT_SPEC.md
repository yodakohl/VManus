# `cho/che` independent co-switch synthetic preflight

## Question and isolation

Calibrate a held-physical-leaf statistic for detecting a distributed formal
change outside every group containing the defining `ch/sh+o/e` site.  This
preflight reads only the validated masked capacity panel and generated feature
vectors.  It must not read `primary_sta_families`, raw target surfaces, or any
future target result.

Frozen inputs:

- `results/cho_che_coswitch_masked_panel.tsv`, SHA-256
  `25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003`
- `results/cho_che_coswitch_capacity_v2.json`, SHA-256
  `c32a6dc5456a59f469de1f8d47d95fba8e6384d60ecccd678adb678c0382b775`
- `results/cho_che_coswitch_capacity_validation.json`, SHA-256
  `68bf07fa2fcaf5437fd5240ac394b4c20add24d4867eb3b3ac846378b0809d73`

## Frozen target representation

For a future target only, join the masked IDs once to their source-native
zero-alternative STA family sequences.  Use the official 24 family symbols and
three separate blocks:

1. `FAMILY_RATE`: 24 group-normalized family frequencies;
2. `ENDPOINT_RATE`: 24 first-family plus 24 last-family frequencies;
3. `BIGRAM_RATE`: 576 group-normalized ordered adjacent-family frequencies.

The exact nuisance cell is
`(section, Currier, hand, kind, grammar_scope, exact formal length,
page-position quartile, group-position class)`.  Within each
`(reading, physical leaf)`, retain a cell only with at least two groups on both
page sides.  Average group features within side and cell, subtract low from
high, then average cells equally.  Bigram cells use only length at least two.
No fitting or feature selection uses page state.

Normalize each nonzero leaf vector within block, concatenate the three blocks
with equal block norm, and normalize again.  For each reading, the primary
alignment is the mean cosine over all 28 leaf pairs.  The primary scalar is the
minimum alignment over ZL3b/IT2a/RF1b.  Enumerate all 256 synchronous sign
flips of the eight physical-leaf vectors; use inclusive upper-tail rank.  The
global complement is an exact tie, so the attainable floor is 2/256=.0078125.

## Frozen target gate

All conditions must hold:

- primary minimum-reading alignment at least `.10`;
- synchronous exact p no larger than `.01`;
- at least seven of eight held-leaf direction scores positive in every
  reading;
- every leave-one-leaf deletion alignment positive in every reading;
- cosine between the mean high-recto and mean high-verso directions positive
  in every reading;
- cosine between mean prose-associated leaves and mean diagnostic/circle
  leaves positive in every reading;
- mean same-leaf cosine across the three alternate readings at least `.40`;
- no leaf supplies more than `.30` of the positive alignment mass in any
  reading;
- at least two of the three separate feature blocks have positive mean
  pairwise alignment in every reading;
- every vector and statistic finite and exact panel geometry retained.

ZL3b, IT2a, and RF1b remain alternate readings, not independent replications.

## Synthetic worlds

Use deterministic Gaussian leaf-vector noise scaled by each frozen
reading/leaf's harmonic side count.  Each block has an independent fixed
direction, shared across readings only when the planted mechanism requires it.
Run:

- 64 `NULL` worlds;
- eight `DISTRIBUTED_THREE_BLOCK` worlds at strength `.75`;
- eight `DISTRIBUTED_TWO_BLOCK` worlds at strength `.75`;
- eight each of `ONE_LEAF`, `ONE_READING`, `OPPOSITE_READING`, `SIDE_ONLY`,
  `DIAGNOSTIC_ONLY`, `PROSE_ONLY`, and `ONE_BLOCK` at strength `1.00`.

Strength is the planted direction norm divided by the expected noise-vector
norm for that reading/leaf/block.  The worlds calibrate the frozen abstract
statistic, not an English or linguistic effect size.

Preflight passes only with:

- at most one of 64 null worlds passing;
- at least seven of eight distributed three-block worlds passing;
- at least seven of eight distributed two-block worlds passing;
- zero passes in every adversarial control family;
- exact 256-assignment sign orbit, finite numerics, deterministic serialization,
  target-file absence, mutation rejection, and independent reconstruction.

Failure forbids target access and closes this exact scorer without threshold or
feature retuning.  Pass authorizes only a separately hash-frozen single target
run.

Even a target pass establishes only a distributed formal page-side system
state outside the defining construction.  It supplies no meaning, sound,
wordhood, language, cipher, plaintext, or translation.
