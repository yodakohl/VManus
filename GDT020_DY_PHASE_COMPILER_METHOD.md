# GDT020 DY-phase compiler

GDT020 tests whether terminal DY establishes a longer-lived within-line phase,
rather than influencing only the immediately following group.

The sole input is the frozen f84r-free GDT016 inventory.  Every group is
assigned `BEFORE_FIRST_DY` or `AFTER_FIRST_DY`; a separate flag marks the
immediately post-DY group.  Leave-one-physical-folio categorical prediction
compares normalized position alone with position plus the phase flag at 4, 8,
10, and 16 bins.  Dirichlet-1/2 smoothing and the 15-state alphabet are fixed.
An additional four-bin sensitivity removes all immediately post-DY groups.

Raw held codelength gains, positive-fold counts, a five-model selector, and a
BIC-style parameter penalty are reported.  More position bins are sensitivity
controls, not separate discovery wins.

Every line is then mechanically segmented after each DY group.  Complete
line/segment parses and recurrent run-collapsed segment templates are exported.
This is a formal compiler only.  Phase, checkpoint, and payload are mnemonic
labels, not linguistic or semantic assignments.

No transcription or image source is opened and no f84r row can enter.
Claim ceiling: provisional nested record-phase architecture; no morpheme,
sentence syntax, word, sound, language, plaintext, meaning, or translation.
