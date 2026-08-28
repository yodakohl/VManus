# GDT613 scratch bridge audit preregistration

This scratch audit is downstream only of the published GDT612 synthetic
calibration artifacts.  It never reads a target stream, target evaluation,
target key, Voynich page selector, or manuscript image.  In particular, it
does not read `f84` or `f84r` material.

## Frozen question

Does a pure fourth-order real-Latin generative character cross-entropy rank the
GDT612 planted key ahead of (a) all six archived synthetic fitted pseudokeys and
(b) every legal one-primitive output mutation available in the frozen GDT612
Latin role-specific candidate inventory, when the mutation keeps the truth
role, all overrides, and the output length fixed?

## Frozen objectives kept separate

The only key score is a smoothed real-Latin character-model log probability.
Two fit/score contracts are reported independently.  The legacy-compatible
contract fits one continuous reference stream and scores each decoded chunk
from one triple-boundary context, including internal word boundaries.  The
reset-matched contract uses the current GDT613 `fst.py` construction—three
start boundaries and one final boundary are inserted for every reference word
during fit—and scores every decoded word from a fresh triple-boundary context.
Their scores are never pooled or silently substituted for one another.

There is no destroyed-language model,
language-model subtraction, lexicon reward, grammar penalty, length penalty,
role prior, override prior, or codebook reward.  A terminal boundary is scored
for every chunk, including an empty decoded chunk.  The primary cross-entropy
denominator is every predicted symbol: letters plus internal/final word
boundaries.  Empirical event counts are the primary chunk weights; the frozen
GDT612 square-root weights are a sensitivity analysis.

## Declared mutation universe

For each non-null truth primitive, replace its output by each different value
in that primitive role's published `latin_real_candidates.tsv` category that:

1. has exactly the truth output length; and
2. is not already assigned to another truth primitive of the same role.

No role, override, merge, boundary behavior, or output length may change.  This
is exhaustive only within the decoder's published candidate inventory; it is
not an exhaustive search over arbitrary strings or multi-site keys.

## Language-model panels

Each fit/score contract uses all four declared panels.  The bridge panel uses
all published real-Latin reference tokens.  The exact prospective GDT613
reference cuts are independently derived from the GDT612 word list: tokens
0:8,209 are `LM_FIT_40` and 8,209:12,313 are `LM_CONFIRM_20`.  One model is fit
to each and intrinsically checked on the other.  A fourth model is fit only on the
published synthetic-held plaintext words, which are carrier-disjoint from the
synthetic train chunks.  These are independent splits of one reference source,
not independent historical corpora.

## Hard falsifiers

- Any fixed-length local mutation tying or beating truth in primary
  bits/predicted-symbol under any of the eight explicit contract x reference
  models falsifies the
  declared local bridge for that panel.
- Any archived fitted pseudokey tying or beating truth in primary
  bits/predicted-symbol falsifies seven-key discrimination for that panel.
- A local mutation changing weighted emitted-letter or boundary totals is an
  implementation failure.
- Either half-corpus model failing to beat the uniform 27-symbol baseline on
  its disjoint half makes that split non-informative.
- Any read outside the explicit input allow-list invalidates the audit.

Passing these gates establishes only a local objective bridge.  It does not
show global key identifiability, optimizer recovery, historical correctness, a
Voynich language, or a translation.
