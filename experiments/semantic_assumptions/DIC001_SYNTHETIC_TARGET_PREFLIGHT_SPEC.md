# DIC001 synthetic target preflight

Status: **TARGET-IDENTITY-BLIND DEVELOPMENT FREEZE**.

The one-shot target will compare drawing interruptions with unanimous definite
spaces on the same 87 pages.  For each page it computes mean target minus mean
control reset-likeness; pages are averaged within physical folio and the 59
folios are then equally weighted.  The reference classifier is the already
validated leave-physical-folio-out six-field STA-family edge instrument, fitted
only outside all target pages.  Its score is centered and scaled on its training
ordinary spaces.

The primary score is additionally residualized, without boundary-class labels,
against page fixed effects, normalized boundary position (cubic plus deciles),
capped group count, and capped left/right neighboring-group lengths.  The raw
score is a required concordant control.  Thus the estimand is shape-based reset
likeness beyond those nuisance fields, not merely a tendency for drawings to
occur at a certain position or beside short groups.

The fixed target gates are: raw and residual equal-folio effects at least 0.10
training-space SD; one-sided 65,536-world within-page fixed-count permutation
`p <= .01` for each; at least 39/59 positive residual folios; residual effects
of at least 0.10 in each of Currier A and B and separately in Herbal-section
versus non-Herbal pages; every leave-one-folio deletion positive; and maximum absolute folio
concentration at most .15.  All permutations move whole boundary labels within
page and preserve each page's exact target count.

Before target access, the same aggregator, nuisance projection, diagnostics and
gates must pass an 8,192-world synthetic suite on the masked 4,571-row topology:
zero of 64 null worlds may pass; at least 6/8 distributed worlds must pass at
effect 0.50 and 8/8 at 0.75; and all eight worlds in each one-folio, one-section,
page-only, position-only, length-only, and reversed-signal family must fail.
Synthetic lengths are deterministic nuisance coordinates, not manuscript
measurements.  This suite tests the decision machinery and confound rejection;
it supplies no target observation.

A target pass would establish only that groups separated by drawings have a
distributed local edge shape more like known continuation-line restarts than
same-page ordinary spaces.  A target failure would reject that fixed reset-like
contrast, not prove grammatical continuity.  Neither outcome establishes
object ownership, word boundaries, words, sounds, POS, meaning, plaintext,
language, cipher, or translation.
