# LRG007 A/D prose-edge transfer capacity

Status: `REGISTERED_ASSOCIATION_UNOPENED_CAPACITY`

LRG002 independently defines FIRST, CORE, and LAST positions in corrected B/P
prose segments. LRG004 independently confirms that source-native initial family
A is label-associated and D is label-depleted. LRG007 asks a new transfer
question: do those two fixed families occupy the corresponding prose-edge
register after exact page and group-length control?

Start from the frozen LRG002 primary prose panel. Form cells by exact page and
symbol count without reading any initial family. Keep only cells containing at
least one FIRST, one CORE, and one LAST group. Emit opaque row and cell IDs,
physical folio, section, and FIRST/CORE/LAST position. After selection is
immutable, reconstruct binary initial-A and initial-D vectors only to record
their aggregate counts, per-cell margins, and vector hashes. Do not compute or
emit any family-by-position count, effect, score, or favorable row.

Capacity requires exactly 4,911 rows in 132 cells on 34 pages and 16 physical
folios, both B/P sections and both folio parities, plus at least 100 occurrences,
30 variable cells, and 12 represented folios for each of A and D. A and D must
be mutually exclusive.

A pass authorizes only target-blind synthetic calibration of a simultaneous
four-channel test: A FIRST-minus-CORE, A LAST-minus-CORE, D CORE-minus-FIRST,
and D CORE-minus-LAST. Exact per-cell A/D/other margins must be preserved. No
position association may open before calibration and clean reconstruction.

Capacity or a later pass cannot establish opening, closing, boundary semantics,
a prefix, morpheme, word, part of speech, sound, language, cipher operation,
English meaning, plaintext, or translation.
