# DIC001 drawing-interruption one-shot target

Status: **PREREGISTERED; UNSCORED**.

## Question and fixed panel

Does the local family-edge shape across a unanimous manual drawing interruption
look more like a known continuation-line restart than the unanimous definite
spaces on the same page?  The target is exactly the masked DIC001 capacity panel:
428 drawing boundaries and 4,143 definite-space controls on 87 pages and 59
physical folios.  ZL3b, IT2a, and RF1b supply one consensus STA-family sequence,
not three samples.  No image or OCR feature is used.

## Fixed score

All 87 target pages are excluded from reference fitting.  For each target
physical folio, fit the validated categorical naive-Bayes shape instrument on
the remaining reference folios' ordinary spaces and genuine continuation-line
resets.  The six fields are left final family, right initial family, their pair,
left final two, right first two, and their two-by-two pair.  Center and divide
scores by the population SD of that fold's training ordinary-space scores.

The raw vector is then projected, without using boundary class, on: an
intercept; page fixed effects; normalized boundary position as a cubic and nine
decile indicators; capped group-count indicators; and indicators for every
observed capped `(left family length, right family length)` cell except the
lexicographically first baseline.  `numpy.linalg.lstsq(..., rcond=None)` defines
the projection.  Its residual is primary; raw standardized score must concur.

For each vector, compute drawing mean minus space mean within page, mean pages
within physical folio, and mean the 59 folios equally.  Currier and section
diagnostics use the same page-then-equal-folio rule within their subset.  A
folio's concentration is its absolute effect divided by the sum of absolute
folio effects.  Deletion recomputes the equal mean after removing one folio.

## Fixed null and gates

Use 65,536 deterministic uniform fixed-count assignments per page.  For page
`p`, seed PCG64 with the little-endian first eight SHA-256 bytes of
`"76001004|p"`; in each world choose the `k_p` smallest independent priorities,
where `k_p` is the observed drawing count.  The one-sided plus-one p-value is
`(1 + # null >= observed) / 65,537`.

Every gate is mandatory:

- raw and residual equal-folio effects are each at least 0.10 training-space SD;
- raw and residual permutation p-values are each at most .01;
- at least 39 of 59 residual folio effects are positive;
- residual Currier A, Currier B, Herbal, and non-Herbal effects are each at
  least 0.10;
- every leave-one-folio residual effect is positive;
- maximum absolute residual folio concentration is at most .15.

No threshold, covariate, page, folio, subgroup, or score can change after the
freeze.  The target runs once, followed by one nonimporting reconstruction.

## Decision and claim ceiling

All gates passing gives `CONFIRMED_DISTRIBUTED_RESET_LIKENESS`: text groups on
opposite sides of drawings have a distributed local edge shape more like known
continuation restarts than same-page ordinary spaces, beyond the frozen nuisance
projection.  A failed gate gives `FINAL_NONCONFIRMATION`: the fixed reset-like
contrast is not established; this is not proof that text continues through a
drawing.  Neither outcome establishes that adjacent text names or describes the
drawing, nor any word boundary, word, sound, POS, meaning, plaintext, language,
cipher, or translation.
