# Public word-boundary overlap audit for the retained hard edges

This deterministic audit asks whether the frozen retained-parser hard-edge
inventory is structurally new, or whether its surface carrier is primarily an
instance of a pattern already described in public Voynich research.

Public prior:

- Emma May Smith, “Glyph Combinations across Word Breaks in the Voynich
  Manuscript” (2019):
  <https://agnosticvoynich.files.wordpress.com/2019/06/glyph-combinations-across-word-breaks-in-the-voynich-manuscript-preprint.pdf>

The paper reports non-independent glyph combinations across transcribed word
breaks, identifies `y.q` as a particularly strong combination, and notes that
Voynich `q` is regularly connected with following `o` and can be construed as
`qo`. It also cautions that such distributional structure supplies no
translation by itself.

## Frozen comparison

For every one of the 4,737 `confirmed_edges` in the frozen pre-grounding
interlinear, recover the left and right retained-node surfaces named by the
stored `Wn>Wm` coordinates. Count:

- the final character and final two characters of the left node;
- the initial character and initial two characters of the right node;
- literal `y|q`, `y|qo`, and `(dy|ey)|qo` overlap;
- the same quantities separately for each of the six retained role-edge
  classes and each alternate reading.

Use the independently validated source-separator impact artifact to distinguish
the 4,731 direct adjacent-source-group edges from the six edges that skip an
intervening source group. ZL3b, IT2a, and RF1b remain alternate readings of one
manuscript, not independent manuscripts.

## Interpretation rule

If at least 85% of direct edges are literal `y|q` and at least 90% enter
`qo...`, the aggregate hard-edge direction is reclassified as predominantly a
formal partition of the known public word-boundary pattern. The exact
source-separated occurrences remain valid, but they may not be advertised as
an independently discovered new syntax.

The six role classes still describe the frozen retained parser. They are
conditional on an unavailable, surface-incomplete parser and are not validated
as exhaustive grammar by this audit.

Claim ceiling: this audit can correct novelty and interpretation language. It
cannot establish authorial wordhood, syntax, a morpheme, sound, language,
cipher, meaning, plaintext, or translation.
