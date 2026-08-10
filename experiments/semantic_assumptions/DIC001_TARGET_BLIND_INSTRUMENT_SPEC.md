# DIC001 target-blind continuity instrument

Status: **DEVELOPMENT FREEZE; DRAWING TARGET EXCLUDED**.

All pages containing a unanimous drawing interruption are excluded.  On the
remaining strict confirmed-prose pages, the reference classes are unanimous
ordinary within-line spaces and genuine continuation-line resets: consecutive
numeric loci on one page where the latter has IVTFF `+P...` status.

The fixed structural model is leave-physical-folio-out categorical naive
Bayes with Laplace smoothing.  It uses six local STA-family-shape fields only:
left final family, right initial family, their ordered pair, left final two,
right initial two, and the ordered two-by-two edge.  A separate three-field
group-length model is a nuisance control.  No complete form, root, legacy
role, page position, drawing identity, OCR, or image feature is used.

Aggregate page AUC first within folio and then equally over folios.  The
instrument passes only with at least 1,000 resets and 60 folios, shape AUC at
least .75, shape-minus-length AUC at least .15, at least 90% positive folios,
both Currier A/B AUC at least .70, and a 64-world within-page held-label
permutation p at most 1/65.  These thresholds were fixed after a disclosed
development smoke and before any drawing-boundary family identity or score.

A pass licenses an independent reconstruction and then a separately frozen
one-shot target.  It establishes only that a reset-likeness instrument works
on known reference boundaries, not how drawing interruptions behave and not a
word, sound, POS, meaning, plaintext, language, cipher, or translation.
