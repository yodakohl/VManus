# GDT018 DY boundary-function report

Status: **DY INTERNAL TRANSITION NOT LOCAL RESET**

`DY` is not a miniature line reset.  Across 2344 held
post-DY boundaries, the cross-folio log-likelihood ratio of line-start versus
non-DY internal continuation is -349.097 bits; only
25/94 held folios favor line-start behavior.
The full-corpus Jensen-Shannon distance is 0.1033 bit between
post-DY and line-start distributions, compared with 0.0524 bit
between other internal continuations and line starts.

At the same time, DY is a strong transferable transition feature.  The
position-only held code uses 39872.320 bits.  Adding only
previous-DY status reduces this to 39422.513, a gain of
449.807 bits across 13121 internal boundaries and
80/94 positive held folios.  It captures
92.9% of the gain obtained by adding the complete
previous state to the position model.  The four-model-selector-paid gain is
447.807 bits.  Even a conservative 56-extra-
parameter BIC approximation leaves 66.778 net bits.

The most coherent functional reading is therefore **internal resolution
linker**: DY closes or resolves a local field while licensing a distinctive
continuation, but it does not restart the line's state machine.  This refines
the earlier HPR/PRS theory: physical newline is the true record reset; DY is
an embedded transition checkpoint.  “Resolution” and “linker” are provisional
functional mnemonics, not translations.

This result uses a post-selected lossy state projection and partly recovers
known `y | q` structure.  It does not identify what is resolved, and it does
not make DY a linguistic suffix.  f84r was absent from the sole input and was
not opened, retained, joined, or scored.  No morpheme, word, syntax, sound,
language, plaintext, meaning, or translation is confirmed.
