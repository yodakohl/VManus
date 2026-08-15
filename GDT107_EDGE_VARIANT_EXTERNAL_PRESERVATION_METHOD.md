# GDT107 — external preservation across PAGE_HOST edge variants

## Question

When the same edge-stripped PAGE_HOST core occurs with different final edge
characters on different physical folios, does it preserve archived external
object or relation tags?

This tests the coupled-address interpretation after GDT105/GDT106. It does not
assume that an edge-stripped core is a word or morpheme.

## Panel

From the non-f84r HPR2 external inventory, retain single-group annotated loci
with PAGE_HOST length at least four. Form all pairs with:

- equal `PAGE_HOST[:-1]`;
- different final characters;
- different physical folios.

Average tag Jaccard within each core first, then average cores equally so a
single frequent core cannot dominate.

## Matched null

For each anchored pair, replace the second member by a different-core locus
matched on target section, Currier, final character, host length, and a folio
different from the anchor. If no exact edge match exists, relax only the final
character and disclose the count. Use 20,000 deterministic draws.

Score the pre-existing four object/content axes, four relation/layout axes,
and all eight together. These tags are archived, exposed, and correlated;
p-values are diagnostics only.

## Claim ceiling

Cross-edge external-tag preservation only. No word, morpheme, POS, sound,
language, plaintext, semantic role, gloss, meaning, or translation. f84r is
excluded and untouched.
