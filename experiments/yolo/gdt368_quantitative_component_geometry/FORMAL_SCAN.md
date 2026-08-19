# GDT368 frozen formal scan

Status: **FROZEN AFTER VISUAL CAPACITY, BEFORE FORMAL ROW ACCESS**.

The eligible visual panel is fixed at 27 rows and three categorical endpoints:
`MAJOR_BODY_COUNT`, `TERMINAL_ARM_COUNT`, and `DOMINANT_HUE`. All visual calls,
including uncertainty, were published before this scan.

## Formal source and library

Use only the already generated, f84-free GDT002 exploratory visual/formal join,
filtering its canonical `CONTACT_GAP` rows to the exact 27-locus GDT368 census.
No PAGE_HOST, HPR2, member code, literal transcription, root, tuple identity,
lexical surface, or semantic field is eligible.

Build one state-blind family-level predicate library:

- family-component presence;
- family bigrams and trigrams generated only within source groups;
- first-group prefixes and last-group suffixes of length 1–3;
- delimiter-preserving exact family expression;
- fixed symbol-count thresholds `<=3/4/5` and `>=6/8/10`;
- group-count `>=2/3`;
- internal-boundary type and alternative-reading presence when available.

Admit a mask only if it occurs on at least four of 27 loci, is absent on at
least four, and both its presence and absence span at least two physical
folios. Collapse identical locus masks and retain aliases. This construction
does not inspect any visual endpoint.

## Fixed scores

For each endpoint and unique formal mask:

1. array-stratified conditional mutual information in bits per row;
2. pooled Cramer's V and full state×feature counts;
3. leave-one-physical-folio-out categorical codelength gain over the
   state-frequency baseline, using Jeffreys smoothing fixed at 0.5;
4. per-folio held gains and number of positive held folios.

Primary null: 4,096 deterministic worlds permuting each visual endpoint within
its complete array while preserving every array's observed state counts.
Uncertain rows are retained as their own category; report a secure-only
sensitivity that removes uncertain rows before building the same state-blind
library. `local_p` is the inclusive tail for one endpoint/mask. `maxT_p` is the
inclusive maximum CMI over all three endpoints and every admitted unique mask
in each world. The whole library is fixed once and is not reselected per
world.

Report leave-one-folio deletion sensitivity, feature support by array, and
whether the apparent effect has the same direction in at least two mobile
arrays. A hue association with no within-array support outside f89/f99 is
`LIKELY_PAGE_CONFOUND` regardless of nominal score.

Labels are exploratory:

- `INTERESTING_EXPLORATORY`: maxT p <= .20, positive LOFO gain, at least two
  positive held folios, and same-direction contribution from at least two
  mobile arrays;
- `WEAK`: local p <= .10 or positive LOFO gain;
- `LIKELY_PAGE_CONFOUND`: nominal association dominated by page/array ecology;
- `UNSTABLE`: sign/direction reverses across mobile arrays or LOFO is negative;
- `NO_SIGNAL`: otherwise.

No threshold is a confirmation gate. Selector-paid gain subtracts
`log2(3 × admitted_unique_masks × 2)` and is descriptive only.

## Ceiling

This post-image-selected scan can nominate only an anonymous visible-geometry
and source-family association for a later independent acquisition. It cannot
establish ownership, object identity, plant part, role, word, morpheme,
language, plaintext, meaning, or translation. No f84 data may be retained,
joined, scored, or displayed.
