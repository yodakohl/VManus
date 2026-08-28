# GDT607 method

## Inputs

The experiment consumes the published, f84-free GDT606 artifacts: 4,165
guarded lines on 91 physical folios, the unchanged 68-train/23-held split,
30,174 hard chunks, and 98 train-only BPE units. Certain separators and
drawing interruptions remain hard boundaries; uncertain separators remain
joined. No new page, image, or transcription selector is opened.

## Arm A: distributional role attack

All 65,014 unit events are reconstructed with chunk, physical-line,
paragraph, local-neighbour, section, hand, and folio context. The five GDT606
`W` targets (`o`, `y`, `ol`, `C`, `d`) are compared with frequency-matched
non-target controls. A train-only categorical classifier predicts target
identity on held folios; a 200-draw conditional permutation keeps section,
hand, and chunk-position strata while destroying residual identity context.
Literal one-unit hard chunks provide a direct counterclass to the `W` label.

## Arm B: explicit boundary capacity

The GDT606 mixed-codebook solver is extended with `B`, an outputless category
that flushes the current decoded buffer. Five fixed-capacity grids exchange
zero, three, six, eight, or eleven of the eleven `W` slots for `B` slots while
holding letter, double, syllable, and null capacity fixed. Six deterministic
starts for each Latin, Old Italian, and Middle High German reference produce
90 complete 98-unit keys. The test records whether the five targets move to
`B`, remain output-bearing, or enter another class.

## Interpretation ceiling

The experiment can correct a decoder-category confound and assign transferable
formal positional roles. It cannot identify a word, morpheme, sound,
language, ingredient, action, or plaintext meaning.
