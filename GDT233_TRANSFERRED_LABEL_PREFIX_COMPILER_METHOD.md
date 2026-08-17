# GDT233 — transferred graphical-label prefix compiler

## Question

Can source-family prefixes learned outside q13 identify q13 graphical labels,
and can those prefixes be separated from the residual family before content
interpretation?

## Exposed exploratory design

This design and its scratch performance were inspected before publication; it
is a YOLO architecture analysis, not pristine confirmation.  Every f84 row is
rejected before source fields are parsed.

Training contains every non-q13, non-f84 first consensus group.  Candidate
prefixes have length 1–4, support at least 5, at least 4 label occurrences,
label rate at least .50, and one-sided hypergeometric `p <= .01` against the
training label rate.  The union of selected prefixes predicts q13 editorial
label kind.  Longest selected prefix is removed to expose a residual family;
this is a rendering decomposition, not a morphological segmentation.

`BACA-` is also reported as a fixed sensitivity because GDT231/GDT232 exposed
it before this test.  It must meet the same criteria except that its exact
training p-value is shown rather than promoted into the strict prefix set.

## Ceiling

Transferred label prediction supports a graphical register/compiler layer.
Neither a selected prefix nor a residual is an authorial label marker, word,
morpheme, object name, sound, language, plaintext, or translation.
