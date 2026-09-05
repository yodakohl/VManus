# GDT811 — bounded whole-form reference inventory

This is an outcome-aware follow-up to the direct f88r inspection, not an
independent discovery test. It inventories seven preselected complete surfaces:
`okol`, `chokol`, `qokol`, `okoldy`, `qoekol`, `ofaldo`, `ofal`.

## Already seen before this inventory

All 31 admitted f88r transcription lines and the existing f88r image were read.
The page has 15 label lines and three prose paragraphs. Its only exact
label-word/prose-word match is `okol`: label f88r.15 and f88r.19 word 7.
The same complete sequence occurs inside `chokol` at f88r.19 word 2,
`okoldy` at f88r.26 word 7, and five `qokol` at f88r.27 words 1, 3, 4 and
f88r.29 words 3, 6. The less exact candidate `qoekol` occurs twice in f88r.19.
The lower label `ofaldo` at f88r.25 has a possible shorter counterpart `ofal`
at f88r.30 word 7. These thirteen seed occurrences retain their complete
whitespace surfaces in ZL3b, IT2a and RF1b. They are not new findings from the
larger inventory.

## Question and competing implications

Does the existing admitted text place these wholes only near a narrow set of
botanical records, or across many records, sections and non-botanical labels?
The first distribution would be compatible with a particular drug name. Broad
use, especially near visibly unrelated kinds of object, would strengthen a
common property/category or reference rival. Neither distribution identifies a
species, disproves a widely used drug name, or converts section codes into
individual object identities. Image meanings are not assigned by this script.

The seven complete strings remain separate. No meaning is exported to `q`,
`ch`, `dy`, `e`, `do` or any other substring. Counts are descriptive, with no
candidate-ranking score, semantic winner, significance threshold, or relation
gate asserted. Occurrence concentration is not independent lexical evidence.

## Admitted source scope

Use the union of the already inherited 179 selectors in GDT631
`artifacts/PAGE_ALLOWLIST.tsv` and the source selectors for the thirty released
physical pages in GDT791 `src/PAGE_SELECTOR_SPECS.tsv`. Reject any selector
beginning with `f84` before querying. Do not open new pages or images.

Query raw ZL3b lines once and alternate-reader lines once, each through
`vmanus-exp query-tsv`, with every allowed selector explicit and both `f84` and
`f84r` forbidden. Retain only requested columns. Query the GDT791 line-owner
atlas once, restricted to its released source selectors, to obtain the actual
running/local classification and released physical-page mapping. Outside that
atlas, keep the raw transcription kind and record released status as unknown.
The full selected corpus is held only in memory; exported lines belong only to
target occurrences. No OCR, image decoding, or external fetching occurs.

## Counting and reader agreement

Match whitespace-delimited complete surfaces exactly. Preserve every occurrence,
its one-based token ordinal and its one-based occurrence rank for that surface
within the line. Alternate support means the same numbered occurrence exists
in that reader's line. It is not an alignment proof, a neighboring-span claim,
or three independent manuscript witnesses. Export each alternate ordinal and
count, and do not infer character equivalence from a missing match.

Use the explicit GDT791 mapping for released physical-page keys, preserving
panel-numbered physical keys such as `f67r2` and `f68r1` exactly as that mapping
defines them. Do not replace or reject that mapping by a digit-stripping rule.
Outside GDT791 only, normalize source selectors such as `f72r1` and `f72r2` to
the side-grouping key `f72r`, preserving source selectors separately. Mark every
occurrence's grouping basis explicitly: authoritative GDT791 mapping versus
normalized-side heuristic. The latter is not an independently established
physical-page identity, so pooled page counts are grouping counts under that
declared convention. Count source sections as source
metadata, not semantic categories. Distinguish raw prose (`kind=P`), raw local
labels (`kind=L`), other raw kinds, and the independently inherited GDT791
running/local status. Report both occurrence and distinct-locus/page counts.

## Outputs

- `REFERENCE_INVENTORY.tsv`: every exact occurrence, full ZL3b source line,
  location, raw kind, source section, released status and ranked reader support.
- `REFERENCE_WHOLE_SUMMARY.tsv`: one row per selected whole, including zeros,
  total/f88r/external counts, source selectors, physical pages, label/prose
  counts, section counts and reader support.
- `REFERENCE_DISTRIBUTION_COUNTS.tsv`: per-whole counts by source section,
  normalized physical page, raw role and released GDT791 status.
- `REFERENCE_RESULT.json`: source and output hashes, exact query scopes and
  guard statistics, retained-row counts and zero semantic/component credit.

The inventory script may be run only after this design exists. The main GDT811
report must distinguish these outcome-aware descriptive counts from any later
interpretation of the four inspected pages.
