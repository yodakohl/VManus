# GDT193 — compiler-stripped consonantal skeleton screen

## Question

Could PAGE_HOST be a compressed language substrate that omits ordinary vowels,
rather than the literal or one/two-letter channels rejected by GDT189/192?

## Frozen model

- Use the identical non-f84 PAGE_HOST lines and line/SPACE structure as GDT189.
- For each of the six frozen language packs, delete `a/e/i/o/u` inside each
  training word, discard an empty skeleton, and preserve one SPACE between the
  surviving word skeletons.
- Train a Dirichlet-1/2 line-reset order-2 model over exactly the 21 retained
  consonants plus SPACE; deleted vowels are structural zeros, not smoothing
  cells.
- Map the 20 active source signs injectively to 20 of the 21 fixed consonantal
  target letters `bcdfghjklmnpqrstvwxyz`; one consonant is explicitly omitted.
- Pay `log2(P(21,20)) = log2(21!)`, the six-language selector, and the common
  model/order overhead.
- Run three deterministic exhaustive pair-swap descents, including swaps with
  the single omitted consonant, and require exact local optimality.
- Compare with the same matched anonymous order-2 KT source channel as GDT189.

The screen passes only with a negative paid gap and one identical mapping in
all starts. This is a mechanical consonant-deletion sensitivity, not a claim
that manuscript signs are phonemes. It does not test abjads with matres
lectionis, language-specific vowel classes, syllabograms, context-dependent
restoration, or page keys. Every `f84*` row is rejected before parsing.
