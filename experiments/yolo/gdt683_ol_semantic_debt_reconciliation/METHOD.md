# GDT683 method

## Question

Can the inherited generic `ol` renderer be reconciled with GDT664's already
published practical `LEARNED_OL_BASE = Grundansatz` card across every admitted
exact ZL3b occurrence, without exporting a free-word meaning across reader
joins, glyph conflicts or the local `oly` action boundary?

## Inputs

- GDT671's f84-free 4,128-line V48 panel and V48 token glossary;
- GDT664's published V41 stem model;
- GDT682's complete 51-line V56 reader and compact result;
- two manual specification sheets: six V56 debt decisions and 25 local
  boundary/form/rival overrides for neither-exact positions;
- the mixed transcription table, materialized only through
  `vmanus-exp query-tsv` with 417 explicit locus allow-values, seven output
  columns and `--forbid-prefix f84`.

## Method

1. Enumerate exact whitespace-delimited ZL3b `ol` positions in the admitted
   panel. This yields 463 positions on 417 loci and 108 pages.
2. Confirm the propagation split: the GDT664 stem model says
   `LEARNED_OL_BASE / Grundansatz / exaktes nacktes Ganzwort`, while the V48
   glossary still carries the older structural label
   `Eigenschafts-/Zustands-/Materialträger...`.
3. Guard-query exactly the 417 loci. The loader selects 417, rejects 98
   f84-prefixed rows before materialization and skips 4,871 non-allowed rows.
4. Align IT2a and RF1b to ZL3b with a corrected character-cost dynamic
   program. It admits 1→1, bounded 2/3→1 merges, 1→2/3 splits and strict
   2→2 resegmentation. Among minimum-edit paths it prefers exact `ol→ol`
   anchors, then all exact tokens, fewer unexplained insertions/deletions and
   fewer fuzzy boundaries. A 2→2 boundary move is admitted only when its
   concatenated edit distance beats the two independent token edits.
5. Apply portable `Grundansatz` only at the 374 bilateral exact positions. At
   64 positions with exactly one supporting alternate reader, retain it as a
   majority default and record the other reader's boundary, form or deletion
   rival with any available published meaning.
6. Route all 25 neither-exact positions through keyed local specifications:
   nineteen bound material forms, five concrete material/glyph conflicts and
   the `ol+y -> oly = abseihen` action conflict. None exports a free `ol` card.
7. Rerender all 417 affected lines span-wise and the six V56 debt positions.
   At f115r.1 both alternate readers bind `cheop ol`, so that source span
   becomes one powder compound rather than two semantic chunks. Every local
   specification records evidence type, composition, unresolved component,
   reader scope and exact source span.
8. Preserve all 45 untouched V56 lines byte-for-byte at field level, retain
   479 assigned positions, zero gaps and 86 action positions, and emit the
   seven adjacent-`ol` cases as repetition of the same card.
9. Independently rebuild all nine result-bound artifacts, compare every byte,
   verify all occurrence keys, distributions, boundaries, V57 alignments,
   hashes, privacy markers and both page seals.

## Decision rule and claim ceiling

The portable card is admitted only where IT2a and RF1b both have exact `ol`.
A one-reader case is labeled majority-with-rival, never portable across all
readers. A neither-exact position must have one
explicit keyed local renderer and may not inherit `Grundansatz`. A V57 line
passes only if token and gloss counts remain aligned, the old OL meta-gloss and
`Ansatz/Gut` disappear, and no operation, quantity, unknown count or action
count is silently lost.

These are concrete, replaceable working translations. Reader agreement
supports a word boundary at 374 positions and at least one exact alternate at
another 64; it does not prove the German meaning. GDT683 adds no confirmed plaintext,
phonetics, plant, disease, carrier liquid or historical codebook identity.
