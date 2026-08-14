# GDT019 DY-payload continuation test

GDT019 asks whether the content carried inside a DY-closed group selects the
next formal state.  It reads only the frozen, f84r-free GDT016 state inventory.

The 2,344 internal boundaries whose previous group is `DY_RESOLUTION` are
scored with leave-one-physical-folio-out categorical predictors.  The baseline
uses the next group's normalized line-position quartile.  Nine additions are
tested: previous recovered q flag, complete prefix class, candidate-core flag,
candidate-core class, host-length flag, host-length bin, first family symbol,
exact family, and exact residual host.

The targets are the complete 14-way next state plus four binary transitions:
next Q, next OT-local, next DY, and next carrier.  Dirichlet-1/2 smoothing and
the global target alphabet are fixed.  Raw held-bit gain is reported together
with a per-model BIC approximation based on the observed number of feature
levels and a ten-model selector cost.  These penalties rank leads; they do not
turn the exploratory screen into confirmation.

No transcription source is opened.  No f84r row can enter the experiment.
Claim ceiling: low-capacity decoupling of checkpoint payload and following
formal state; no morpheme, syntax, word, sound, language, plaintext, meaning,
or translation.
