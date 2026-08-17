# GDT179 — f57 page-translation scaffold

## Purpose

GDT179 asks whether the strongest surviving diagram-level hypothesis can be
made executable: can f57v be read as a four-element/four-quality technical
schema while every Voynich inscription remains source-native and every
ambiguity remains visible?

This is a YOLO theory-generation pass, not confirmation.  It deliberately
constructs the strongest coherent page reading supported by the inherited
evidence, then records exactly where that reading stops.

## Source freeze

Before the target synthesis, the official Digital Walters description of
Walters MS W.73 was frozen in `gdt179_w73_comparator_manifest.tsv`.  On W.73
f.7v the source places, from the top clockwise:

1. Fire — hot and dry — summer — red/yellow bile;
2. Air — hot and moist — spring — blood;
3. Water — moist and cold — winter — phlegm;
4. Earth — cold and dry — autumn — black bile/melancholy.

The comparator is an independent witness to the system architecture and phase,
not a proposed direct source of the Voynich manuscript.

## Frozen Voynich observations

Only already-published, source-bound f57v facts are used:

- four concentric circular writing bands with one common start;
- R2 is four repeated 17-sign periods;
- R2 position 9 is the sole all-reading-stable changing column and has the
  state `f,f,p,p` in top/right/bottom/left order;
- four figure-near N1 inscriptions occupy NE/SE/SW/NW positions;
- four D1 radial inscriptions occupy the same NE/SE/SW/NW positions but lie
  between figures;
- the N1 and D1 ownership relation remains proximity-only;
- f84r is neither read nor used.

## Target synthesis

The W.73 phase induces element sectors TOP/RIGHT/BOTTOM/LEFT =
FIRE/AIR/WATER/EARTH and inter-element quality positions
NE/SE/SW/NW = HOT/MOIST/COLD/DRY.

The candidate local decoder is then stated, not fitted:

- N1 `starts_ot` selects the two qualities incident to FIRE;
- D1 `has_ok_component` selects the two qualities incident to WATER;
- terminal `y` selects the passive-quality pair MOIST/DRY;
- absence of terminal `y` selects the active-quality pair HOT/COLD.

Each register therefore supplies two binary coordinates and identifies all
four quality positions.  The decoder applies only to these two f57 registers.
Its features were discovered post hoc on the same page, so exact internal fit
is descriptive rather than a confirmation statistic.

For R2, `f,f,p,p` is compared with every frozen binary attribute.  It matches
the hot-element/cold-element partition, but it is also the page upper/lower
partition and the Latin masculine/feminine element-name partition.  GDT179
must retain all three aliases and must not declare `f=hot` or `p=cold`.

## Required outputs

- a complete source-native inscription inventory;
- one explicit page-role scaffold;
- the two-register truth table;
- R2 alias analysis;
- counterexamples and unresolved regions;
- a validator that reconstructs every mapping without importing the scorer.

## Decision ceiling

The strongest permitted result is:

> f57v admits a complete, internally coherent, page-local four-quality decoder
> under a historically attested four-element phase.

This does not establish that any Voynich group literally means an English
quality, that the same affix has that function elsewhere, that W.73 was copied,
or that any prose has been translated.
