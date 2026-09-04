# GDT791 method

## Question

Can the complete 30-page released corpus be represented in one lossless
occurrence graph that respects both the GDT581 text grammar and visible page,
panel, record and component boundaries? Where the two structures disagree,
which links must be split, reparented or quarantined?

## Inputs

- The mixed ZL3b line transcription, materialized only through an explicit
  35-selector allow-list and `f84`/`f84r` prefix rejection.
- GDT515's complete 5,866-token running/local partition and line coordinates.
- GDT581's 5,122 running events, 793 statements, 744 local cards, 4,026 alias
  edges and 5,672 focus assignments.
- GDT790's 123 deep prose lines, 13 records under ten panels, 28 component-label
  tokens and ten exact label/prose string-reuse edges.
- Six prior visual-review batches whose disjoint page union is exactly the 30
  released pages. Their source files and the executable inputs are hash-locked.

## Construction

1. Normalize 35 transcription selectors to 30 physical pages.
2. Replay every selected line against the ordered GDT515 token groups.
3. Classify a line as running prose, local label/marker or empty transcription.
4. Give all occurrences a direct page context. On f77r, f82r and f83r, replace
   that coarse context by the exact GDT790 record or label-component context.
5. Project each GDT581 statement tokenwise into GDT790 records. A legacy
   statement touching two records becomes two local fragments; its old ID is
   retained only as provenance.
6. Classify all 745 deep-page aliases as same-record, source-free owner default,
   or cross-record. Retain, locally reparent, or quarantine them respectively.
7. Audit raw focus governors separately from effective grammar hosts.
8. Keep label/prose exact-string reuse in a separate zero-semantic-credit graph.
9. Count the running and local capacity of six image-conditioned complete-form
   targets without assigning a translation.

## Decision rule

Select the integrated spine only if it gives exact replay of all 1,007 lines and
5,866 tokens; preserves the 5,122/744 running/local partition; assigns all 940
deep prose tokens and 28 deep label tokens; exposes every record crossing; and
materializes no sealed row. Image records outrank a legacy statement only as a
segmentation boundary, never as proof of word meaning.

## Claim ceiling

The experiment may select visible page/panel/component owners, record-local
statement segmentation and boundary-link repairs. It may not select plaintext,
a Voynich lexeme, a free root or affix, object identity, substance, action,
process direction, word-to-figure ownership from proximity, or unseen-form
meaning. Structural tags remain distinct from English or German translations.
