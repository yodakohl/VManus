# GDT220 — fixed-edge local reference audit

## Question

GDT217 found seven page/key cells under one already frozen representation:
the final two source-family signs of a human-annotated label versus the first
two source-family signs of a prose paragraph.  GDT220 does **not** search a
new edge, key width, host, or orientation.  It asks a narrower post-hoc
question: do those seven overlaps identify locally owned label-to-text
references under the existing human catalogue?

## Frozen inputs and scope

- use the seven rows of `gdt217_exact_overlaps.tsv` unchanged;
- use only already published human descriptions copied into
  `gdt220_local_assembly_manifest.tsv`;
- use `gdt012_annotated_core_inventory.tsv` for the selected labels;
- use `gdt016_group_state_inventory.tsv`, rejecting every `f84*` row before
  retention, for the f83r paragraph content diagnostic;
- retain the GDT217 key `FINAL_FAMILY_2_TO_INITIAL_FAMILY_2` exactly.

The panel is fully exposed.  Visual-relation states are therefore descriptive
source audit classes, not a blinded endpoint:

- `SAME_CATALOGUE_PARENT_FIGURE_ADJACENT`;
- `EXPLICIT_DIFFERENT_CATALOGUE_VISUAL_UNITS`;
- `EXPLICIT_DIFFERENT_PAGE_ZONES`;
- `MIXED_LABEL_UNITS_PARAGRAPH_PARENT_UNRESOLVED`;
- `UNRESOLVED_PAGE_LEVEL_ONLY`.

## f83r local diagnostic

The only same-parent cell is f83r: `darolsy` at f83r.51 and the paragraph
beginning at f83r.52 are both human-described relative to the southwest
figure, and their source-family key is `CA`.  Reconstruct the complete
available HPR2 rows of the four-line paragraph f83r.52--55 and report:

1. exact `arolsy` host recurrence;
2. exact `ol` host recurrence;
3. AR/AL-state occurrence;
4. coverage completeness.

This is not a word-meaning test.  The three strict f83 label keys (`AB`, `AG`,
`CA`) can be reassigned to the two upper positions and one lower strict
position in six ways.  The local exact tail is the fraction placing `CA` in
the lower position, where the lower paragraph begins `CA`.  The fourth label
f83r.50 is excluded from this calculation because GDT217 did not have a
strict eligible family value for it; that missing value is a mandatory
counterexample.

## Decision

Call a local reference mechanism established only if at least two independent
physical folios have a same-parent match and no explicit different-unit match.
Otherwise retain individual co-local candidates and reject a demonstrated
reference system.

No family is a number, index, word, sound, language, plaintext, meaning, or
translation.  f84r and every f84 row are excluded and are not accessed.
