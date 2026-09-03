# GDT775 analysis contract

This is an exploratory, count-informed registration, not a blinded holdout.
GDT774 and pilot cache counts were already available when it was written. Its
purpose is to fix the renderer and comparison rules before publication, not to
claim independent discovery data.

## Fixed question and inputs

Starting only from the 376 GDT774 targets, test whether exact complete right
words can turn automatic nominal fallbacks into concrete two-whole spans. Use
the guarded GDT769 cache for exact adjacency, GDT734 for complete-whole German
defaults, GDT762 only for the named state-family architecture, GDT757/765/768
for complete-word controls, and GDT735 for historical architecture. Open no
new page or image. Keep `f84` and `f84r` forbidden.

## Fixed selection

The novel cohort is `automatic_contextual=0`, `any_direct_signature=0`, and
`hybrid_contextual=0`. The primary thirteen-family rule, extension rule, four
slot-only surfaces, fluent templates, rivals, and control anchors are exactly
the rows in the three TSV specs under `src/`. Page, locus, occurrence ID, and
GDT773 case ID are prohibited dispatch keys.

Expected count chain:

```text
376 total → 327 automatic fallback → 311 signalless → 305 novel
305 novel → 203 exact right word → 66 fixed-family spans
66 = 57 primary + 9 extension
four slot-only surfaces = 8 further spans
```

## Fixed comparisons and renderer

Compare the target right-word vector to nominal and field/formula predecessor
vectors in balanced 6+6 and 8+8 decks. Report pooled and per-surface-equalized
cosines separately. Leave-one-folio runs are sensitivity checks, not predictive
holdouts; any first/middle imbalance must remain visible and caps the role
result at a provisional lean. The decks are balanced only by surface count,
the 8+8 deck nests the 6+6 deck, and a target-only drop audit must expose
dependence on `daiin`, `aiin`, and the fixed thirteen-family. Preserve all
existing GDT774 automatic outputs before applying the 66 family spans; the
throughput display then adds the eight slot-only spans.

Token consumption is layer-specific: the family layer consumes only its 66
right words, while throughput and hybrid-throughput consume 74. Separate span
and right-token identifiers prevent a slot-only decision from suppressing a
token in the family layer.

The selected German output is a working renderer, not plaintext. All rows keep
`default_is_translation=0`, `confirmed_lexeme=0`,
`confirmed_plaintext=0`, and `component_export_credit=0` wherever those fields
are present.
